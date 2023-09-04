from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from config import AUTH_USERS
from keyboards import start_kb


async def check_user(message: Message):
    if message.from_id not in AUTH_USERS:
        await message.answer('❌ Доступ запрещён')
        return False
    return True


async def check_cancel(message: Message, state: FSMContext):
    if message.text == '❌ Отмена':
        await state.finish()
        await message.answer(
            '❌ Операция отменена',
            reply_markup=start_kb
        )
        return True
    return False


async def check_task(message: Message, state: FSMContext):
    task = message.text.split(', ')
    if len(task) != 4:
        await message.answer(
            '❌ Некорректный ввод',
            reply_markup=start_kb
        )
        return None
    return task


async def make_reply(db_data: tuple) -> str:
    if not db_data:
        reply = '❌ Нет задач!'
    else:
        tasks = []
        for task in db_data:
            string = (
                f'🔸 {task[0]} | {task[1]}, '
                f'{task[2]}, {task[3]}, {task[4]}'
            )
            tasks.append(string)
            reply = '\n'.join(tasks)
    return reply
