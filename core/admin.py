from django.contrib import admin
from .models import Clinic,StaffProfile,Patient,Practitioner,Service,Appointment,AppointmentEvent,Reminder
for m in [Clinic,StaffProfile,Patient,Practitioner,Service,Appointment,AppointmentEvent,Reminder]: admin.site.register(m)
