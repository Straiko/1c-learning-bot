from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from content.bug_trainer import BUG_CASES

router = Router()

user_bug_state: Dict[int, Dict[str, Any]] = {}

def get_bug_keyboard(case_idx: int) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🐛 Да, здесь есть баг!", callback_data=f"bans_{case_idx}_yes"),
            InlineKeyboardButton(text="✅ Нет, код корректен", callback_data=f"bans_{case_idx}_no"),
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "bug_start")
async def cb_bug_start(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_bug_state[user_id] = {"index": 0, "score": 0}
    await show_bug_case(callback, 0)
    await callback.answer()

async def show_bug_case(callback: CallbackQuery, case_idx: int) -> None:
    total = len(BUG_CASES)
    case = BUG_CASES[case_idx]
    
    text = (
        f"🔍 <b>Ситуация {case_idx + 1} из {total}:</b>\n"
        f"<b>{case['title']}</b>\n\n"
        f"<pre><code>{case['code_snippet']}</code></pre>\n\n"
        "<i>Есть ли в этом фрагменте ошибка или критический архитектурный дефект?</i>"
    )
    await callback.message.edit_text(
        text, 
        reply_markup=get_bug_keyboard(case_idx), 
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("bans_"))
async def cb_bug_answer(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    case_idx = int(parts[1])
    user_choice = (parts[2] == "yes")
    
    state = user_bug_state.get(user_id, {"index": case_idx, "score": 0})
    case = BUG_CASES[case_idx]
    is_correct = (user_choice == case["is_bug"])
    
    if is_correct:
        state["score"] += 1
        verdict = "🎯 <b>В точку! Твоя оценка верна.</b>\n\n"
    else:
        verdict = "❌ <b>Мимо!</b>\n\n"
        
    text = (
        f"{verdict}"
        f"{case['explanation']}"
    )
    
    total = len(BUG_CASES)
    next_idx = case_idx + 1
    state["index"] = next_idx
    user_bug_state[user_id] = state
    
    buttons = []
    if next_idx < total:
        buttons.append([
            InlineKeyboardButton(text="Следующая ситуация ➡️", callback_data=f"bnext_{next_idx}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="🎉 Итоги тренажера", callback_data="bug_finish")
        ])
    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    
    await callback.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("bnext_"))
async def cb_bug_next(callback: CallbackQuery) -> None:
    next_idx = int(callback.data.split("_")[1])
    await show_bug_case(callback, next_idx)
    await callback.answer()

@router.callback_query(F.data == "bug_finish")
async def cb_bug_finish(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = user_bug_state.get(user_id, {"index": len(BUG_CASES), "score": 0})
    score = state["score"]
    total = len(BUG_CASES)
    
    text = (
        f"🏁 <b>Тренажер завершен!</b>\n\n"
        f"Ты правильно определил <b>{score} из {total}</b> ситуаций.\n\n"
        "Теперь ты знаешь все уязвимости кода со скриншота!"
    )
    
    buttons = [
        [
            InlineKeyboardButton(text="⭐ Посмотреть эталонный код", callback_data="view_best_practice"),
            InlineKeyboardButton(text="🔄 Повторить тренажер", callback_data="bug_start")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    await callback.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), 
        parse_mode="HTML"
    )
    await callback.answer()
