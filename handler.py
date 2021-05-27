from typing import Any, Optional
from transitions import Machine, State, EventData


class Handler:
    def handle(self, *args, **kwargs):
        raise NotImplementedError


class SkipAnswer(Exception):
    pass


class PizzaOrderState(State):

    def get_message(self, model):
        raise SkipAnswer()


class SizeQuestion(PizzaOrderState):
    def get_message(self, model):
        return 'Какую вы хотите пиццу? Большую или маленькую?'


class PaymentQuestion(PizzaOrderState):
    def get_message(self, model):
        return 'Как вы будете платить? Наличными или картой?'


class AcceptQuestion(PizzaOrderState):
    def get_message(self, model):
        return f'Вы хотите {model.size} пиццу, оплата - {model.payment}?'


class Thanks(PizzaOrderState):
    def get_message(self, model):
        return f'Спасибо за заказ'


class PizzaOrder:
    initial = PizzaOrderState('initial')
    size_question = SizeQuestion('size_question')
    payment_question = PaymentQuestion('payment_question')
    accept_question = AcceptQuestion('accept_question')
    thanks = Thanks('thanks')

    states = [
        size_question,
        payment_question,
        accept_question,
        thanks,
    ]

    def __init__(self):
        self.size: Optional[str] = None
        self.payment: Optional[str] = None
        machine = Machine(model=self,
                          states=PizzaOrder.states,
                          initial=PizzaOrder.initial,
                          send_event=True,
                          auto_transitions=False,
                          ignore_invalid_triggers=False,
                          )

        machine.add_transition('next', '*', PizzaOrder.size_question, conditions='is_start')
        machine.add_transition('next', PizzaOrder.size_question, PizzaOrder.payment_question, conditions='is_valid_size', before='set_size')
        machine.add_transition('next', PizzaOrder.payment_question, PizzaOrder.accept_question, conditions='is_valid_payment_type', before='set_payment')
        machine.add_transition('next', PizzaOrder.accept_question, PizzaOrder.thanks, conditions='is_yes')
        machine.add_transition('next', PizzaOrder.accept_question, PizzaOrder.size_question, conditions='is_no')
        self.machine = machine

    def set_size(self, event: EventData):
        self.size = event.kwargs['message']

    def set_payment(self, event: EventData):
        self.payment = event.kwargs['message']

    def is_start(self, event: EventData) -> bool:
        return event.kwargs.get('message') == '/start'

    def is_valid_size(self, event: EventData) -> bool:
        message = event.kwargs.get('message')
        return message and (message == 'большую' or message == 'маленькую')

    def is_valid_payment_type(self, event: EventData) -> bool:
        message = event.kwargs.get('message')
        return message and (message == 'картой' or message == 'наличными')

    def is_yes(self, event: EventData) -> bool:
        return event.kwargs.get('message') == 'да'

    def is_no(self, event: EventData) -> bool:
        return event.kwargs.get('message') == 'нет'


class PizzaOrderHandler(Handler):

    def __init__(self):
        self.orders: dict[Any, PizzaOrder] = {}

    def handle(self, user_id: Any, message: str) -> str:
        message = message.lower()

        try:
            order = self.orders[user_id]
        except KeyError:
            order = PizzaOrder()
            self.orders[user_id] = order

        order.next(message=message)
        answer = order.machine.get_state(order.state).get_message(order)
        return answer
