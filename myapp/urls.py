from django.urls import path
from myapp.views import (
    ParticipantView,
    ParticipantSubmissionView,
    ParticipantDetailView,
    MonumentViewSet,
    MonumentLocationView,
    MonumentHeritageDestinationView,
    MonumentInceptionsView,
    MonumentImageView,
    MonumentDetailView,
    SubmissionDailyView,
    SubmissionYearlyView,  
    SubmissionYearlyAuthorView,   
    SubmissionYearlyTotalView,  
    SubmissionYearlyTotalAuthorView,
    SubmissionImageView,
    SubmissionDetailView,
    CompetitionStatisticsView     
)

urlpatterns = [
    # Existing paths for monuments
    path('monuments/', MonumentViewSet.as_view({'get': 'list'}), name='monument-all'),
    path('monuments/locations', MonumentLocationView.as_view(), name='monuments-location'),
    path('monuments/destinations', MonumentHeritageDestinationView.as_view(), name='monuments-heritage-destination'),
    path('monuments/inceptions', MonumentInceptionsView.as_view(), name='monuments-yearly'),
    path('monuments/images', MonumentImageView.as_view(), name='monuments-images'),
    path('monuments/<str:label>', MonumentDetailView.as_view(), name='monuments-detail'),
    
    # Paths for authors and author details
    path('participants/', ParticipantView.as_view(), name='participant-all'),
    path('participants/submissions', ParticipantSubmissionView.as_view(), name='participant-submission'),
    path('participants/<str:authorname>/', ParticipantDetailView.as_view(), name='participant-detail'),

    # Add a path for submission-specific data
    path('submissions/', SubmissionYearlyView.as_view(), name='submissions-all'),
    path('submissions/daily', SubmissionDailyView.as_view(), name='submissions-daily'),
    path('submissions/yearly', SubmissionYearlyView.as_view(), name='submissions-yearly'),
    path('submissions/yearly/total', SubmissionYearlyTotalView.as_view(), name='submissions-yearly-total'),
    path('submissions/yearly/<str:authorname>', SubmissionYearlyAuthorView.as_view(), name='submissions-yearly-author'),
    path('submissions/yearly/total/<str:authorname>/', SubmissionYearlyTotalAuthorView.as_view(), name='submissions-total-author'),
    path('submissions/images', SubmissionImageView.as_view(), name='submissions-images'),
    path('submissions/<str:label>', SubmissionDetailView.as_view(), name='submissions-detail'),

    # Path for combined competition statistics
    path('competition/statistics/', CompetitionStatisticsView.as_view(), name='competition-statistics'),
]