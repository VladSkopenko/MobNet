from typing import Tuple

from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from common.messages import MODEL_BUTTONS


def get_callback_buttons(
   buttons, sizes: Tuple[int] = (2,)
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for text, data in buttons.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    keyboard.adjust(*sizes)

    return keyboard.as_markup()


async def choice_model() -> InlineKeyboardMarkup:
    buttons = MODEL_BUTTONS
    keyboard = get_callback_buttons(
        buttons,
        (2,),
    )
    return keyboard
