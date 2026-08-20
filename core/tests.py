from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from .models import Clinic,Patient,Practitioner,Service,Appointment

class AppointmentRulesTest(TestCase):
    def setUp(self):
        self.clinic=Clinic.objects.create(name="Test Clinic"); self.patient=Patient.objects.create(clinic=self.clinic,patient_no="P1",full_name="Test Patient",mobile="+923001234567")
        self.doctor=Practitioner.objects.create(clinic=self.clinic,full_name="Doctor One"); self.service=Service.objects.create(clinic=self.clinic,name="Consultation",duration_minutes=30)
    def test_rejects_doctor_overlap(self):
        start=timezone.now()+timedelta(days=1); Appointment.objects.create(clinic=self.clinic,patient=self.patient,practitioner=self.doctor,service=self.service,starts_at=start,ends_at=start+timedelta(minutes=30))
        clash=Appointment(clinic=self.clinic,patient=self.patient,practitioner=self.doctor,service=self.service,starts_at=start+timedelta(minutes=10),ends_at=start+timedelta(minutes=40))
        with self.assertRaises(ValidationError): clash.full_clean()
