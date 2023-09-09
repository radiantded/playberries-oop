from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateTaskFSM(StatesGroup):
    create = State()


class StartTaskFSM(StatesGroup):
    start = State()
    finish = State()


class DeleteTaskFSM(StatesGroup):
    delete = State()
