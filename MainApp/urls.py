from django.urls import path, reverse_lazy
from django.contrib.auth.views import *
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('user_registration', views.user_registration, name='user_registration'),
    path('resource_listings', views.resource_listings, name='resource_listings'),
    path('resource_listings/<str:pk>', views.listing_details, name='listing_details'),
    path('resource_listings/<str:pk>/apply', views.apply_to_lease, name="apply_to_lease"),
    path('leasing_requests', views.leasing_requests, name='leasing_requests'),
    path('leasing_requests/<str:pk>/approve', views.approve_request, name='approve_request'),
    path('leasing_requests/<str:pk>/reject', views.reject_request, name='reject_request'),
    path('add_listing', views.add_listing, name='add_listing'),
    path('my_listings', views.my_listings, name='my_listings'),
    path('my_listings/<str:pk>/remove', views.remove_listing, name='remove_listing'),
    path('my_listings/<str:pk>/edit', views.edit_listing, name='edit_listing'),
    path('my_requests', views.my_requests, name='my_requests'),
    path('announcements', views.announcements, name='announcements'),
    path('make_announcements', views.make_announcements, name='make_announcements'),
    path('announcements/<str:pk>', views.announcement_details, name='announcement_details'),
    path('incident_reports', views.incident_reports, name='incident_reports'),
    path('incident_reports/<str:pk>', views.report_details, name='report_details'),
    path('make_report', views.make_report, name='make_report'),
    path('user/<str:pk>', views.view_profile, name='view_profile'),
    path('user/<str:pk>/edit', views.edit_profile, name='edit_profile')
]