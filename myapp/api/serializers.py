from rest_framework import serializers
from myapp.models import Monument, Submission

class MonumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monument
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'
