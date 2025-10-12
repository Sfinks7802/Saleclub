from aiogram import types, Router
from aiogram.filters import Command


router = Router()



def menu_kb():
    buttons = [
        [types.InlineKeyboardButton(text="nigger", callback_data="nigger")]
               ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

@router.message(Command('menu'))
async def get_menu(message: types.Message):
    await message.answer('Выберите категорию', reply_markup=menu_kb())