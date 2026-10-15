from typing import Dict, Any
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from content.questions import QUIZ_QUESTIONS

router = Router()

user_quiz_state: Dict[int, Dict[str, Any]] = {}

def get_question_keyboard(q_index: int) -> InlineKeyboardMarkup:
    q = QUIZ_QUESTIONS[q_index]
    buttons = []
    
    for idx, opt in enumerate(q["options"]):
        letter = chr(65 + idx)  # A, B, C, D
        buttons.append([
            InlineKeyboardButton(
                text=f"{letter}) {opt}", 
                callback_data=f"qans_{q_index}_{idx}"
            )
        ])
        
    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(F.data == "quiz_start")
async def cb_quiz_start(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user_quiz_state[user_id] = {"index": 0, "score": 0}
    
    await show_question(callback, 0)
    await callback.answer()

async def show_question(callback: CallbackQuery, q_index: int) -> None:
    total = len(QUIZ_QUESTIONS)
    q = QUIZ_QUESTIONS[q_index]
    
    text = (
        f"🎯 <b>Вопрос {q_index + 1} из {total}:</b>\n\n"
        f"{q['question']}\n\n"
        "<i>Выбери один из вариантов ответа:</i>"
    )
    await callback.message.edit_text(
        text, 
        reply_markup=get_question_keyboard(q_index), 
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("qans_"))
async def cb_question_answer(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    parts = callback.data.split("_")
    q_index = int(parts[1])
    selected_idx = int(parts[2])
    
    state = user_quiz_state.get(user_id, {"index": q_index, "score": 0})
    q = QUIZ_QUESTIONS[q_index]
    is_correct = (selected_idx == q["correct_index"])
    
    if is_correct:
        state["score"] += 1
        result_header = "✅ <b>Правильно!</b>\n\n"
    else:
        correct_letter = chr(65 + q["correct_index"])
        correct_text = q["options"][q["correct_index"]]
        result_header = (
            f"❌ <b>Неправильно!</b>\n"
            f"Правильный ответ: <b>{correct_letter}) {correct_text}</b>\n\n"
        )
        
    text = (
        f"{result_header}"
        f"{q['explanation']}"
    )
    
    total = len(QUIZ_QUESTIONS)
    next_index = q_index + 1
    state["index"] = next_index
    user_quiz_state[user_id] = state
    
    buttons = []
    if next_index < total:
        buttons.append([
            InlineKeyboardButton(text="Следующий вопрос ➡️", callback_data=f"qnext_{next_index}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="📊 Посмотреть итоги теста", callback_data="quiz_finish")
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

@router.callback_query(F.data.startswith("qnext_"))
async def cb_question_next(callback: CallbackQuery) -> None:
    next_index = int(callback.data.split("_")[1])
    await show_question(callback, next_index)
    await callback.answer()

@router.callback_query(F.data == "quiz_finish")
async def cb_quiz_finish(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    state = user_quiz_state.get(user_id, {"index": len(QUIZ_QUESTIONS), "score": 0})
    score = state["score"]
    total = len(QUIZ_QUESTIONS)
    
    percentage = int((score / total) * 100)
    
    if score == total:
        verdict = "🏆 <b>Великолепно! 100% результат!</b> Ты отлично разбираешься в тонкостях этого кода 1С!"
    elif score >= 4:
        verdict = "👍 <b>Хороший результат!</b> Основные концепции усвоены, но стоит обратить внимание на тонкости клиента и сервера."
    else:
        verdict = "📚 <b>Нужно повторить!</b> Рекомендуем пройти «Пошаговый разбор», чтобы детально изучить архитектуру 1С."

    text = (
        f"🏁 <b>Тестирование завершено!</b>\n\n"
        f"Твой счет: <b>{score} из {total}</b> ({percentage}%)\n\n"
        f"{verdict}"
    )
    
    buttons = [
        [
            InlineKeyboardButton(text="🔄 Пройти тест снова", callback_data="quiz_start"),
            InlineKeyboardButton(text="🐛 Тренажер «Найди баг»", callback_data="bug_start")
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
