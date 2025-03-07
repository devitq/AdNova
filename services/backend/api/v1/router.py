from functools import partial

from ninja import NinjaAPI

from api.v1 import handlers
from api.v1.ads.views import router as ads_router
from api.v1.advertisers.views import router as advertisers_router
from api.v1.campaigns.views import router as compaigns_router
from api.v1.clients.views import router as clients_router
from api.v1.generate.views import router as generate_router
from api.v1.report.views import router as report_router
from api.v1.stats.views import router as stats_router
from api.v1.time.views import router as time_router

router = NinjaAPI(
    title="AdNova API",
    version="1",
    description="API docs for AdNova",
    openapi_url="/docs/openapi.json",
)


router.add_router(
    "clients",
    clients_router,
)
router.add_router(
    "",
    advertisers_router,
)
router.add_router(
    "advertisers",
    compaigns_router,
)
router.add_router(
    "ads",
    ads_router,
)
router.add_router(
    "stats",
    stats_router,
)
router.add_router(
    "generate",
    generate_router,
)
router.add_router(
    "report",
    report_router,
)
router.add_router(
    "time",
    time_router,
)


for exception, handler in handlers.exception_handlers:
    router.add_exception_handler(exception, partial(handler, router=router))
