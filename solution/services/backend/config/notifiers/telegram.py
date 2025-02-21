import datetime
import logging
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import httpx
from django.utils.timezone import get_current_timezone

TELEGRAM_LOG_HANDLER = logging.getLogger("telegram_log_handler")

LEVEL_EMOJIS = {
    "DEBUG": "🐞",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🚨",
}


class LoggingHandler(logging.Handler):
    _executor = ThreadPoolExecutor(max_workers=5)

    def __init__(
        self,
        token: str,
        chat_id: int,
        thread_id: int | None = None,
        retries: int | None = 3,
        delay: int | None = 2,
        timeout: int | None = 5,
    ) -> None:
        super().__init__()

        self.token = token
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.retries = retries
        self.delay = delay
        self.timeout = timeout
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        self.template = (
            "<b>{levelname}</b>\n"
            "\t<b>Guid:</b> <code>{correlation_id}</code>\n"
            "\t<b>Timestamp:</b> <code>{asctime}</code>\n"
            "\t<b>Logger:</b> <code>{name}</code>\n"
            "\t<b>File:</b> <code>{pathname}</code> "
            "(Line: <code>{lineno}</code>)\n\n"
            '<pre><code class="language-message">{message}</code></pre>\n'
        )

    def emit(self, record: logging.LogRecord) -> None:
        try:
            formatted_record = self.format(record)
            self._executor.submit(self._send_message, formatted_record)
        except Exception as e:  # noqa: BLE001
            self.handleError(record)
            TELEGRAM_LOG_HANDLER.exception(e)

    def _send_message(self, formatted_record: str) -> None:
        payload = {
            "chat_id": self.chat_id,
            "text": formatted_record,
            "parse_mode": "HTML",
        }
        if self.thread_id:
            payload["reply_to_message_id"] = self.thread_id

        for attempt in range(1, self.retries + 1):
            response = httpx.post(
                self.api_url,
                data=payload,
                timeout=self.timeout,
            )
            if response.status_code != httpx.codes.OK:
                if attempt == self.retries:
                    TELEGRAM_LOG_HANDLER.exception(
                        "Failed to send to Telegram after %d attempts: %s",
                        self.retries,
                        response.text,
                    )
                else:
                    time.sleep(self.delay)
            else:
                return

    def format(self, record: logging.LogRecord) -> str:
        try:
            asctime = datetime.datetime.fromtimestamp(
                record.created,
                tz=get_current_timezone(),
            ).strftime("%Y-%m-%d %H:%M:%S %Z")
            level_emoji = LEVEL_EMOJIS.get(record.levelname, "")

            formatted_message = self.template.format(
                levelname=f"{level_emoji} {record.levelname}",
                correlation_id=getattr(record, "correlation_id", "N/A"),
                asctime=asctime,
                name=record.name,
                pathname=record.pathname,
                lineno=record.lineno,
                message=record.getMessage(),
            )

            if record.exc_info:
                formatted_message += self._format_exception(record.exc_info)

            formatted_message += (
                f"\n#{record.levelname.lower()} "
                f"#{record.name.replace('.', '_')}"
            )
            if hasattr(record, "correlation_id"):
                formatted_message += f" #{record.correlation_id}"
        except Exception as format_error:  # noqa: BLE001
            TELEGRAM_LOG_HANDLER.exception(
                "Error formatting log record: %s",
                format_error,
            )
            return f"Error formatting log record: {format_error}"
        else:
            return formatted_message

    @staticmethod
    def _format_exception(exc_info: Exception) -> str:
        exc_text = "".join(traceback.format_exception(*exc_info))
        return (
            f"\n<pre><code class='language-traceback'>{exc_text}</code></pre>"
        )

    @classmethod
    def shutdown_executor(cls) -> None:
        cls._executor.shutdown(wait=True)
