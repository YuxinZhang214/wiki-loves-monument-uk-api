from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.shortcuts import get_list_or_404

from myapp.models import Submission
from myapp.api.serializers import SubmissionSerializer

from collections import defaultdict

excluded_years = [2015, 2021, 2024]

class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

class SubmissionDailyView(APIView):
    def get(self, request, format=None):
        formatted_data = defaultdict(lambda: defaultdict(int))
        submissions = Submission.objects.exclude(year__in=excluded_years).values('year', 'date').annotate(total=Count('id')).order_by('year', 'date')

        for submission in submissions:
            year = submission['year']
            date = submission['date']
            formatted_data[year][date] = submission['total']

        return Response(dict(formatted_data))

class SubmissionYearlyView(APIView):
    def get(self, request, format=None):
        years = Submission.objects.exclude(year__in=excluded_years).values('year').distinct().order_by('year')
        formatted_data = {}

        for year_entry in years:
            year = year_entry['year']
            # Count submissions for each year, excluding the specified years
            submission_count = Submission.objects.filter(year=year).count()
            formatted_data[str(year)] = submission_count

        return Response(formatted_data)
    
class SubmissionYearlyAuthorView(APIView):
    def get(self, request, authorname, format=None):
        # Assuming `excluded_years` is defined somewhere in your code

        # Retrieve years with submissions by the specified author, excluding specified years
        years = Submission.objects.filter(image_author=authorname) \
                                  .exclude(year__in=excluded_years) \
                                  .values('year') \
                                  .distinct() \
                                  .order_by('year')

        formatted_data = {}

        for year_entry in years:
            year = year_entry['year']
            # Count submissions for this author in the specific year, excluding specified years
            submission_count = Submission.objects.filter(image_author=authorname, year=year) \
                                                 .exclude(year__in=excluded_years) \
                                                 .count()
            formatted_data[str(year)] = submission_count

        return Response(formatted_data)

class SubmissionYearlyTotalView(APIView):
    def get(self, request, format=None):

        years = Submission.objects.exclude(year__in=excluded_years).values('year').annotate(total=Count('id')).order_by('year')
        formatted_data = {}
        cumulative_total = 0

        for year_entry in years:
            year = year_entry['year']
            cumulative_total += year_entry['total']
            formatted_data[str(year)] = cumulative_total

        return Response(formatted_data)
    
class SubmissionYearlyTotalAuthorView(APIView):
    def get(self, request, authorname, format=None):
        # Define `excluded_years` if not defined globally
        excluded_years = [2015, 2021]  # Example: excluding the years 2021 and 2022
        
        # Filter Submission objects by authorname and exclude specified years
        years = Submission.objects.filter(image_author=authorname) \
                                  .exclude(year__in=excluded_years) \
                                  .values('year') \
                                  .annotate(total=Count('id')) \
                                  .order_by('year')
        
        formatted_data = {}
        cumulative_total = 0

        # Calculate cumulative total
        for year_entry in years:
            year = year_entry['year']
            cumulative_total += year_entry['total']
            formatted_data[str(year)] = cumulative_total

        return Response(formatted_data)
    
class SubmissionImageView(APIView):
    def get(self, request, format=None):
        submissions = Submission.objects.all().values('label', 'image_url','image_author','year','date')
        formatted_data = list(submissions) 
        return Response(formatted_data)
    
class SubmissionDetailView(APIView):
    def get(self, request, label, format=None):
        if label is not None:
            submissions = get_list_or_404(Submission, label=label)
            serializer = SubmissionSerializer(submissions, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Label parameter is required."}, status=status.HTTP_400_BAD_REQUEST)