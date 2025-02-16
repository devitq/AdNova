import typing
from uuid import UUID

from ninja import ModelSchema

from apps.advertiser.models import Advertiser as AdvertiserModel
from apps.mlscore.models import Mlscore as MlscoreModel


class Advertiser(ModelSchema):
    advertiser_id: UUID

    class Meta:
        model = AdvertiserModel
        exclude: typing.ClassVar[tuple[str]] = (AdvertiserModel.id.field.name,)


class Mlscore(ModelSchema):
    class Meta:
        model = MlscoreModel
        exclude: typing.ClassVar[tuple[str]] = (MlscoreModel.id.field.name,)
