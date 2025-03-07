from django.contrib import admin
from django.http import HttpRequest

from apps.campaign.forms import CampaignForm, CampaignReportForm
from apps.campaign.models import (
    Campaign,
    CampaignClick,
    CampaignImpression,
    CampaignReport,
)


class CampaignAdmin(admin.ModelAdmin):
    form = CampaignForm
    readonly_fields = (
        Campaign.id.field.name,
        Campaign.advertiser.field.name,
    )
    fields = (
        Campaign.id.field.name,
        Campaign.advertiser.field.name,
        Campaign.impressions_limit.field.name,
        Campaign.clicks_limit.field.name,
        Campaign.cost_per_impression.field.name,
        Campaign.cost_per_click.field.name,
        Campaign.ad_title.field.name,
        Campaign.ad_text.field.name,
        Campaign.ad_image.field.name,
        Campaign.start_date.field.name,
        Campaign.end_date.field.name,
        Campaign.gender.field.name,
        Campaign.age_from.field.name,
        Campaign.age_to.field.name,
        Campaign.location.field.name,
    )

    def has_add_permission(
        self, request: HttpRequest, obj: Campaign = None
    ) -> bool:
        return False


class CampaignImpressionAdmin(admin.ModelAdmin):
    readonly_fields = (
        CampaignImpression.id.field.name,
        CampaignImpression.campaign.field.name,
        CampaignImpression.client.field.name,
        CampaignImpression.date.field.name,
    )
    fields = (
        CampaignImpression.id.field.name,
        CampaignImpression.campaign.field.name,
        CampaignImpression.client.field.name,
        CampaignImpression.date.field.name,
        CampaignImpression.price.field.name,
    )

    def has_add_permission(
        self, request: HttpRequest, obj: CampaignImpression = None
    ) -> bool:
        return False


class CampaignClickAdmin(admin.ModelAdmin):
    readonly_fields = (
        CampaignClick.id.field.name,
        CampaignClick.campaign.field.name,
        CampaignClick.client.field.name,
        CampaignClick.date.field.name,
    )
    fields = (
        CampaignClick.id.field.name,
        CampaignClick.campaign.field.name,
        CampaignClick.client.field.name,
        CampaignClick.date.field.name,
        CampaignClick.price.field.name,
    )

    def has_add_permission(
        self, request: HttpRequest, obj: CampaignClick = None
    ) -> bool:
        return False


class CampaignReportAdmin(admin.ModelAdmin):
    form = CampaignReportForm
    readonly_fields = (
        CampaignReport.id.field.name,
        CampaignReport.campaign.field.name,
        CampaignReport.client.field.name,
        CampaignReport.message.field.name,
        CampaignReport.flagged_by_llm.field.name,
    )
    fields = (
        CampaignReport.id.field.name,
        CampaignReport.campaign.field.name,
        CampaignReport.client.field.name,
        CampaignReport.state.field.name,
        CampaignReport.message.field.name,
        CampaignReport.flagged_by_llm.field.name,
    )
    list_filter = (
        CampaignReport.state.field.name,
        CampaignReport.flagged_by_llm.field.name,
    )
    list_display = (
        "__str__",
        CampaignReport.flagged_by_llm.field.name,
    )

    def has_add_permission(
        self, request: HttpRequest, obj: CampaignReport = None
    ) -> bool:
        return False


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignImpression, CampaignImpressionAdmin)
admin.site.register(CampaignClick, CampaignClickAdmin)
admin.site.register(CampaignReport, CampaignReportAdmin)
