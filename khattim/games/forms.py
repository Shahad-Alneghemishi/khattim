from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        username = self.fields["username"]
        username.help_text = ""
        username.error_messages["invalid"] = (
            "Username can only contain letters, numbers, and @ . + - _ (no spaces)."
        )
        username.error_messages["unique"] = "This username is already taken."

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "avatar"]

SELECT_CLASSES = (
    "w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm"
    "dark:border-slate-700 dark:bg-slate-800"
)

class RecommendForm(forms.Form):
    TIME_CHOICES = [
        ("short", "Short (under 1 hour)"),
        ("medium", "Medium (1-3 hours)"),
        ("long", "Long (3+ hours)"),
    ]
    MOOD_CHOICES = [
        ("relax", "Relax"),
        ("story", "Story"),
        ("challenge", "Challenge"),
        ("action", "Action"),
    ]

    session_length = forms.ChoiceField(
        choices=TIME_CHOICES,
        label="How much time do you have?",
        widget=forms.Select(attrs={"class": SELECT_CLASSES})
    )
    mood = forms.ChoiceField(
        choices=MOOD_CHOICES,
        label="What's your mood?",
        widget=forms.Select(attrs={"class": SELECT_CLASSES})
    )