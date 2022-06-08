from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


no = KeyboardButton('Нет')
yes = KeyboardButton('Да')
go = KeyboardButton('Давай!')
connect = KeyboardButton('Начать общение')
anketa = KeyboardButton('Поехали!')

create = ReplyKeyboardMarkup(resize_keyboard = True).add(anketa)
talk = ReplyKeyboardMarkup(resize_keyboard = True).add(connect)
go = ReplyKeyboardMarkup(resize_keyboard = True).add(go)
yes_no = ReplyKeyboardMarkup(resize_keyboard = True).add(no,yes)


