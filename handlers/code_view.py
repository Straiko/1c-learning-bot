import html
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from content.raw_code import ORIGINAL_CODE, EXPECTED_JSON, BEST_PRACTICE_CODE

router = Router()

def get_code_back_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📄 Исходный код", callback_data="view_original_code"),
            InlineKeyboardButton(text="📦 Пример JSON", callback_data="view_json"),
        ],
        [
            InlineKeyboardButton(text="⭐ Эталонный вариант", callback_data="view_best_practice"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "view_original_code")
async def cb_view_original(callback: CallbackQuery) -> None:
    safe_code = html.escape(ORIGINAL_CODE)
    text = (
        "<b>📄 Исходный код со скриншота:</b>\n\n"
        f"<pre><code class=\"language-bsl\">{safe_code}</code></pre>"
    )
    await callback.message.edit_text(text, reply_markup=get_code_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "view_json")
async def cb_view_json(callback: CallbackQuery) -> None:
    safe_json = html.escape(EXPECTED_JSON)
    text = (
        "<b>📦 Пример входного JSON-файла:</b>\n\n"
        f"<pre><code class=\"language-json\">{safe_json}</code></pre>"
    )
    await callback.message.edit_text(text, reply_markup=get_code_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "view_best_practice")
async def cb_view_best_practice(callback: CallbackQuery) -> None:
    safe_code = html.escape(BEST_PRACTICE_CODE)
    text = (
        "<b>⭐ Эталонная реализация (по стандартам 1С):</b>\n\n"
        "• Асинхронная отправка файла на сервер через временное хранилище\n"
        "• Корректное чтение через <code>ЧтениеJSON</code>\n"
        "• Однократное обновление списка без циклического автообновления\n\n"
        f"<pre><code class=\"language-bsl\">{safe_code}</code></pre>"
    )
    await callback.message.edit_text(text, reply_markup=get_code_back_keyboard(), parse_mode="HTML")
    await callback.answer()
