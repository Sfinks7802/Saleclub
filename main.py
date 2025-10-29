import asyncio
from aiogram import Dispatcher
from Handlers import (cmd_start, cq_nigger, cmd_menu, main_hand)
from Bot import bot


async def main():
    dp = Dispatcher()

    dp.include_routers(cmd_start.router, cq_nigger.router, cmd_menu.router, main_hand.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())