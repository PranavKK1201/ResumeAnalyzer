from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
import PyPDF2
import os
from dotenv import load_dotenv
import traceback
import json
import requests
from datetime import datetime
import re
import hashlib
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
import markdown

load_dotenv()

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)  # Print to console
    
    # Also log to a file
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f'resume_analyzer_{datetime.now().strftime("%Y%m%d")}.log')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')

def get_gemini_response(prompt):
    try:
        log_message("Starting Gemini API call...")
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-001:generateContent?key={api_key}"
        
        # Prepare the request payload
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        log_message("Sending request to Gemini API...")
        # Send the request
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            log_message("Successfully received response from Gemini API")
            reply = response.json()
            
            # Log the full response for debugging
            log_message(f"Full Gemini response: {json.dumps(reply, indent=2)}")
            
            # Extract text response with better error handling
            try:
                text_response = reply.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if not text_response:
                    log_message("Warning: Empty text response from Gemini API")
                    raise ValueError("Empty response from Gemini API")
                return text_response
            except Exception as e:
                log_message(f"Error extracting text from Gemini response: {str(e)}")
                log_message(f"Response structure: {json.dumps(reply, indent=2)}")
                raise
        else:
            error_msg = f"Gemini API error: Status {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f" - {json.dumps(error_details)}"
            except:
                error_msg += f" - {response.text}"
            log_message(error_msg)
            raise ValueError(error_msg)

    except Exception as e:
        log_message(f"Error with Gemini API: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())
        raise

def index(request):
    # Redirect to landing page
    return redirect('landing_page')

def landing_page(request):
    return render(request, 'analyzer/landing.html')

def results_page(request):
    # Get the analysis text from session
    analysis_text = request.session.get('analysis_text', '')
    
    if not analysis_text:
        return redirect('landing_page')
    
    # Convert markdown to HTML
    html_content = markdown.markdown(analysis_text, extensions=['extra'])
    
    # Extract scores from the analysis text
    relevance_match = re.search(r'Relevance Score:\s*(\d+)/10', analysis_text)
    ats_match = re.search(r'ATS Compatibility:\s*(\d+)/10', analysis_text)
    readability_match = re.search(r'Readability & Clarity:\s*(\d+)/10', analysis_text)
    
    # Get scores or default to 0 if not found
    relevance_score = int(relevance_match.group(1)) if relevance_match else 0
    ats_score = int(ats_match.group(1)) if ats_match else 0
    readability_score = int(readability_match.group(1)) if readability_match else 0
        
    return render(request, 'analyzer/results.html', {
        'analysis_text': html_content,
        'relevance_score': relevance_score,
        'ats_score': ats_score,
        'readability_score': readability_score
    })

def extract_text_from_pdf(pdf_file):
    try:
        log_message(f"Starting PDF text extraction for file: {pdf_file.name}")
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        total_pages = len(pdf_reader.pages)
        log_message(f"PDF has {total_pages} pages")
        
        for i, page in enumerate(pdf_reader.pages, 1):
            log_message(f"Extracting text from page {i}/{total_pages}")
            text += page.extract_text()
        
        return text
    except Exception as e:
        log_message(f"Error extracting text from PDF: {str(e)}")
        raise

class ResumeAnalysisView(APIView):
    def post(self, request):
        print("\n=== Starting Resume Analysis Process ===")
        try:
            print("1. Initial request received")
            print(f"Request method: {request.method}")
            print(f"Request FILES: {request.FILES}")
            print(f"Request POST: {request.POST}")
            
            # Handle resume file
            resume_file = request.FILES.get('resume')
            if not resume_file:
                print("ERROR: No resume file provided")
                return Response({'error': 'No resume file provided'}, status=status.HTTP_400_BAD_REQUEST)
                
            print(f"2. Resume file received: {resume_file.name}, size: {resume_file.size}")
            
            # Handle job description file
            jd_file = request.FILES.get('job_description')
            if not jd_file:
                print("ERROR: No job description file provided")
                return Response({'error': 'No job description file provided'}, status=status.HTTP_400_BAD_REQUEST)
                
            print(f"3. Job description file received: {jd_file.name}, size: {jd_file.size}")

            # Reset file pointers to the beginning
            resume_file.seek(0)
            jd_file.seek(0)

            try:
                print("6. Starting text extraction from PDFs...")
                resume_text = extract_text_from_pdf(resume_file)
                print("Resume text extracted successfully")
                jd_text = extract_text_from_pdf(jd_file)
                print("Job description text extracted successfully")
            except Exception as e:
                print(f"ERROR extracting text: {str(e)}")
                return Response({'error': 'Error extracting text from files. Please ensure files are valid PDFs.'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            print("7. Preparing prompt for Gemini...")
            # Prepare the prompt for Gemini
            prompt = f"""You are a resume analyzer. Analyze the provided resume against the job description and provide a detailed assessment.

IMPORTANT: You MUST follow this EXACT format for your response. Do not add any additional text or explanations before or after these sections.

SCORES (must be whole numbers between 0-10):
Relevance Score: X/10
ATS Compatibility: Y/10
Readability & Clarity: Z/10

ANALYSIS:
## Overall Assessment
[Your assessment here]

## Strengths
[Your strengths analysis here]

## Areas for Improvement
[Your improvement suggestions here]

## Detailed Analysis
[Your detailed analysis here]

## Action Items
[Your action items here]

CRITICAL FORMATTING RULES:
1. Scores MUST be on separate lines starting with exactly "Relevance Score:", "ATS Compatibility:", and "Readability & Clarity:"
2. Each score MUST be followed by "/10" (e.g., "Relevance Score: 8/10")
3. Scores MUST be whole numbers between 0 and 10
4. Section headers MUST start with exactly "## " followed by the section name
5. Do not add any text before the scores or after the action items
6. Do not add any additional sections or formatting

Resume:
{resume_text}

Job Description:
{jd_text}"""

            print("8. Sending request to Gemini API...")
            # Get response from Gemini
            response_text = get_gemini_response(prompt)
            print("9. Received response from Gemini API")
            print("Response text preview:", response_text[:200] + "...")
            
            # Store the analysis text in the session
            request.session['analysis_text'] = response_text
            
            # Return success response
            return Response({'status': 'success'})

        except Exception as e:
            print(f"ERROR in analyze method: {str(e)}")
            print("Traceback:")
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

