from django import forms

from .models import LoanRequest, SavingsRecord


class SavingsRecordForm(forms.ModelForm):
    class Meta:
        model = SavingsRecord
        fields = ["amount", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ["name", "id_number", "amount", "purpose", "document"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "document":
                field.widget.attrs.update({"class": "form-control"})
            else:
                field.widget.attrs.update({"class": "form-control"})
