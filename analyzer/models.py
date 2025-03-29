from django.db import models

# Create your models here.

class ResumeAnalysis(models.Model):
    resume_file = models.FileField(upload_to='resumes/')
    job_description_file = models.FileField(upload_to='job_descriptions/')
    analysis = models.TextField()
    relevance_score = models.IntegerField()
    ats_score = models.IntegerField()
    readability_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis {self.id} - {self.created_at}"
