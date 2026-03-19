from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f'Привет, {message.from_user.full_name}!'
                         f'')

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("???")