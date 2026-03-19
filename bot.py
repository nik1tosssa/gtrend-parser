import asyncio
import logging
from aiogram import Bot, Dispatcher
from selenium.webdriver.remote.webdriver import create_matches
from config_reader import config

# set logging
logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    logging.info(f"Bot started with token: {config.bot_token.get_secret_value()}")
    #
    #
    #
    #

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Shutting down')
