from django.db import models

# Create your models here.
class Greeting(models.Model):
    when = models.DateTimeField('date created', auto_now_add=True)

#NEW

class Certs(models.Model):

   name = models.CharField(max_length = 50)
   prereqs = models.CharField(max_length = 50)

   class Meta:
      db_table = "certs"
