from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Clinic,StaffProfile,Patient,Practitioner,Service,Appointment,Reminder

class Command(BaseCommand):
    help="Create safe synthetic ClinicFlow demo data"
    def handle(self,*args,**kwargs):
        User=get_user_model(); clinic,_=Clinic.objects.get_or_create(name="ClinicFlow Demo Clinic",branch="Rawalpindi")
        user,_=User.objects.get_or_create(username="admin",defaults={"email":"admin@example.test","first_name":"Demo","last_name":"Manager","is_staff":True,"is_superuser":True})
        user.set_password("ClinicFlow2026!"); user.save(); StaffProfile.objects.update_or_create(user=user,defaults={"clinic":clinic,"role":"admin"})
        service,_=Service.objects.get_or_create(clinic=clinic,name="General Consultation",defaults={"duration_minutes":30})
        doctor,_=Practitioner.objects.get_or_create(clinic=clinic,full_name="Ayesha Khan",defaults={"specialty":"General Medicine","registration_no":"DEMO-PMDC-001"})
        names=[("P-0001","Ali Raza","+923001111111"),("P-0002","Sara Ahmed","+923002222222"),("P-0003","Usman Tariq","+923003333333")]
        base=timezone.localtime().replace(hour=9,minute=0,second=0,microsecond=0)
        for i,(no,name,mobile) in enumerate(names):
            patient,_=Patient.objects.get_or_create(clinic=clinic,patient_no=no,defaults={"full_name":name,"mobile":mobile,"whatsapp_consent":True,"consent_captured_at":timezone.now()})
            start=base+timedelta(hours=i*2); appt,_=Appointment.objects.get_or_create(clinic=clinic,patient=patient,practitioner=doctor,starts_at=start,defaults={"service":service,"ends_at":start+timedelta(minutes=30),"status":"confirmed" if i==0 else "scheduled","created_by":user})
            Reminder.objects.get_or_create(appointment=appt,template_code="appointment_24h",scheduled_for=start-timedelta(hours=24))
        self.stdout.write(self.style.SUCCESS("Demo ready: admin / ClinicFlow2026!"))
