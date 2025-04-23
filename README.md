# Resume Analyzer

A modern web application that analyzes resumes against job descriptions using AI. The application provides a rating and suggestions for improvement.

## Features

- Upload PDF resumes and job descriptions
- Extract text from PDFs using PyPDF2
- Analyze content using Google's Gemini AI
- Dynamic rating display with color-coded feedback
- Detailed suggestions for improvement
- Modern, responsive UI using Bootstrap

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  
# On Windows: Set-ExecutionPolicy Unrestricted
#             -Scope Process.\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

6. Visit http://localhost:8000 in your browser.

## Usage

1. Upload your resume (PDF format)
2. Upload the job description (PDF format)
3. Click "Analyze" to process the documents
4. View your rating and suggestions for improvement

## Requirements

- Python 3.8+
- Django 4.2+
- Django REST Framework
- PyPDF2
- Google Generative AI
- python-dotenv

## Note

Make sure to keep your Gemini API key secure and never commit it to version control. 
