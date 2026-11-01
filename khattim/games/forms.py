from django import forms

from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["display_name", "avatar"]

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

    session_length = forms.ChoiceField(choices=TIME_CHOICES)
    mood = forms.ChoiceField(choices=MOOD_CHOICES)