from rest_framework import serializers
from .models import ResumeAnalysis

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = ['id', 'resume', 'job_description', 'rating', 'suggestions', 'created_at', 'updated_at']
        read_only_fields = ['rating', 'suggestions', 'created_at', 'updated_at'] 