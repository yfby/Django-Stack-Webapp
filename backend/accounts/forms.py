from datetime import timedelta
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac
from database.models import LoginThrottle
User = get_user_model()

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, label="Your name")
    email = forms.EmailField()
    workspace_name = forms.CharField(max_length=40, label="Print shop name", initial="My print shop")
    sample_data = forms.BooleanField(required=False, initial=True, label="Start with sample print jobs")
    class Meta:
        model = User
        fields = ("first_name", "email", "username", "workspace_name", "password1", "password2", "sample_data")
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered. Sign in or reset your password.")
        return email

class DeskAuthenticationForm(AuthenticationForm):
    """A database-backed per-username/IP throttle, shared by WSGI workers."""
    def clean(self):
        username = self.cleaned_data.get("username", "").casefold()
        address = self.request.META.get("REMOTE_ADDR", "") if self.request else ""
        key = salted_hmac("flowdesk.login", username + ":" + address).hexdigest()
        now = timezone.now()
        with transaction.atomic():
            throttle, _ = LoginThrottle.objects.select_for_update().get_or_create(key=key)
            if now - throttle.window_start > timedelta(minutes=10):
                throttle.failures, throttle.window_start = 0, now
                throttle.save()
            blocked = throttle.failures >= 5
        if blocked:
            raise forms.ValidationError("Too many sign-in attempts. Try again in 10 minutes.")
        try:
            data = super().clean()
        except forms.ValidationError:
            from django.db.models import F
            LoginThrottle.objects.filter(key=key).update(failures=F("failures") + 1)
            raise
        LoginThrottle.objects.filter(key=key).delete()
        return data

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name")

class WorkspaceForm(forms.Form):
    name = forms.CharField(max_length=40)
    sample_data = forms.BooleanField(required=False, label="Include sample print jobs")

class InviteForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=[("agent", "Agent · manage print jobs"), ("viewer", "Viewer · read only"), ("manager", "Manager · jobs and settings")])


class MemberRoleForm(forms.Form):
    role = forms.ChoiceField(choices=[("agent", "Agent"), ("viewer", "Viewer"), ("manager", "Manager")])
