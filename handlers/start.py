from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

router = Router()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✍️ Практика: Напиши код сам (с автопроверкой)", callback_data="practice_list"),
        ],
        [
            InlineKeyboardButton(text="📖 Пошаговый разбор (5 шагов)", callback_data="lesson_1"),
        ],
        [
            InlineKeyboardButton(text="🧠 Интерактивный квиз", callback_data="quiz_start"),
            InlineKeyboardButton(text="🐛 Тренажер «Найди баг»", callback_data="bug_start"),
        ],
        [
            InlineKeyboardButton(text="📄 Исходный код со скриншота", callback_data="view_original_code"),
            InlineKeyboardButton(text="📦 Пример JSON-файла", callback_data="view_json"),
        ],
        [
            InlineKeyboardButton(text="⭐ Эталонный код (Best Practice)", callback_data="view_best_practice"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        "👋 <b>Привет! Я бот для изучения кода со скриншота 1С.</b>\n\n"
        "🎯 <b>Главная фишка:</b> режим практики, где вы пишете код сами прямо в сообщениях бота! "
        "Бот автоматически проверяет ваш ввод строчка за строчкой, указывает среду исполнения "
        "(<code>&amp;НаКлиенте</code> или <code>&amp;НаСервере</code>), подсвечивает ошибки, опечатки, "
        "пропущенные директивы и объясняет, что именно пошло не так.\n\n"
        "Выберите раздел для старта:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        "<b>📌 Доступные разделы:</b>\n\n"
        "• <b>✍️ Практика (Напиши код сам)</b> — вы вводите код по секциям со скриншота, "
        "бот моментально анализирует его и выдает диагностику ошибок по каждой строке.\n"
        "• <b>📖 Пошаговый разбор</b> — теория и разбор логики 1С шаг за шагом.\n"
        "• <b>🧠 Интерактивный квиз</b> — проверка знаний по механизмам 1С.\n"
        "• <b>🐛 Найди баг</b> — выявление архитектурных уязвимостей кода со скриншота.\n"
        "• <b>📄 Исходный код со скриншота</b> — полный текст без сокращений."
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    text = (
        "🏠 <b>Главное меню:</b>\n\n"
        "Выберите раздел:"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    await callback.answer()
