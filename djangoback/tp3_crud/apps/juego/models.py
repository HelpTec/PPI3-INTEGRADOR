from django.db import models

class Juego(models.Model):
    Rank = models.IntegerField(max_length=10)
    Name = models.CharField(max_length=100)
    Platform = models.CharField(max_length=50)
    Year = models.DateField()
    Genre = models.CharField(max_length=100)
    Publisher = models.CharField(max_length=100)
    NA_Sales = models.FloatField(max_length=100)
    EU_Sales = models.FloatField(max_length=100)
    JP_Sales = models.FloatField(max_length=100)
    Other_Sales = models.FloatField(max_length=100)
    Global_Sales = models.FloatField(max_length=100)
    