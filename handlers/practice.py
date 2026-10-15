import html
from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from content.practice_tasks import PRACTICE_SECTIONS
from engine.code_checker import check_code_submission

router = Router()

class PracticeState(StatesGroup):
    waiting_for_code = State()

def get_section_keyboard(sec_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="💡 Подсказка", callback_data=f"prac_hint_{sec_id}"),
            InlineKeyboardButton(text="👀 Показать код со скриншота", callback_data=f"prac_reveal_{sec_id}"),
        ],
        [
            InlineKeyboardButton(text="⏭ Пропустить секцию", callback_data=f"prac_skip_{sec_id}"),
            InlineKeyboardButton(text="📋 К списку секций", callback_data="practice_list"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_sections_list_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for s in PRACTICE_SECTIONS:
        btn_text = f"Секция {s['id']}: {s['title'].split(':')[1].strip()}"
        buttons.append([
            InlineKeyboardButton(text=btn_text, callback_data=f"prac_start_{s['id']}")
        ])
    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "practice_list")
async def cb_practice_list(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    text = (
        "✍️ <b>Тренажер написания кода 1С со скриншота:</b>\n\n"
        "Вы пишете код прямо в чат — бот автоматически анализирует текст, "
        "указывает контекст выполнения (<code>&amp;НаКлиенте</code> / <code>&amp;НаСервере</code>) "
        "и объясняет каждую ошибку.\n\n"
        "Выберите секцию для тренировки:"
    )
    await callback.message.edit_text(text, reply_markup=get_sections_list_keyboard(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("prac_start_"))
async def cb_practice_start_section(callback: CallbackQuery, state: FSMContext) -> None:
    sec_id = int(callback.data.split("_")[2])
    await prompt_section(callback.message, state, sec_id, is_edit=True)
    await callback.answer()

async def prompt_section(message: Message, state: FSMContext, sec_id: int, is_edit: bool = False) -> None:
    sec = next((s for s in PRACTICE_SECTIONS if s["id"] == sec_id), None)
    if not sec:
        await message.answer("Секция не найдена.")
        return

    await state.set_state(PracticeState.waiting_for_code)
    await state.update_data(current_section_id=sec_id)

    total_sec = len(PRACTICE_SECTIONS)
    text = (
        f"✍️ <b>{sec['title']} (Секция {sec['id']} из {total_sec})</b>\n\n"
        f"🌐 <b>Среда выполнения:</b> <code>{sec['env_name']}</code>\n"
        f"ℹ️ <i>{sec['env_desc']}</i>\n\n"
        f"📝 <b>Что нужно написать:</b>\n"
        f"{sec['task_desc']}\n\n"
        "👇 <b>Напишите и отправьте код ответным сообщением:</b>"
    )

    if is_edit:
        await message.edit_text(text, reply_markup=get_section_keyboard(sec_id), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=get_section_keyboard(sec_id), parse_mode="HTML")

@router.callback_query(F.data.startswith("prac_hint_"))
async def cb_practice_hint(callback: CallbackQuery) -> None:
    sec_id = int(callback.data.split("_")[2])
    sec = next((s for s in PRACTICE_SECTIONS if s["id"] == sec_id), None)
    if sec:
        await callback.answer("Подсказка показана!", show_alert=False)
        await callback.message.answer(sec["hint"], parse_mode="HTML")
    else:
        await callback.answer("Секция не найдена.", show_alert=True)

@router.callback_query(F.data.startswith("prac_reveal_"))
async def cb_practice_reveal(callback: CallbackQuery) -> None:
    sec_id = int(callback.data.split("_")[2])
    sec = next((s for s in PRACTICE_SECTIONS if s["id"] == sec_id), None)
    if sec:
        escaped_code = html.escape(sec["target_code"])
        text = (
            f"👀 <b>Код со скриншота для секции {sec_id}:</b>\n\n"
            f"<pre><code class=\"language-bsl\">{escaped_code}</code></pre>\n\n"
            "Попробуйте набрать его самостоятельно по памяти для тренировки!"
        )
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()
    else:
        await callback.answer("Секция не найдена.", show_alert=True)

@router.callback_query(F.data.startswith("prac_skip_"))
async def cb_practice_skip(callback: CallbackQuery, state: FSMContext) -> None:
    sec_id = int(callback.data.split("_")[2])
    next_id = sec_id + 1
    if next_id <= len(PRACTICE_SECTIONS):
        await prompt_section(callback.message, state, next_id, is_edit=True)
    else:
        await cb_practice_list(callback, state)
    await callback.answer()

@router.message(PracticeState.waiting_for_code)
async def handle_practice_code_submission(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    sec_id = data.get("current_section_id", 1)
    sec = next((s for s in PRACTICE_SECTIONS if s["id"] == sec_id), PRACTICE_SECTIONS[0])

    user_code = message.text or ""
    result = check_code_submission(
        user_code=user_code,
        expected_code=sec["target_code"],
        env_name=sec["env_name"],
        env_desc=sec["env_desc"]
    )

    if result["is_correct"]:
        next_sec_id = sec_id + 1
        buttons = []
        if next_sec_id <= len(PRACTICE_SECTIONS):
            buttons.append([
                InlineKeyboardButton(text=f"Перейти к секции {next_sec_id} ➡️", callback_data=f"prac_start_{next_sec_id}")
            ])
        else:
            buttons.append([
                InlineKeyboardButton(text="🎓 Вы прошли все секции! К списку", callback_data="practice_list")
            ])
        buttons.append([
            InlineKeyboardButton(text="🔄 Написать еще раз для закрепления", callback_data=f"prac_start_{sec_id}"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ])

        reply_text = (
            f"🎉 <b>ИДЕАЛЬНО! Точность: 100%</b>\n\n"
            f"Ваш код полностью совпадает со скриншотом!\n\n"
            f"🌐 <b>Среда:</b> <code>{sec['env_name']}</code> отработана без ошибок."
        )
        await state.clear()
        await message.answer(reply_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    else:
        # Errors detected
        errors_list = []
        for idx, err in enumerate(result["errors"][:5], 1):  # show top 5 errors
            if err["type"] == "mismatch":
                err_text = (
                    f"<b>Ошибка #{idx}</b> (строка {err.get('user_line_no', '?')}):\n"
                    f"Ваш код: <code>{html.escape(err['user_line'])}</code>\n"
                    f"Ожидалось: <code>{html.escape(err['expected_line'])}</code>\n"
                    f"👉 <i>{err['message']}</i>"
                )
            elif err["type"] == "missing":
                err_text = (
                    f"<b>Ошибка #{idx} (пропуск строки):</b>\n"
                    f"Ожидалась строка со скриншота: <code>{html.escape(err['expected_line'])}</code>\n"
                    f"👉 <i>{err['message']}</i>"
                )
            elif err["type"] == "extra":
                err_text = (
                    f"<b>Ошибка #{idx} (лишняя строка {err.get('user_line_no', '?')}):</b>\n"
                    f"Вы написали: <code>{html.escape(err['user_line'])}</code>\n"
                    f"👉 <i>{err['message']}</i>"
                )
            else:
                err_text = f"<b>Ошибка #{idx}:</b> {err['message']}"
            errors_list.append(err_text)

        formatted_errors = "\n\n".join(errors_list)
        total_err_count = len(result["errors"])
        more_note = f"\n\n<i>(и еще {total_err_count - 5} расхождений...)</i>" if total_err_count > 5 else ""

        reply_text = (
            f"❌ <b>ОБНАРУЖЕНЫ ОШИБКИ В КОДЕ:</b>\n\n"
            f"🌐 <b>Среда / Контекст:</b> <code>{sec['env_name']}</code>\n"
            f"📊 <b>Точность совпадения:</b> {result['accuracy']}%\n\n"
            f"{formatted_errors}{more_note}\n\n"
            "-------------------------\n"
            "👇 <b>Исправьте код и отправьте его снова:</b>"
        )
        await message.answer(reply_text, reply_markup=get_section_keyboard(sec_id), parse_mode="HTML")
