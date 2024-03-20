from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from myapp.models import Submission, Monument

class CompetitionStatisticsView(APIView):
    def get(self, request, format=None):
        # Count total submissions and monuments
        total_submissions = Submission.objects.count()
        total_monuments = Monument.objects.count()
        heritage_designation = Monument.objects.values('heritage_designation').distinct().count()

        year_submissions_count = Submission.objects.exclude(year__in=[2015, 2021, 2024]).values('year').distinct().count()
        country_submissions_count = Submission.objects.values('country').distinct().count()
        participants_submissions_count = Submission.objects.values('image_author').distinct().count()

        instance_type_monuments_count = Monument.objects.values('instance_of_type_label').distinct().count()

        # Combine the statistics into a single response object
        response_data = {
            'submissions': total_submissions,
            'monuments': total_monuments,
            'years': year_submissions_count,
            'country': country_submissions_count,
            'participants': participants_submissions_count,
            'heritage_instances': instance_type_monuments_count,
            'heritage_designation': heritage_designation
        }

        return Response(response_data)