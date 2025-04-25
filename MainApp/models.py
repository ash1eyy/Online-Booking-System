from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class Resource(models.Model):
    resourceName = models.CharField(max_length=100)
    uploadedBy = models.CharField(max_length=20)
    resourceType = models.CharField(max_length=20)
    resourceDesc = models.CharField(max_length=20)
    resourceImage = models.ImageField(upload_to="resource_images/", null=True)
    uploadDate = models.DateField()
    
class LeasingRequest(models.Model):
    resourceLeased = models.ForeignKey(Resource, on_delete=models.CASCADE)
    leasedBy = models.CharField(max_length=20)
    startDate = models.DateField()
    endDate = models.DateField()
    requestDate = models.DateField()
    requestDesc = models.CharField(max_length=1000)
    requestStatus = models.BooleanField(null=True)
    amountPaid = models.PositiveBigIntegerField()
    
    class Meta:
        verbose_name = "Leasing Request"
    
class Report(models.Model):
    reportedBy = models.CharField(max_length=20)
    reportTitle = models.CharField(max_length=100)
    reportDate = models.DateField()
    affectedResource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    incidentDate = models.DateField()
    reportDesc = models.CharField(max_length=1000)

class Tenant(models.Model):
    unitNumber = models.CharField(max_length=7)
    reports = models.ManyToManyField(Report)
    leasingRequests = models.ManyToManyField(LeasingRequest)
    
    def class_name(self):
        return "Tenant"
    
    class Meta:
        verbose_name = "Tenant"
    
class Owner(models.Model):
    user = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="related_user")
    resources = models.ManyToManyField(Resource)
    
    def class_name(self):
        return "Owner"
    
    class Meta:
        verbose_name = "Owner"
        #for database name

# Create your models here.
class CustomUser(AbstractUser, models.Model):
    username = models.CharField(max_length=20, unique=True)
    firstname = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=1,
        choices=(('M', 'M'),('F', 'F')),
        null=True,
        blank=True
    )
    birthDate = models.DateField(null=True, blank=True)
    icNumber = models.CharField(max_length=12, null=True, blank=True)
    email = models.EmailField()
    profilePic = models.ImageField(upload_to="profile_pics/", default='profile_pics/default.jpg')
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="related_tenant", null=True)
    owner = models.OneToOneField(Owner, on_delete=models.CASCADE, related_name="related_owner", null=True)
    
class Announcement(models.Model):
    announceTitle = models.CharField(max_length=100)
    announceDate = models.DateField()
    announceDesc = models.CharField(max_length=1000)