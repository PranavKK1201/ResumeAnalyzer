from django.urls import path
from .views import ResumeAnalysisView, index, landing_page, results_page

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('api/analyze/', ResumeAnalysisView.as_view(), name='analyze'),
    path('results/', results_page, name='results_page'),
] 