from aiogram import Bot, Dispatcher, executor, types

from communicators import Communicator
from handler import Handler, SkipAnswer


class TelegramCommunicator(Communicator):
    def __init__(self, handler: Handler, token: str):
        self.token = token
        self.handler = handler

        bot = Bot(token=token)
        self.bot = bot

        dispatcher = Dispatcher(bot)
        dispatcher.register_message_handler(self.answer)

        self.dispatcher = dispatcher

    def start(self):
        executor.start_polling(self.dispatcher, skip_updates=True)

    async def answer(self, message: types.Message):
        try:
            answer = self.handler.handle(message.from_user.id, message.text)
        except SkipAnswer:
            pass
        else:
            await message.answer(answer)
