import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram import types
import buttons as nav
import os
import csv


BOT_TOKEN = "5423997060:AAHG2ecBeY-0lKwU-ma6H7W_MRyfLOQ2u_U"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    fullname = State()
    city = State()
    position = State()
    hobby = State()


@dp.message_handler()
async def bot_message(message: types.Message):
    if message.text == '/start':
        await message.reply(
            "Приветствую\nКаждую неделю я буду предлагать тебе для встречи интересного человека, "
            "случайно выбранного среди других участников сообщества."
            "Для старта ответь на несколько вопросов и прочитай короткую инструкцию. ", reply_markup=nav.create)
    elif message.text == 'Поехали!':
        try:
            conn = sqlite3.connect("project.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM `users` WHERE `telegram`=?", [message.from_user.username], )
            result = cursor.fetchall()
            conn.commit()

            if result == []:
                await Form.fullname.set()
                await bot.send_message(message.from_user.id, "Напиши Имя и Фамилию ")

                @dp.message_handler(state=Form.fullname)
                async def process_name(message: types.Message, state: FSMContext):
                    async with state.proxy() as data:
                        data['fullname'] = message.text

                    await Form.next()
                    await message.reply("Напиши свой город")

                @dp.message_handler(state=Form.city)
                async def process_city(message: types.Message, state: FSMContext):
                    async with state.proxy() as data:
                        data['city'] = message.text
                    await Form.next()
                    await message.reply(" Напиши свою должность/роль в компании\nПример: менеджер проектов")

                @dp.message_handler(state=Form.position)
                async def process_work(message: types.Message, state: FSMContext):
                    async with state.proxy() as data:
                        data['position'] = message.text
                    await Form.next()
                    await message.reply("Чем ты можешь быть полезен своему собеседнику?")

                @dp.message_handler(state=Form.hobby)
                async def process_gender(message: types.Message, state: FSMContext):
                    async with state.proxy() as data:
                        data['hobby'] = message.text
                        username = message.from_user.username
                        try:
                            cursor.execute(
                                "INSERT INTO `users` (`full_name`, `city`, `position`, `hobby`, `telegram`) VALUES (?, ?, ?, ?, ?)",
                                (data['fullname'],
                                 data['city'],
                                 data['position'],
                                 data['hobby'],
                                 str(username)
                                 ))
                            await bot.send_message(
                                message.chat.id, f'Супер! Твой профиль выглядит так:\nИмя: {data["fullname"]}\n'
                                                 f'Город: {data["city"]}\n'
                                                 f'Занятие: {data["position"]}\n'
                                                 f'О себе: {data["hobby"]}', reply_markup=nav.talk)
                            conn.commit()
                        except:
                            await bot.send_message(message.chat.id, 'Sorry, something went wrong1')
                        finally:
                            if (conn):
                                conn.close()
                        await state.finish()
            else:
                await bot.send_message(message.chat.id,
                                       text='У тебя уже есть анкета, можешь приступать к поиску напарника!',
                                       reply_markup=nav.talk)
        except:
            await bot.send_message(message.chat.id, text='Sorry, something went wrong2')

    elif message.text == 'Начать общение':
        username = str(message.from_user.username)
        conn = sqlite3.connect("project.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM `users` ORDER BY RANDOM() LIMIT 1")
        partner = cursor.fetchall()
        for row in partner:
            id2 = row[0]
            name = row[1]
            city = row[2]
            work = row[3]
            hobby = row[4]
            tg2 = row[5]
        if partner == [] or tg2 == username:
            await message.reply('Не смогли найти партнера, заходи попозже')
        else:
            cursor.execute("SELECT * FROM `meetings` WHERE `username1` LIKE ? AND `username2` LIKE ?", (username, tg2))
            check1 = cursor.fetchall()
            cursor.execute("SELECT * FROM `meetings` WHERE `username1` LIKE ? AND `username2` LIKE ?", (tg2, username))
            check2 = cursor.fetchall()

            if check2 == check1 == []:
                await bot.send_message(
                    message.chat.id, text=f'Я нашел тебе напарника. Это {name}'
                                          f'\nГород: {city}'
                                          f'\nЗанятие:{work}'
                                          f'\nО себе:{hobby}'
                                          f'\nВот его телеграм:@{tg2}'
                                          '\n\nНапиши напарнику, и договоритесь о времени встречи или видеозвонка.', reply_markup=nav.go
                )
                cursor.execute("INSERT INTO `meetings`(`username1`,`username2`) VALUES (?,?)", (username, tg2))
                conn.commit()
                conn.close()
                for seconds in range(5 - 1, -1, -1):
                    await asyncio.sleep(1)
                    if seconds == 0:
                        await bot.send_message(chat_id=message.chat.id,
                                               text=f'👋🏻Привет!\nПомнишь, я давал тебе напарника @{tg2}?',
                                               reply_markup=nav.yes_no)

            else:
                await message.reply('Не смогли найти партнера, заходи попозже')
    elif message.text == 'Давай!':
        await message.reply('Не откладывай, договорись о встрече сразу🙂', reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Нет':
        await message.reply(f'Спасибо за отзыв!', reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Да':
        await message.reply(f'Спасибо за отзыв!', reply_markup=types.ReplyKeyboardRemove())

conn = sqlite3.connect("project.db")
cursor = conn.cursor()
cursor.execute("select * from users")
with open("users.csv", "w") as csv_file:
    csv_writer = csv.writer(csv_file, delimiter="\t")
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)

dirpath = os.getcwd() + "/users.csv"

if __name__ == '__main__':
    executor.start_polling(dp)
