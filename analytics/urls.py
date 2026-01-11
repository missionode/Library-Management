from django.urls import path
from . import views, chatbot

urlpatterns = [
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('reports/', views.ReportBuilderView.as_view(), name='report_builder'),
    path('chatbot/api/', chatbot.chatbot_api, name='chatbot_api'),
]
