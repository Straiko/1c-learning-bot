from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

router = Router()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🎯 Общий тест: написать весь код (1 Total)", callback_data="prac_start_5"),
        ],
        [
            InlineKeyboardButton(text="✍️ Практика по частям (Секции 1-4)", callback_data="practice_list"),
        ],
        [
            InlineKeyboardButton(text="📄 Код со скриншота (1 в 1)", callback_data="view_original_code"),
            InlineKeyboardButton(text="📦 Пример JSON-файла", callback_data="view_json"),
        ],
        [
            InlineKeyboardButton(text="🧠 Проверочный квиз", callback_data="quiz_start"),
            InlineKeyboardButton(text="🐛 Разбор ошибок со скриншота", callback_data="bug_start"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        "👋 <b>Привет! Я бот для изучения и воспроизведения кода 1С со скриншота.</b>\n\n"
        "В боте используется <b>строго один код — оригинал со скриншота</b> (без сторонних вариантов и правок).\n\n"
        "🎯 <b>Режим проверки кода:</b>\n"
        "Вы можете написать <b>весь код целиком (1 Total)</b> или потренироваться по частям.\n"
        "Бот автоматически проверит ввод строка за строкой, укажет среду (<code>&amp;НаКлиенте</code> или <code>&amp;НаСервере</code>) "
        "и объяснит, где допущены неточности.\n\n"
        "Выберите режим:"
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        "<b>📌 Разделы бота:</b>\n\n"
        "• <b>🎯 Общий тест (1 Total)</b> — написать обе процедуры целиком со скриншота с автопроверкой всех строк.\n"
        "• <b>✍️ Практика по частям</b> — тренировка по 4 коротким блокам (диалог, чтение JSON, поиск, запись).\n"
        "• <b>📄 Код со скриншота</b> — посмотреть точный текст оригинала.\n"
        "• <b>📦 Пример JSON</b> — структура входного файла.\n"
        "• <b>🧠 Квиз / 🐛 Ошибки</b> — закрепление теории."
    )
    await message.answer(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    text = (
        "🏠 <b>Главное меню:</b>\n\n"
        "Выберите нужный режим:"
    )
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    await callback.answer()
