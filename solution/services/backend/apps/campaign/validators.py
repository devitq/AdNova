from django.core.exceptions import ValidationError


class CampaignAgeValidator:
    def __call__(self, instance) -> None:  # noqa: ANN001
        if (
            isinstance(instance.age_from, int)
            and isinstance(instance.age_to, int)
            and instance.age_from > instance.age_to
        ):
            err = "age_from can't be greater than age_to"
            raise ValidationError(err)


class CampaignDurationValidator:
    def __call__(self, instance) -> None:  # noqa: ANN001
        if (
            isinstance(instance.start_date, int)
            and isinstance(instance.end_date, int)
            and instance.start_date > instance.end_date
        ):
            err = "start_date can't be greater than end_date"
            raise ValidationError(err)


class CampaignLimitsValidator:
    def __call__(self, instance) -> None:  # noqa: ANN001
        if (
            isinstance(instance.impressions_limit, int)
            and isinstance(instance.clicks_limit, int)
            and instance.impressions_limit < instance.clicks_limit
        ):
            err = "clicks_limit can't be greater than impressions_limit"
            raise ValidationError(err)


class CampaignTargetingLocationValidator:
    def __call__(self, instance) -> None:  # noqa: ANN001
        if instance.location == "":
            err = "targeting.location cannot be blank"
            raise ValidationError(err)


class CampaignReportMessageValidator:
    def __call__(self, instance) -> None:  # noqa: ANN001
        if instance.message == "":
            err = "message cannot be blank"
            raise ValidationError(err)
