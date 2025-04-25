from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import *
from SharedResources import *

import datetime
import sqlite3

connect = sqlite3.connect('db.sqlite3', check_same_thread=False)
cursor = connect.cursor()

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'login.html')
    
def dashboard(request):
    loggedin = ""
        
    if request.user.is_superuser:
        loggedin = "Admin"
    elif request.user.owner is not None:
        loggedin = "Owner"
    elif request.user.tenant is not None:
        loggedin = "Tenant"
        
    return render(request, 'dashboard.html', {'loggedin': loggedin})

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate(username=username, password=password)
        
        # user exists
        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')
        # user does not exist
        else:
            messages.info(request, 'Credentials not valid')
            return redirect('login')
        
    else:
        return render(request, 'login.html')
    
def logout(request):
    auth.logout(request)
    return render(request, 'login.html')

def user_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        usertype = request.POST['usertype']
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        unitnum = request.POST.get('block') + "-" + request.POST.get('floor') + "-" + request.POST.get('unit')
        password = request.POST.get('password')
    
        if CustomUser.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            return redirect('user_registration')
        else:
            
            if usertype == "tenant":
                tenant = Tenant(unitNumber=unitnum)
                tenant.save()
                user = CustomUser(username=username,
                                  password=password,
                                  firstname=firstname,
                                  lastname=lastname,
                                  email=email,
                                  tenant=tenant)
            elif usertype == "owner":
                tenant = Tenant(unitNumber=unitnum)
                tenant.save()
                owner = Owner(user=tenant)
                owner.save()
                user = CustomUser(username=username,
                                  password=password,
                                  firstname=firstname, 
                                  lastname=lastname,
                                  email=email,
                                  tenant=tenant,
                                  owner=owner)
            
            user.set_password(password)
            user.save()
            
            return redirect('index')
    
    return render(request, 'user_registration.html')

def resource_listings(request):
    listings = Resource.objects.all()
    
    return render(request, 'resource_listings.html', {'listings': listings})

def add_listing(request):
    if request.method == 'POST':
        resourcename = request.POST.get('resourcename')
        resourcetype = request.POST['resourcetype']
        resourcedesc = request.POST.get('resourcedesc')
        resourceimage = request.FILES['resourceimage']
        
        resource = Resource(resourceName=resourcename, 
                            uploadedBy=request.user.username,
                            resourceType=resourcetype,
                            resourceDesc=resourcedesc,
                            resourceImage=resourceimage,
                            uploadDate=datetime.datetime.now())
        resource.save()
        if request.user.owner is not None:
            request.user.owner.resources.add(resource)
        else:
            resource.uploadedBy = "Admin"
            resource.save()
        return redirect('resource_listings')
        
    else:
        return render(request, 'add_listing.html')

def listing_details(request, pk):
    return render(request, 'listing_details.html', {'listing': Resource.objects.get(pk=pk)})

def leasing_requests(request):
    requests = []
    
    # if user is an owner
    if request.user.owner is not None:
        for rq in LeasingRequest.objects.all():
            if rq.resourceLeased.uploadedBy == request.user.username and rq.requestStatus is None:
                requests.append(rq)
    # if user is an admin
    else:
        for rq in LeasingRequest.objects.all():
            if rq.resourceLeased.uploadedBy == "Admin" and rq.requestStatus is None:
                requests.append(rq)
        
    return render(request, 'leasing_requests.html', {'requests': requests})
    
def approve_request(request, pk):
    rq = LeasingRequest.objects.get(pk=pk)
    rq.requestStatus = True
    rq.save()
    return redirect(leasing_requests)

def reject_request(request, pk):
    rq = LeasingRequest.objects.get(pk=pk)
    rq.requestStatus = False
    rq.save()
    return redirect(leasing_requests)

def apply_to_lease(request, pk):
    if request.method == 'POST':
        leasingstart = request.POST['leasingstart']
        leasingend = request.POST['leasingend']
        leasingdetails = request.POST.get('leasingdetails')
        
        leasingreq = LeasingRequest(resourceLeased=Resource.objects.filter(pk=pk).first(),
                                    leasedBy=request.user.username,
                                    startDate=leasingstart,
                                    endDate=leasingend,
                                    requestDate=datetime.datetime.now(),
                                    requestDesc=leasingdetails,
                                    requestStatus=None,
                                    amountPaid=0)
        leasingreq.save()
        request.user.tenant.leasingRequests.add(leasingreq)
        return redirect('resource_listings')
                        
    else:
        return render(request, 'apply_to_lease.html', {'listing': Resource.objects.get(pk=pk)})

