import os
import logging
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states import ParserSteps
from app.constants import COUNTRIES
from app.utils import file_reader
from app.utils.url_generator import generate_all_urls, generate_url
import app.utils.proxy_controller as proxy_controller
from app.services.xlsx_creator import get_new_xlsx_file_path
from aiogram.types import FSInputFile

from models import session_model

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(f'Привет, {message.from_user.full_name}! /n'
                         f'Введите страну для парсинга в формате ISO-2(код BY, RU, UA)!'
                         f'')
    await state.set_state(ParserSteps.choosing_country)


@router.message(ParserSteps.choosing_country)
async def country_chosen(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)

    if message.text.upper() not in COUNTRIES:
        await message.answer(f"\"{message.text}\" не выглядит как валидный код для страны!"
                             f"Введите название страны еще раз!")
        return

    kb = [
        [types.KeyboardButton(text="1 месяц")],
        [types.KeyboardButton(text="3 месяца")],
        [types.KeyboardButton(text="1 год")],
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.answer(f"Принято: {message.text} (код - {COUNTRIES.get(message.text.lower())}). Выберите период!",
                         reply_markup=keyboard)
    await state.set_state(ParserSteps.choosing_period)


@router.message(ParserSteps.choosing_period, F.text.in_(["1 месяц", "3 месяца", "1 год"]))
async def period_chosen(message: types.Message, state: FSMContext):
    await state.update_data(period=message.text)

    await message.answer(
        f"Отлично, теперь пришлите файл таблицы (.xlsx или .csv)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(ParserSteps.uploading_file)


@router.message(ParserSteps.uploading_file, F.document)
async def file_uploaded(message: types.Message, state: FSMContext, bot: Bot):
    file_name = message.document.file_name
    if not (file_name.endswith(".xlsx") or file_name.endswith(".csv")):
        await message.answer(f"Неверное расширение файла: {file_name}")
        return

    if not os.path.exists("downloads"):
        os.mkdir("downloads")

    file_path = os.path.join("downloads", f"{message.document.file_unique_id}_{file_name}")
    await bot.download(message.document, destination=file_path)
    logging.info(f"File downloaded to {file_path}")

    user_data = await state.get_data()

    await message.answer(
        f"✅ Все данные получены!\n"
        f"🌍 Страна: {user_data['country']}\n"
        f"📅 Период: {user_data['period']}\n"
        f"💾 Файл сохранен: {file_name}\n\n"
        "Начинаю обработку данных и запуск Selenium..."
    )

    proxy_controller.change_proxy_ip()

    try:
        session = session_model.Session()
        session.geo = user_data['country'].upper()
        session.period = user_data['period']
        session.start_keywords_file_path = file_path
        session.start_keywords = file_reader.get_keywords_from_file(session)
        session.urls = generate_all_urls(session)
        session.collect_keywords_and_value_pairs()
        session.collect_brand_keywords()
        session.compare_brands()
    except Exception as e:
        logging.error(f"error: {e}")

    file_path = session.create_csv(doc_id=message.document.file_unique_id)

    file_path = os.path.join("", file_path)
    if os.path.exists(file_path):
        # Создаем объект файла из файловой системы
        document = FSInputFile(file_path)
        await message.answer_document(
            document,
            caption=f"Вот ваш отчет Google Trends и список брендов!\n"
                    f"{session.brand_keywords}"
        )
        # Опционально: удалить файл после отправки, чтобы не захламлять корень
        # os.remove(file_path)
    else:
        await message.answer("Ошибка: файл не был сформирован.")

    # if len(urls) == 0:
    #     await message.answer("Ссылки не сформировались, возможно ПЕРВЫЫЙ столбец пустой")
    #     return


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("???")
