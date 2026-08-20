from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

class Clinic(models.Model):
    name = models.CharField(max_length=160)
    branch = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=24, blank=True)
    timezone = models.CharField(max_length=64, default="Asia/Karachi")
    active = models.BooleanField(default=True)
    def __str__(self): return f"{self.name} — {self.branch}" if self.branch else self.name

class StaffProfile(models.Model):
    class Role(models.TextChoices):
        RECEPTION="reception", "Reception"; DOCTOR="doctor", "Doctor"; MANAGER="manager", "Manager"; ADMIN="admin", "Administrator"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile")
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name="staff")
    role = models.CharField(max_length=20, choices=Role.choices)
    phone = models.CharField(max_length=24, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

class Patient(models.Model):
    class Language(models.TextChoices): EN="en", "English"; UR="ur", "Urdu"; ROMAN="roman_ur", "Roman Urdu"
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name="patients")
    patient_no = models.CharField(max_length=30)
    full_name = models.CharField(max_length=160)
    mobile = models.CharField(max_length=20, help_text="Use +92XXXXXXXXXX")
    language = models.CharField(max_length=12, choices=Language.choices, default=Language.EN)
    whatsapp_consent = models.BooleanField(default=False)
    consent_captured_at = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["clinic","patient_no"], name="unique_patient_no_per_clinic")]
        indexes = [models.Index(fields=["clinic","mobile"]), models.Index(fields=["clinic","full_name"])]
    def __str__(self): return f"{self.patient_no} — {self.full_name}"

class Service(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120)
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    active = models.BooleanField(default=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["clinic","name"], name="unique_service_per_clinic")]
    def __str__(self): return self.name

class Practitioner(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name="practitioners")
    full_name = models.CharField(max_length=160)
    specialty = models.CharField(max_length=120, blank=True)
    registration_no = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return f"Dr. {self.full_name}"

class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED="scheduled","Scheduled"; CONFIRMED="confirmed","Confirmed"; CHECKED_IN="checked_in","Checked in"
        COMPLETED="completed","Completed"; CANCELLED="cancelled","Cancelled"; NO_SHOW="no_show","No-show"
    clinic = models.ForeignKey(Clinic, on_delete=models.PROTECT, related_name="appointments")
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name="appointments")
    practitioner = models.ForeignKey(Practitioner, on_delete=models.PROTECT, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="appointments")
    starts_at = models.DateTimeField(); ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.CharField(max_length=300, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="created_appointments")
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering=["starts_at"]
        indexes=[models.Index(fields=["clinic","starts_at"]), models.Index(fields=["clinic","status"])]
        constraints=[models.CheckConstraint(condition=Q(ends_at__gt=models.F("starts_at")), name="appointment_end_after_start")]
    def clean(self):
        if self.patient_id and self.patient.clinic_id != self.clinic_id: raise ValidationError("Patient belongs to another clinic.")
        if self.practitioner_id and self.practitioner.clinic_id != self.clinic_id: raise ValidationError("Practitioner belongs to another clinic.")
        if self.service_id and self.service.clinic_id != self.clinic_id: raise ValidationError("Service belongs to another clinic.")
        if self.starts_at and self.ends_at:
            clash=Appointment.objects.filter(clinic=self.clinic, practitioner=self.practitioner, starts_at__lt=self.ends_at, ends_at__gt=self.starts_at).exclude(pk=self.pk).exclude(status=Appointment.Status.CANCELLED)
            if clash.exists(): raise ValidationError("This doctor already has an appointment during the selected time.")
    def __str__(self): return f"{self.patient.full_name} — {self.starts_at:%d %b %Y %H:%M}"

class AppointmentEvent(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="events")
    from_status = models.CharField(max_length=20, blank=True); to_status = models.CharField(max_length=20)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    reason = models.CharField(max_length=300, blank=True); created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=["-created_at"]

class Reminder(models.Model):
    class Status(models.TextChoices): QUEUED="queued","Queued"; SENT="sent","Sent"; DELIVERED="delivered","Delivered"; FAILED="failed","Failed"; SKIPPED="skipped","Skipped"
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="reminders")
    scheduled_for = models.DateTimeField(); status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    template_code = models.CharField(max_length=80); provider_message_id = models.CharField(max_length=160, blank=True)
    error = models.CharField(max_length=300, blank=True); created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=["appointment","template_code","scheduled_for"], name="unique_reminder_job")]
