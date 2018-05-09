from django.db import models

# Create your models here.
# class Greeting(models.Model):
#     when = models.DateTimeField('date created', auto_now_add=True)

#NEW

# class Certs(models.Model):

#    name = models.CharField(max_length = 50)
#    prereqs = models.CharField(max_length = 50)

#    class Meta:
#       db_table = "certs"

class Certificates(models.Model):

   title = models.CharField(max_length=100, primary_key=True)
   code = models.CharField(max_length=5)
   link_page = models.URLField()
   contact_name=models.CharField(max_length=255)
   contact_email=models.EmailField()
   total_courses=models.IntegerField()
   description=models.CharField(max_length=10000)
   tracks=models.CharField(default='', max_length=1000000)
   # track2=models.CharField(max_length=1000)
   # track3=models.CharField(max_length=1000)
   # track4=models.CharField(max_length=1000)
   # track5=models.CharField(max_length=1000)
   # track6=models.CharField(max_length=1000)
   class Meta:
   	db_table = "certificates"

class Students(models.Model):
    netid = models.CharField(max_length=100, primary_key=True)
    major = models.CharField(max_length=100, default='')
    degree = models.CharField(max_length=100, default='')
    year = models.IntegerField(null=True)
    certsObtained = models.CharField(max_length=1000000, default='')
    numCoursesCompleted = models.IntegerField(null=True)
    certificateObtainable = models.IntegerField(null=True)
    coursesNeeded = models.IntegerField(null=True)
    courseBasket = models.CharField(max_length=1000000, default='')
    coursesCompleted = models.CharField(max_length=1000000, default='')
    pinnedCertificates = models.CharField(max_length=1000000, default='')
    class Meta:
        db_table = "students"


class Metadata(models.Model):

   title = models.CharField(max_length=100, primary_key=True)
   code = models.CharField(max_length=5)
   number_of_students = models.IntegerField(null=True)
   trend = models.IntegerField(null=True)
   class Meta:
        db_table = "metadata"