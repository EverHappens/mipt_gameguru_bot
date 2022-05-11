import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

BOT_TOKEN = '5382016281:AAEbvndupAYz-YsIageAiuzUANAJK2SY2F4'

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    name = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    await message.reply("Hi! This is Igromania news bot, delivering recent news on time!")


@dp.message_handler(commands=['help'])
async def send_help(message):
    await message.reply(
        "/start - Introduction/greeting\n/help - View commands\n/top - View top 5 relevant articles\n/search - Find top 5 articles on a search query")


@dp.message_handler(commands=['top'])
async def send_top(message):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://gameguru.ru/articles/') as response:
            HOST = 'https://gameguru.ru'
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.find_all('div', class_='short-news')
            news = []
            for item in items:
                news.append({
                    'text': item.find('a', class_='area-clickable').get_text(),
                    'link': HOST + item.find('a').get('href'),
                    'image': HOST + item.find('img').get('src')
                })
            await message.reply("Here's what I have found:")
            for item in news[:5]:
                await bot.send_photo(chat_id=message.from_user.id, photo=item['image'], caption=item['text']+'\n'+item['link'])

@dp.message_handler(commands=['search'])
async def send_search(message):
    await Form.name.set()
    await message.reply("Enter topic (write '/cancel' to stop the search):")

@dp.message_handler(state='*', commands=['cancel'])
async def handle_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply("Cancelled.")

@dp.message_handler(state=Form.name)
async def get_search_result(message: types.Message, state: FSMContext):
    await state.finish()
    search_text = message.text.replace(' ', '+')
    async with aiohttp.ClientSession() as session:
        async with session.get('https://gameguru.ru/articles/?search=' + search_text) as response:
            HOST = 'https://gameguru.ru'
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.find_all('div', class_='short-news')
            news = []
            for item in items:
                news.append({
                    'text': item.find('a', class_='area-clickable').get_text(),
                    'link': HOST + item.find('a').get('href'),
                    'image': HOST + item.find('img').get('src')
                })
            await message.reply("Here's what I have found:")
            for item in news[:5]:
                await bot.send_photo(chat_id=message.from_user.id, photo=item['image'], caption=item['text']+'\n'+item['link'])
            pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