def my_listings(request):
    listings = []
    if request.user.owner is not None:
        listings = request.user.owner.resources.all()
    else:
        for listing in Resource.objects.all():
            if listing.uploadedBy == "Admin":
                listings.append(listing)
                
    return render(request, 'my_listings.html', {'listings': listings})

def edit_listing(request, pk):
    listing = Resource.objects.get(pk=pk)
    
    if request.method == 'POST':
        resourcename = request.POST.get('resourcename')
        resourcetype = request.POST['resourcetype']
        resourcedesc = request.POST.get('resourcedesc')
        
        if 'resourceimage' in request.FILES:
            resourceimage = request.FILES.get('resourceimage')
        else:
            resourceimage = listing.resourceImage
        
        listing.resourceName = resourcename
        listing.resourceType = resourcetype
        listing.resourceDesc = resourcedesc
        listing.resourceImage = resourceimage
        listing.save()
        return redirect('my_listings')
        
    else:
        return render(request, 'edit_listing.html', {'listing': listing})

def remove_listing(request, pk):
    listing = Resource.objects.get(pk=pk)
    listing.delete()
    return redirect(resource_listings)

def my_requests(request):
    requests = request.user.tenant.leasingRequests.all()
        
    return render(request, 'my_requests.html', {'requests': requests})

def announcements(request):
    announcements = Announcement.objects.all()
    return render(request, 'announcements.html', {'announcements': announcements.order_by('-pk')})

def announcement_details(request, pk):
    return render(request, 'announcement_details.html', {'announcement': Announcement.objects.get(pk=pk)})

def make_announcements(request):
    if request.method == 'POST':
        announcetitle = request.POST.get('announcetitle')
        announcedesc = request.POST.get('announcedesc')
        
        if announcetitle is None or announcedesc is None:
            messages.info(request, 'Announcement details not valid')
            return redirect('make_announcements')
        else:
            announcement = Announcement(announceTitle=announcetitle,
                                        announceDate=datetime.datetime.now(),
                                        announceDesc=announcedesc)
            announcement.save()
            return redirect('announcements')
                        
    else:
        return render(request, 'make_announcements.html')
    
def incident_reports(request):
    reports = Report.objects.all()
    return render(request, 'incident_reports.html', {'reports': reports.order_by('-pk')})

def report_details(request, pk):
    return render(request, 'report_details.html', {'report': Report.objects.get(pk=pk)})

def make_report(request):
    if request.method == 'POST':
        reporttitle = request.POST.get('reporttitle')
        reportresource = request.POST.get('resource')
        resourceowner = request.POST.get('resourceowner')
        incidentdate = request.POST['incidentdate']
        reportdesc = request.POST.get('reportdesc')
        affectedResource = None
        
        for user in CustomUser.objects.all():
            if user.owner is not None:
                for resource in user.owner.resources.all():
                    if resourceowner == user.username and reportresource == resource.resourceName:
                        affectedResource = resource
            elif user.is_superuser:
                for resource in Resource.objects.all():
                    if resourceowner == "Admin" and reportresource == resource.resourceName:
                        affectedResource = resource
            
        if affectedResource is None:
            messages.info(request, 'Report details not valid')
            return redirect('make_report')
        
        report = Report(reportedBy=request.user.username,
                        reportTitle=reporttitle,
                        reportDate=datetime.datetime.now(),
                        affectedResource=affectedResource,
                        incidentDate=incidentdate,
                        reportDesc=reportdesc)
        report.save()
        return redirect('incident_reports')
                        
    else:
        return render(request, 'make_report.html')

def view_profile(request, pk):
    return render(request, 'view_profile.html', {'user': request.user})

def edit_profile(request, pk):
    user = CustomUser.objects.get(pk=pk)
    
    if request.method == 'POST':
        if 'profilepic' in request.FILES:
            profilepic = request.FILES.get('profilepic')
        else:
            profilepic = user.profilePic
            
        unitnum = request.POST.get('block') + "-" + request.POST.get('floor') + "-" + request.POST.get('unit')
        gender = request.POST['gender']
        birthdate = request.POST['birthdate']
        icnumber = request.POST.get('icbirth') + "-" + request.POST.get('iclocation') + "-" + request.POST.get('iclast4')
        
        user.tenant.unitNumber = unitnum
        user.gender = gender
        user.birthDate = birthdate
        user.icNumber = icnumber
        user.profilePic = profilepic
        user.tenant.save()
        user.save()
            
        return redirect('view_profile', user.pk)
        
    else:
        return render(request, 'edit_profile.html', {'user': user})