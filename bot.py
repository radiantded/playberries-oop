from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import Message
from aiogram.utils.executor import start_polling
from telegram.fsms import CreateTaskFSM, DeleteTaskFSM, StartTaskFSM
from telegram.keyboards import cancel_kb, launch_que_kb, start_kb

from config import BOT_TOKEN
from database.db import Database
from scrapper.datacls import Task
from scrapper.playberries import script
from telegram.utils import check_cancel, check_task, check_user, make_reply


storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(state=StartTaskFSM.start)
async def register_tasks(message: Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        await data['reply'].delete()

    if not await check_user(message):
        return

    if await check_cancel(message, state):
        return

    task_id = message.text
    async with Database() as base:
        task = await base.get_one(task_id)
    if not task:
        await message.answer(
            '❌ Нет задач с таким id',
            reply_markup=start_kb)
        await state.finish()
        return

    async with state.proxy() as data:
        data['que'] = task
        confirm = await message.answer(
            f'✅ Задача готова к запуску:\n'
            f'🔸 {task[0]} | {task[1]}, '
            f'{task[2]}, {task[3]}, {task[4]}',
            reply_markup=launch_que_kb
        )
        reply = await message.answer('⚙️ Подтвердите запуск задачи')
        data['reply'] = reply
        data['confirm'] = confirm

    await StartTaskFSM.next()


@dp.message_handler(state=DeleteTaskFSM.delete)
async def delete_tasks(message: Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        await data['reply'].delete()

    if not await check_user(message):
        return

    if await check_cancel(message, state):
        return

    task_id = message.text
    async with Database() as base:
        await base.delete(task_id)
    await state.finish()
    await message.answer(
        f'✅ Задача 🔸 {task_id} удалена',
        reply_markup=start_kb
    )


@dp.message_handler(state=StartTaskFSM.finish)
async def que_handler(message: Message, state: FSMContext):
    await message.delete()
    if not await check_user(message):
        return

    async with state.proxy() as data:
        await data['reply'].delete()
        await data['confirm'].delete()
        task = data['que']

    if await check_cancel(message, state):
        return

    if message.text == '✅ Запустить':
        await message.answer(
            f'🚀 Запущена задача:\n'
            f'🔸 {task[0]} | {task[1]}, '
            f'{task[2]}, {task[3]}, {task[4]}',
            reply_markup=start_kb)
        await state.finish()
        result = await script(Task(*task))
        if not result:
            await message.answer(
                f'❌ Задача завершилась с ошибкой:\n'
                f'🔸 {task[0]} | {task[1]}, '
                f'{task[2]}, {task[3]}, {task[4]}',
                reply_markup=start_kb
            )
        else:
            await message.answer(
                f'✅ Задача завершена:\n'
                f'🔸 {task[0]} | {task[1]}, '
                f'{task[2]}, {task[3]}, {task[4]}',
                reply_markup=start_kb
            )


@dp.message_handler(state=CreateTaskFSM.create)
async def create_task(message: Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        try:
            await data['reply'].delete()
        except:
            pass

    if not await check_user(message):
        return

    if await check_cancel(message, state):
        return

    task = await check_task(message, state)
    if not task:
        return

    async with Database() as base:
        task_id = await base.add(tuple(task))
    await message.answer(
        f'✅ Добавлена задача:\n'
        f'🔸 {task_id[0]} | {task[0]}, '
        f'{task[1]}, {task[2]}, {task[3]}',
        reply_markup=start_kb
    )
    await state.finish()


@dp.message_handler(text='🔶 Все задачи')
async def get_all_tasks(message: Message):
    await message.delete()
    if not await check_user(message):
        return

    async with Database() as base:
        db_data = await base.get_all()
    reply = await make_reply(db_data)
    await message.answer(
        reply,
        reply_markup=start_kb
    )


@dp.message_handler(text='⚙️ Создать задачу')
async def get_task_params(message: Message, state: FSMContext):
    await message.delete()
    if not await check_user(message):
        return

    async with state.proxy() as data:
        data['reply'] = await message.answer(
            ('⚙️ Введите параметры задачи: <запрос>, '
             '<артикул>, <повторы>, <корзина>')
        )
    await CreateTaskFSM.create.set()


@dp.message_handler(text='❌ Удалить задачу')
async def delete_task(message: Message, state: FSMContext):
    await message.delete()
    if not await check_user(message):
        return

    async with state.proxy() as data:
        data['reply'] = await message.answer(
            '⚙️ Введите id задачи для удаления',
            reply_markup=cancel_kb
        )
    await DeleteTaskFSM.delete.set()


@dp.message_handler(text='🚀 Запустить задачу')
async def create_que(message: Message, state: FSMContext):
    await message.delete()
    if not await check_user(message):
        return

    async with state.proxy() as data:
        data['reply'] = await message.answer(
            '⚙️ Введите id задачи для запуска',
            reply_markup=cancel_kb
        )
    await StartTaskFSM.start.set()


@dp.message_handler(commands=['start'])
async def start(message: Message):
    print(message.from_id)
    await message.delete()
    if not await check_user(message):
        return

    await message.answer(
        '☀️ Добро пожаловать!',
        reply_markup=start_kb
    )


if __name__ == '__main__':
    start_polling(dp, timeout=10000, skip_updates=True)
