from typing import Any

from django import forms

from apps.campaign.models import Campaign, CampaignReport


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = "__all__"

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        location = cleaned_data.get("location")

        if location == "":
            cleaned_data["location"] = None

        return cleaned_data


class CampaignReportForm(forms.ModelForm):
    class Meta:
        model = CampaignReport
        fields = "__all__"

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        message = cleaned_data.get("message")

        if message == "":
            cleaned_data["message"] = None

        return cleaned_data
