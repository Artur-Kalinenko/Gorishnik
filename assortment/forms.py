from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} ⭐") for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Оцінка"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Відгук"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
