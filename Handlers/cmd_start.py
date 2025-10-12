from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart

router = Router()

@router.message(Command('start'))
async def cmd_start(message: types.Message):
    await message.answer(f'{message.text}')