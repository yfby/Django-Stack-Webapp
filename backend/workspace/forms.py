from django import forms
from django.contrib.auth import get_user_model
from database.models import Membership
from database.models import ACCENTS, STATUSES, Ticket, Workspace


class TicketForm(forms.ModelForm):
    version = forms.IntegerField(required=False, widget=forms.HiddenInput)
    def __init__(self, *args, workspace=None, **kwargs):
        super().__init__(*args, **kwargs)
        members = Membership.objects.filter(workspace=workspace, role__in=["owner", "manager", "agent"]).values("user_id")
        self.fields["assignee"].queryset = get_user_model().objects.filter(id__in=members).order_by("first_name", "username")
        self.fields["assignee"].label_from_instance = lambda user: user.get_full_name() or user.get_username()
        self.fields["assignee"].empty_label = "Unassigned"
        if self.instance.pk:
            self.fields["version"].initial = self.instance.version
            self.fields["version"].required = True
    class Meta:
        model = Ticket
        fields = ("title", "description", "category", "status", "priority", "due_date", "assignee", "requester_email",
                  "customer_name", "contact_number", "copies", "paper_size")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "What should the shop print, finish, or prepare?"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "customer_name": forms.TextInput(attrs={"placeholder": "e.g. Riverside Café"}),
            "contact_number": forms.TextInput(attrs={"placeholder": "Phone or extension"}),
            "copies": forms.NumberInput(attrs={"min": 1, "placeholder": "e.g. 120"}),
            "paper_size": forms.TextInput(attrs={"placeholder": "e.g. A4, A5, 85×55 mm"}),
        }

    def clean_title(self):
        value = self.cleaned_data["title"].strip()
        if not value:
            raise forms.ValidationError("Give this item a title.")
        return value

    def clean_category(self):
        value = self.cleaned_data["category"].strip()
        if not value:
            raise forms.ValidationError("Enter a category.")
        return value


class PreferencesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep the existing stored key so current databases need no migration.
        self.fields["accent"].choices = [("teal", "Dashboard purple (default)"), ("violet", "Violet"), ("forest", "Forest"), ("clay", "Clay")]

    class Meta:
        model = Workspace
        fields = ("name", "accent")

    def clean_name(self):
        value = self.cleaned_data["name"].strip()
        if not value:
            raise forms.ValidationError("Enter a workspace name.")
        return value


class MoveForm(forms.Form):
    status = forms.ChoiceField(choices=STATUSES)


class WorkflowForm(forms.Form):
    operation = forms.ChoiceField(choices=[
        ("append", "Add to end · append"), ("prepend", "Add to start · prepend"),
        ("insert_at", "Insert at position · insert_at"), ("remove_at", "Remove at position · remove_at"),
        ("remove", "Remove first matching step · remove"), ("get", "Read at position · get"),
        ("index_of", "Find first position · index_of"),
    ])
    value = forms.CharField(max_length=80, required=False)
    index = forms.IntegerField(min_value=0, required=False)

    def clean(self):
        data = super().clean()
        op = data.get("operation")
        if op in {"append", "prepend", "insert_at", "remove", "index_of"} and not data.get("value", "").strip():
            self.add_error("value", "This operation needs a value.")
        if op in {"insert_at", "remove_at", "get"} and data.get("index") is None:
            if "index" not in self.errors:
                self.add_error("index", "This operation needs an index.")
        return data


class CommentForm(forms.Form):
    body = forms.CharField(max_length=3000, widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Add context, a handoff, or a progress update…"}), label="Team note")


class StatusNoteForm(forms.Form):
    status_note = forms.CharField(
        max_length=500,
        required=False,
        label="Job status note",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "e.g. Proof sent to the customer; waiting for approval before printing."}),
        help_text="A quick update visible on this print job. Clear it and save to remove the note.",
    )
