from django.db import models

class Monument(models.Model):
    label = models.CharField(max_length=255)

    image_url = models.URLField(max_length=1024, blank=True)
    image_author = models.CharField(max_length=255, blank=True)

    year = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)

    instance_of_type_label = models.CharField(max_length=255, blank=True)

    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)

    inception = models.DateField(blank=True, null=True)

    admin_entity_label = models.CharField(max_length=255, blank=True)
    historic_county_label = models.CharField(max_length=255, blank=True)

    heritage_designation = models.CharField(max_length=255)

class Submission(models.Model):
    label = models.CharField(max_length=255)

    image_url = models.URLField(max_length=1024, blank=True)
    image_author = models.CharField(max_length=255, blank=True)

    year = models.IntegerField(null=True, blank=True)
    date = models.IntegerField(null=True, blank=True)

    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)