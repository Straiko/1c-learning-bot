from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

router = Router()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📖 Пошаговый разбор (5 шагов)", callback_data="lesson_1"),
        ],
        [
            InlineKeyboardButton(text="🧠 Интерактивный тест (Квиз)", callback_data="quiz_start"),
            InlineKeyboardButton(text="🐛 Тренажер «Найди баг»", callback_data="bug_start"),
        ],
        [
            InlineKeyboardButton(text="📄 Исходный код 1С", callback_data="view_original_code"),
            InlineKeyboardButton(text="📦 Пример JSON-файла", callback_data="view_json"),
        ],
        [
            InlineKeyboardButton(text="⭐ Эталонный код (Best Practice)", callback_data="view_best_practice"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = (
        "👋 <b>Привет! Я бот для быстрого изучения кода 1С:Предприятие.</b>\n\n"
        "Мы разберем код из твоего скриншота:\n"
        "• Клиент-серверное взаимодействие (<code>&amp;НаКлиенте</code> / <code>&amp;НаСервере</code>)\n"
        "• Асинхронный диалог выбора файла (<code>ОписаниеОповещения</code>)\n"
        "• Парсинг JSON и структуры данных в 1С 8.3\n"
        "• Поиск и создание элементов справочника (<code>СправочникОбъект</code> vs <code>Ссылка</code>)\n"
        "• Критические ошибки и подводные камни, которые любят спрашивать на собеседованиях!\n\n"
        "Выбери, с чего начать:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "<b>📌 Доступные разделы:</b>\n\n"
        "• <b>Пошаговый разбор</b> — 5 последовательных уроков с объяснениями каждой строки.\n"
        "• <b>Квиз</b> — 6 тестовых вопросов с моментальной проверкой и разъяснениями.\n"
        "• <b>Найди баг</b> — практический тренажер на поиск архитектурных ошибок 1С.\n"
        "• <b>Исходный / Эталонный код</b> — сравнение исходника и профессионального варианта."
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery) -> None:
    text = (
        "🏠 <b>Главное меню:</b>\n\n"
        "Выбери нужный раздел обучения:"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    await callback.answer()
