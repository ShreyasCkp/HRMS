from django import forms
from django.forms import inlineformset_factory
from .models import PerformanceReview, PerformanceScore


class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['employee', 'review_period', 'feedback', 'reviewed_by']
        widgets = {
            'review_period': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Q1 2025'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'reviewed_by': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PerformanceScoreForm(forms.ModelForm):
    class Meta:
        model = PerformanceScore
        fields = ['kpi', 'score']
        widgets = {
            'kpi': forms.Select(attrs={'class': 'form-control'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 10}),
        }


# Only 1 KPI form will be shown by default
PerformanceScoreFormSet = inlineformset_factory(
    PerformanceReview,
    PerformanceScore,
    form=PerformanceScoreForm,
       extra=1,    # only 1 by default
    can_delete=True
)
