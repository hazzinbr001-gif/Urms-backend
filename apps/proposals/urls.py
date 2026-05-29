from django.urls import path
from .views import ProposalCreateView, ProposalListView, ProposalDetailView, ProposalTransitionView

urlpatterns = [
    path('', ProposalListView.as_view(), name='proposal_list'),
    path('new/', ProposalCreateView.as_view(), name='create_proposal'),
    path('<uuid:pk>/', ProposalDetailView.as_view(), name='proposal_detail'),
    path('<uuid:pk>/transition/', ProposalTransitionView.as_view(), name='proposal_transition'),
]
