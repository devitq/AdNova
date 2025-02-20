import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram_dialog import setup_dialogs

import config
from commands.campaigns import campaigns_router
from commands.logout import logout_router
from commands.start import start_router
from commands.stats import statistics_router
from dialogs.campaigns import campaigns_dialog
from dialogs.start import start_dialog
from middlewares.auth import AuthMiddleware
from middlewares.throttling import ThrottlingMiddleware

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(levelname)-8s %(filename)s:%(lineno)d"
            " [%(asctime)s] - %(name)s - %(message)s"
        ),
    )
    logger.info("Starting bot...")

    bot: Bot = Bot(
        config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML")
    )
    dp: Dispatcher = Dispatcher(
        storage=RedisStorage.from_url(
            config.REDIS_URI,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        ),
    )

    dp.message.middleware(ThrottlingMiddleware(0.5))
    dp.message.outer_middleware(AuthMiddleware())

    dp.include_routers(
        start_router,
        campaigns_router,
        statistics_router,
        logout_router,
    )
    dp.include_routers(start_dialog, campaigns_dialog)

    setup_dialogs(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
