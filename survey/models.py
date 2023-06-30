from django.db import models
from django.contrib.auth.models import User
from jsonfield import JSONField
import collections

# Create your models here.

QUESTION_TYPE_CHOICES = [
    (0, 'Yes-No'),
    (1, 'Text'),
]

class Questions(models.Model):
    question = models.CharField(max_length=500, null = True, blank = True)
    # options = models.CharField(max_length=500, null = True, blank = True)
    options = JSONField()
    # type = models.SmallIntegerField(choices = QUESTION_TYPE_CHOICES, null = True, blank = True)
    class Meta:  
        db_table = "questions"
    
    def __str__(self):
        return str(self.question)

class DailySurvey(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    survey = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict})
    survey_rating = models.SmallIntegerField(null = True, blank = True)
    date = models.DateField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True, null = True, blank = True)
    updated = models.DateTimeField(auto_now=True, null = True, blank = True)
    class Meta:  
        db_table = "daily_survey"
    
    def __str__(self):
        return str(self.user)

class SurveyRating(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.DateField(null=True,blank=True)
    rating = models.SmallIntegerField(null = True, blank = True)
    class Meta: 
        db_table = "survey_rating"

    def __str__(self):
        return str(self.user)