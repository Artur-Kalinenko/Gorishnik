from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} ⭐") for i in range(1, 6)],
        widget=forms.RadioSelect,
        label=_("Оцінка")
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'maxlength': 500, 'id': 'id_comment'}),
        required=False,
        label=_("Відгук"),
        max_length=500
    )

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '')
        if len(comment) > 500:
            raise forms.ValidationError(_("Відгук не повинен перевищувати 500 символів."))
        return comment

    class Meta:
        model = Review
        fields = ['rating', 'comment']
