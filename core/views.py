from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import AppointmentForm
from .models import Appointment, AppointmentEvent, Reminder

def clinic_for(user):
    return getattr(getattr(user,"staff_profile",None),"clinic",None)

@login_required
def dashboard(request):
    clinic=clinic_for(request.user)
    if not clinic: return render(request,"core/no_access.html",status=403)
    today=timezone.localdate(); qs=Appointment.objects.filter(clinic=clinic,starts_at__date=today).select_related("patient","practitioner","service")
    counts={s:qs.filter(status=s).count() for s,_ in Appointment.Status.choices}
    reminders=Reminder.objects.filter(appointment__clinic=clinic,scheduled_for__date=today)
    context={"clinic":clinic,"appointments":qs,"counts":counts,"total":qs.count(),"delivered":reminders.filter(status=Reminder.Status.DELIVERED).count(),"failed":reminders.filter(status=Reminder.Status.FAILED).count()}
    return render(request,"core/dashboard.html",context)

@login_required
def appointment_create(request):
    clinic=clinic_for(request.user)
    if not clinic: return render(request,"core/no_access.html",status=403)
    form=AppointmentForm(request.POST or None,clinic=clinic)
    if request.method=="POST" and form.is_valid():
        appt=form.save(False); appt.created_by=request.user; appt.save()
        AppointmentEvent.objects.create(appointment=appt,to_status=appt.status,actor=request.user,reason="Appointment created")
        if appt.patient.whatsapp_consent:
            Reminder.objects.bulk_create([
                Reminder(appointment=appt,scheduled_for=timezone.now(),template_code="booking_confirmation"),
                Reminder(appointment=appt,scheduled_for=appt.starts_at-timedelta(hours=24),template_code="appointment_24h"),
                Reminder(appointment=appt,scheduled_for=appt.starts_at-timedelta(hours=2),template_code="appointment_2h"),
            ],ignore_conflicts=True)
        messages.success(request,"Appointment booked and reminder jobs created."); return redirect("dashboard")
    return render(request,"core/appointment_form.html",{"form":form,"clinic":clinic})

@login_required
def appointment_status(request,pk,status):
    clinic=clinic_for(request.user); appt=get_object_or_404(Appointment,pk=pk,clinic=clinic)
    allowed={x for x,_ in Appointment.Status.choices}
    if request.method=="POST" and status in allowed:
        old=appt.status; appt.status=status; appt.save(update_fields=["status","updated_at"])
        AppointmentEvent.objects.create(appointment=appt,from_status=old,to_status=status,actor=request.user)
        if status in {Appointment.Status.CANCELLED,Appointment.Status.COMPLETED,Appointment.Status.NO_SHOW}:
            appt.reminders.filter(status=Reminder.Status.QUEUED).update(status=Reminder.Status.SKIPPED)
        messages.success(request,"Appointment status updated.")
    return redirect("dashboard")
