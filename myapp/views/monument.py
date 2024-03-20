from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.db.models import F

from django.http import JsonResponse
from collections import OrderedDict, defaultdict

from myapp.models import Monument
from myapp.api.serializers import MonumentSerializer
from myapp.models import Monument

class MonumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Monument.objects.all()
    serializer_class = MonumentSerializer 

class MonumentLocationView(APIView):
    def get(self, request, format=None):
        '''
        Monuments containing all lat/long.
        '''
        monuments = Monument.objects.values('latitude', 'longitude').distinct()

        formatted_data = []
        for monument in monuments:
            formatted_data.append({
                'lat': monument['latitude'],
                'long': monument['longitude']
            })

        return Response(formatted_data) 

class MonumentHeritageDestinationView(APIView):
    def get(self, request, format=None):
        '''
        Monuments count by heritage designation
        '''
        monuments = Monument.objects.values('heritage_designation').annotate(total=Count('heritage_designation')).order_by()

        # Convert QuerySet to a dictionary with heritage_designation as key and count as value
        counts = {monument['heritage_designation']: monument['total'] for monument in monuments}

        return Response(counts)

class MonumentInceptionsView(APIView):
    def get(self, request, format=None):
        '''
        Monuments grouped by inception (year),
        containing image label, image URL.
        '''
        monuments = Monument.objects.exclude(inception__isnull=True).annotate(
            inception_year=ExtractYear('inception')
        ).values('inception_year', 'label', 'image_url').order_by('inception_year')

        formatted_data = defaultdict(list)
        for monument in monuments:
            year = monument['inception_year']
            formatted_data[year].append({
                'label': monument['label'],
                'image_url': monument['image_url']
            })

        return Response(dict(formatted_data))
    
class MonumentImageView(APIView):
    def get(self, request, format=None):
        monuments = Monument.objects.values('label', 'image_url','image_author','instance_of_type_label','inception','admin_entity_label','historic_county_label','heritage_designation')
        formatted_data = list(monuments)
        return Response(formatted_data)
    
class MonumentDetailView(APIView):
    def get(self, request, label, format=None):
        monuments = Monument.objects.filter(label=label) if label else Monument.objects.all()

        formatted_data = [
            {
                'label': monument.label,
                'image_url': monument.image_url,
                'image_author': monument.image_author,
                'year': monument.year,
                'date': monument.date,
                'instance_of_type_label': monument.instance_of_type_label,
                'longitude': monument.longitude,
                'latitude': monument.latitude,
                'country': monument.country,
                'inception': monument.inception,
                'admin_entity_label': monument.admin_entity_label,
                'historic_county_label': monument.historic_county_label,
                'heritage_designation': monument.heritage_designation
            } for monument in monuments
        ]
        

        # Return an array of monuments. It could be one monument, multiple, or none.
        return Response(formatted_data)