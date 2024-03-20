from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from collections import OrderedDict, defaultdict

from myapp.models import Monument, Submission

class ParticipantView(APIView):
     def get(self, request, *args, **kwargs):
        authors = Submission.objects.values_list('image_author', flat=True).distinct().order_by('image_author')
        authors_list = list(authors)
        return Response(authors_list)

class ParticipantSubmissionView(APIView):
    def get(self, request, *args, **kwargs):
        authors = Submission.objects.values('image_author').annotate(total_submissions=Count('id')).order_by('-total_submissions')
        return Response(authors)
    
class ParticipantDetailView(APIView):
    def get(self, request, authorname):
        # Filter by author for both models
        monuments_by_author = Monument.objects.filter(image_author=authorname)
        submissions_by_author = Submission.objects.filter(image_author=authorname)

        heritage_designations_counts = monuments_by_author.values('heritage_designation').annotate(total=Count('heritage_designation')).order_by('heritage_designation')
        instance_types_counts = monuments_by_author.values('instance_of_type_label').annotate(total=Count('instance_of_type_label')).order_by('instance_of_type_label')

        # Initialize aggregated_data to ensure correct data structure
        aggregated_data = {
            'heritage_designations_counts': list(heritage_designations_counts),
            'instance_types_counts': list(instance_types_counts),
            'monuments': [],
            'submissions': [],
        }

        # Process monuments
        for monument in monuments_by_author:
            aggregated_data['monuments'].append({
                'label': monument.label,
                'image_url': monument.image_url,
                'year': monument.year,
                'date': monument.date,
                'instance_of_type_label': monument.instance_of_type_label,
                'longitude': monument.longitude,
                'latitude': monument.latitude,
                'country': monument.country,
                'inception': monument.inception,
                'admin_entity_label': monument.admin_entity_label,
                'historic_county_label': monument.historic_county_label,
                'heritage_designation': monument.heritage_designation,
            })

        # Process submissions
        for submission in submissions_by_author:
            aggregated_data['submissions'].append({
                'label': submission.label,
                'image_url': submission.image_url,
                'year': submission.year,
                'date': submission.date,
                'longitude': submission.longitude,
                'latitude': submission.latitude,
                'country': submission.country,
            })

        return Response(aggregated_data)