from aiogram import Router, types, F


router = Router()


@router.callback_query(F.data == 'nigger')
async def nigger(callback: types.CallbackQuery):
    await callback.message.answer('sam ty nigger')
    await callback.answer()