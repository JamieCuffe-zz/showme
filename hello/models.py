from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)
    
#NEW
class Certificates(models.Model):
	name = models.CharField(max_length=255)
	prereqs = models.CharField(max_length=255)
	deparmentHead = models.CharField(max_length=255)
	class Meta:
      db_table = "certificates"