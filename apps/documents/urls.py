from django.urls import path
from .views import DocumentTrackingView, DocumentUploadView, DocumentReviewView

app_name = 'documents'

urlpatterns = [
    path('proposal/<uuid:proposal_id>/tracking/', DocumentTrackingView.as_view(), name='tracking'),
    path('proposal/<uuid:proposal_id>/section/<uuid:section_id>/upload/', DocumentUploadView.as_view(), name='upload'),
    path('submission/<uuid:pk>/review/', DocumentReviewView.as_view(), name='review'),
]
