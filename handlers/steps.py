from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from content.lessons import LESSONS

router = Router()

def get_lesson_keyboard(current_id: int) -> InlineKeyboardMarkup:
    total = len(LESSONS)
    nav_row = []

    if current_id > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"lesson_{current_id - 1}"))
    
    nav_row.append(InlineKeyboardButton(text=f"{current_id}/{total}", callback_data="noop"))
    
    if current_id < total:
        nav_row.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"lesson_{current_id + 1}"))

    keyboard = [
        nav_row,
        [
            InlineKeyboardButton(text="🧠 Проверить себя в Квизе", callback_data="quiz_start"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.callback_query(F.data.startswith("lesson_"))
async def cb_show_lesson(callback: CallbackQuery) -> None:
    lesson_id = int(callback.data.split("_")[1])
    lesson = next((item for item in LESSONS if item["id"] == lesson_id), None)
    
    if not lesson:
        await callback.answer("Урок не найден", show_alert=True)
        return

    text = lesson["content"]
    await callback.message.edit_text(
        text, 
        reply_markup=get_lesson_keyboard(lesson_id), 
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery) -> None:
    await callback.answer()
