from datetime import timedelta
from django import forms
from django.utils import timezone
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    starts_at = forms.DateTimeField(widget=forms.DateTimeInput(attrs={"type":"datetime-local"}), input_formats=["%Y-%m-%dT%H:%M"])
    class Meta: model=Appointment; fields=["patient","practitioner","service","starts_at","notes"]
    def __init__(self,*args,clinic=None,**kwargs):
        super().__init__(*args,**kwargs); self.clinic=clinic
        for field in ["patient","practitioner","service"]: self.fields[field].queryset=self.fields[field].queryset.filter(clinic=clinic,active=True)
    def save(self,commit=True):
        obj=super().save(False); obj.clinic=self.clinic; obj.ends_at=obj.starts_at+timedelta(minutes=obj.service.duration_minutes); obj.full_clean()
        if commit: obj.save()
        return obj
