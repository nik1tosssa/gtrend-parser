from aiogram.fsm.state import StatesGroup, State

class ParserSteps(StatesGroup):
    choosing_country = State()
    choosing_period = State()
    uploading_file = State()