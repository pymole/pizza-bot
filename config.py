from communicators.telegram import TelegramCommunicator
from handler import PizzaOrderHandler
import os


communicator = TelegramCommunicator(
    PizzaOrderHandler(),
    os.environ['TELEGRAM_TOKEN']
)
