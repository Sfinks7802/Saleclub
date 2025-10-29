from aiogram import Router, types, F
from llm import analyze_reviews_with_gigachat, token
from get_reviews_from_wb import get_reviews_from_wb

router = Router()

@router.message(F.text)
async def cmd_start(message: types.Message):
    reviews = get_reviews_from_wb(message.text)[1]
    ans = analyze_reviews_with_gigachat(token=token, reviews=reviews)
    await message.answer(f'{ans}')