import html
from contextlib import suppress
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from content.raw_code import SCREENSHOT_CODE, EXPECTED_JSON

router = Router()

def get_code_back_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✍️ Тренажер: написать этот код", callback_data="practice_list"),
        ],
        [
            InlineKeyboardButton(text="📄 Код со скриншота", callback_data="view_original_code"),
            InlineKeyboardButton(text="📦 Пример JSON-файла", callback_data="view_json"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "view_original_code")
async def cb_view_original(callback: CallbackQuery) -> None:
    safe_code = html.escape(SCREENSHOT_CODE)
    text = (
        "<b>📄 Исходный код со скриншота (1 в 1):</b>\n\n"
        f"<pre><code class=\"language-bsl\">{safe_code}</code></pre>"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_code_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "view_json")
async def cb_view_json(callback: CallbackQuery) -> None:
    safe_json = html.escape(EXPECTED_JSON)
    text = (
        "<b>📦 Пример входного JSON-файла:</b>\n\n"
        f"<pre><code class=\"language-json\">{safe_json}</code></pre>"
    )
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text, reply_markup=get_code_back_keyboard(), parse_mode="HTML")
    await callback.answer()
