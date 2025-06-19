from django.db import models

class Juego(models.Model):
    Rank = models.IntegerField(null=True, blank= True)
    Name = models.CharField(max_length=100, null=True, blank= True)
    Platform = models.CharField(max_length=50, null=True, blank= True)
    Year = models.IntegerField(null=True, blank= True)
    Genre = models.CharField(max_length=100, null=True, blank= True)
    Publisher = models.CharField(max_length=100, null=True, blank= True)
    NA_Sales = models.FloatField(max_length=100, null=True, blank= True)
    EU_Sales = models.FloatField(max_length=100, null=True, blank= True)
    JP_Sales = models.FloatField(max_length=100, null=True, blank= True)
    Other_Sales = models.FloatField(max_length=100, null=True, blank= True)
    Global_Sales = models.FloatField(max_length=100, null=True, blank= True)
    API_ID = models.CharField(max_length=100, unique=True, null=True, blank=True)
    Image_URL = models.URLField(max_length=500, null=True, blank=True)
