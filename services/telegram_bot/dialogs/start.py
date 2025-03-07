from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.text import Const
from pydantic import ValidationError

from api.client import AdNovaClient
from api.errors import NotFoundError
from api.schemas import Advertiser
from states.start import StartDialogState


def check_advertiser_id(advertiser_id: str) -> None:
    Advertiser.__pydantic_validator__.validate_assignment(
        Advertiser.model_construct(), "advertiser_id", advertiser_id
    )

    try:
        client = AdNovaClient()
        client.sync_get_advertiser(advertiser_id)
    except NotFoundError:
        raise ValueError from None


async def advertiser_id_on_error(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: object,
) -> None:
    if isinstance(error, ValidationError):
        await message.answer("Invalid advertiser UUID.")
    elif isinstance(error, ValueError):
        await message.answer("Advertiser with this UUID not found.")


async def advertiser_id_on_success(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    advertiser_id: str,
) -> None:
    state = dialog_manager.middleware_data["state"]
    state_data = await state.get_data()
    state_data["advertiser_id"] = message.text
    await state.set_data(state_data)

    await message.answer(
        f"Successfully authenticated as {message.text}. Get help: /help."
    )
    await dialog_manager.mark_closed()


start_dialog = Dialog(
    Window(
        Const("Enter adveritser UUID:"),
        TextInput(
            id="advertiser_id",
            type_factory=check_advertiser_id,
            on_success=advertiser_id_on_success,
            on_error=advertiser_id_on_error,
        ),
        state=StartDialogState.start,
    ),
)
