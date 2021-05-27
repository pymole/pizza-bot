from handler import PizzaOrderHandler, SkipAnswer
import pytest


size_question = 'Какую вы хотите пиццу? Большую или маленькую?'
payment_question = 'Как вы будете платить? Наличными или картой?'
thanks = 'Спасибо за заказ'
user_id = 1


@pytest.fixture
def initial_handler():
    return PizzaOrderHandler()


@pytest.fixture(params=['/start'])
def size_handler(request, initial_handler):
    initial_handler.handle(user_id, request.param)
    return initial_handler


@pytest.fixture(params=['Большую', 'Маленькую'])
def payment_handler(request, size_handler):
    size_handler.handle(user_id, request.param)
    return size_handler


@pytest.fixture(params=['Картой', 'Наличными'])
def accept_handler(request, payment_handler):
    payment_handler.handle(user_id, request.param)
    return payment_handler


@pytest.fixture
def accept_question(accept_handler):
    return f'Вы хотите {accept_handler.orders[user_id].size} пиццу, оплата - {accept_handler.orders[user_id].payment}?'


@pytest.fixture(params=['Да', 'Нет'])
def thanks_handler(request, accept_handler):
    accept_handler.handle(user_id, request.param)
    return accept_handler


@pytest.mark.parametrize('handler', [
    pytest.lazy_fixture('initial_handler'),
    pytest.lazy_fixture('size_handler'),
    pytest.lazy_fixture('payment_handler'),
    pytest.lazy_fixture('accept_handler'),
    pytest.lazy_fixture('thanks_handler'),
])
def test_start(handler):
    """At any time user can start new order by /start message"""
    answer = handler.handle(user_id, '/start')
    assert answer == size_question


def test_start_stay(initial_handler):
    """Skip answer when user types any except /start command"""
    with pytest.raises(SkipAnswer):
        initial_handler.handle(user_id, '/random_command')


@pytest.mark.parametrize('size', ['Большую', 'Маленькую'])
def test_size_question(size, size_handler):
    """Select pizza size and answer payment question"""
    answer = size_handler.handle(user_id, size)
    assert answer == payment_question


def test_size_question_repeat(size_handler):
    """Repeat size question on invalid pizza size"""
    answer = size_handler.handle(user_id, 'Супер огромную величиной с дом')
    assert answer == size_question


@pytest.mark.parametrize('payment', ['Картой', 'Наличными'])
def test_payment_question(payment, size_handler, accept_question):
    """Select payment method and answer accept question"""
    answer = size_handler.handle(user_id, payment)
    assert answer == accept_question


def test_payment_question_repeat(payment_handler):
    """Repeat payment question on invalid payment type"""
    answer = payment_handler.handle(user_id, 'Космической пыльцой')
    assert answer == payment_question


def test_accept_question_yes(accept_handler):
    """Thanks to the user for new order"""
    answer = accept_handler.handle(user_id, 'Да')
    assert answer == thanks


def test_accept_question_restart_order(accept_handler):
    """Restart if something wrong in order"""
    answer = accept_handler.handle(user_id, 'Нет')
    assert answer == size_question


def test_accept_question_repeat(accept_handler, accept_question):
    """Repeat question accept question on invalid message"""
    answer = accept_handler.handle(user_id, 'Не знаю')
    assert answer == accept_question


@pytest.mark.parametrize('handler,repeat_question', [
    [pytest.lazy_fixture('size_handler'), size_question],
    [pytest.lazy_fixture('payment_handler'), payment_question],
    [pytest.lazy_fixture('accept_handler'), pytest.lazy_fixture('accept_question')],
])
def test_question_repeat_on_invalid_message(handler, repeat_question):
    answer = handler.handle(user_id, 'Случайные данные, которые не подходят ни под один вопрос')
    assert answer == repeat_question
