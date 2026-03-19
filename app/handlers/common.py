import os
import logging
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states import ParserSteps

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(f'Привет, {message.from_user.full_name}! /n'
                         f'Введите страну для парсинга!'
                         f'')
    await state.set_state(ParserSteps.choosing_country)


@router.message(ParserSteps.choosing_country)
async def country_chosen(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    # TODO: country validation
    kb = [
        [types.KeyboardButton(text="1 месяц")],
        [types.KeyboardButton(text="3 месяца")],
        [types.KeyboardButton(text="1 год")],
    ]

    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    await message.answer(f"Принято: {message.text}. Выберите период!", reply_markup=keyboard)
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
    logging.basicConfig(level=logging.INFO)
    logging.info(f"File downloaded to {file_path}")

    user_data = await state.get_data()

    await message.answer(
        f"✅ Все данные получены!\n"
        f"🌍 Страна: {user_data['country']}\n"
        f"📅 Период: {user_data['period']}\n"
        f"💾 Файл сохранен: {file_name}\n\n"
        "Начинаю обработку данных и запуск Selenium..."
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("???")
