from typing import TYPE_CHECKING

from django.core.cache import cache
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from apps.campaign.models import Campaign, CampaignReport


class CampaignTargetingLocationValidator:
    def __call__(self, instance: "Campaign") -> None:
        if instance.location == "":
            err = "targeting.location can't be blank."
            raise ValidationError(err)


class CampaignTargetingGenderValidator:
    def __call__(self, instance: "Campaign") -> None:
        if instance.gender == "":
            err = "gender can't be blank."
            raise ValidationError(err)


class CampaignAgeValidator:
    def __call__(self, instance: "Campaign") -> None:
        if (
            isinstance(instance.age_from, int)
            and isinstance(instance.age_to, int)
            and instance.age_from > instance.age_to
        ):
            err = "targeting.age_from can't be greater than targeting.age_to."
            raise ValidationError(err)


class CampaignDurationValidator:
    def __call__(self, instance: "Campaign") -> None:
        if (
            isinstance(instance.start_date, int)
            and isinstance(instance.end_date, int)
            and instance.start_date > instance.end_date
        ):
            err = "start_date can't be greater than end_date."
            raise ValidationError(err)


class CampaignLimitsValidator:
    def __call__(self, instance: "Campaign") -> None:
        if (
            isinstance(instance.impressions_limit, int)
            and isinstance(instance.clicks_limit, int)
            and instance.impressions_limit < instance.clicks_limit
        ):
            err = "clicks_limit can't be greater than impressions_limit."
            raise ValidationError(err)


class CampaignStartDateValidator:
    def __call__(self, instance: "Campaign") -> None:
        current_date = cache.get("current_date", default=0)
        err = "start_date must be greater or equal than the current_date."
        try:
            original = type(instance).objects.get(id=instance.id or "")
            if (
                original.start_date != instance.start_date
                and instance.start_date < current_date
            ):
                raise ValidationError(err)
        except type(instance).DoesNotExist:
            if instance.start_date < current_date:
                raise ValidationError(err) from None


class CampaignReportMessageValidator:
    def __call__(self, instance: "CampaignReport") -> None:
        if instance.message == "":
            err = "message can't be blank."
            raise ValidationError(err)
