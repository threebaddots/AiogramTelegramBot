#!venv/bin/python
import logging
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from config import token


class Memory:

    def __init__(self):
        self.users = dict()

    def get_user(self, chat):
        if chat['id'] not in self.users:
            user_object = {
                'telegram_id': int(chat['id']),
                'balance': 0,
                'last_use': datetime.datetime.now()
            }
            for key in ['first_name', 'last_name', 'username', 'phone']:
                if key in chat:
                    user_object[key] = chat[key]
                else:
                    user_object[key] = None  # если я не получил эту информацию, то она None
            user = User.from_user_object(user_object=user_object)
            self.users[chat['id']] = user
        else:
            user = self.users[chat['id']]

        return user


class User:

    def __init__(self, user_object):
        self.data = user_object
        self.action = None

    @staticmethod
    def from_user_object(user_object):
        return User(user_object)


# Объект бота
bot = Bot(token=token)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
memory = Memory()


# Хэндлер на команду /reg
@dp.message_handler(commands="reg")
async def cmd_reg(message: types.Message):
    user = memory.get_user(message.chat)
    user.action = "name"
    await message.answer("Как тебя зовут?")


@dp.message_handler()
async def get_info(message: types.Message):
    user = memory.get_user(message.chat)
    if user.action == "name":
        user.data["first_name"] = message.text
        user.action = "surname"
        await message.answer("Какая у тебя фамилия?")
    elif user.action == "surname":
        user.data["second_name"] = message.text
        user.action = "age"
        await message.answer("Сколько тебе лет?")
    elif user.action == "age":
        if not message.text.isdigit():
            await message.answer("Цифрами, пожалуйста")
        else:
            user.data["age"] = int(message.text)
            user.action = "check"
            buttons = [
                types.InlineKeyboardButton(text="Да", callback_data="check_yes"),
                types.InlineKeyboardButton(text="Нет", callback_data="check_no")
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            ques = f"Тебе {str(user.data['age'])} лет, тебя зовут {user.data['first_name']} {user.data['second_name']}?"
            await message.answer(ques, reply_markup=keyboard)
    else:
        await message.answer("Напиши /reg")


@dp.callback_query_handler(Text(startswith="check_"))
async def get_check_value(call: types.CallbackQuery):
    if call.data.split("_")[1] == "yes":
        await call.message.answer("Запомню : )")
    else:
        await call.message.answer("Напиши /reg")


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
