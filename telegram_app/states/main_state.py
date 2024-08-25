from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class MainState(StatesGroup):
    image = State()
    model = State()
