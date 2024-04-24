import pytest

from telegrinder.bot.cute_types.message import MessageCute
from telegrinder.bot.dispatch.context import Context
from telegrinder.bot.dispatch.handler.abc import ABCHandler
from telegrinder.bot.dispatch.handler.func import FuncHandler
from telegrinder.bot.dispatch.middleware.abc import ABCMiddleware
from telegrinder.bot.dispatch.return_manager.message import MessageReturnManager
from telegrinder.bot.dispatch.view.abc import BaseStateView
from telegrinder.bot.rules.abc import ABCRule


class SomeView(BaseStateView[MessageCute]):
    def __init__(self) -> None:
        self.middlewares: list[ABCMiddleware[MessageCute]] = []
        self.auto_rules: list[ABCRule[MessageCute]] = []
        self.handlers: list[ABCHandler[MessageCute]] = []
        self.return_manager: MessageReturnManager = MessageReturnManager()

    async def get_state_key(self, event: MessageCute) -> int | None:
        return event.message_id


@pytest.mark.asyncio()
async def test_register_middleware():
    view = SomeView()

    @view.register_middleware(one=1, two=2)
    class SomeMiddleware(ABCMiddleware[MessageCute]):
        def __init__(self, one: int, two: int) -> None:
            self.one = one
            self.two = two

        async def pre(self, event: MessageCute) -> None:
            pass
    
    assert len(view.middlewares) == 1
    assert isinstance(view.middlewares[0], SomeMiddleware)
    assert view.middlewares[0].one == 1
    assert view.middlewares[0].two == 2


@pytest.mark.asyncio()
async def test_register_func_handler():
    view = SomeView()

    @view()
    async def func_handler(event: MessageCute) -> None:
        pass

    assert len(view.handlers) == 1
    assert isinstance(view.handlers[0], FuncHandler)
    assert view.handlers[0] == func_handler
    assert view.handlers[0].func == func_handler.func


@pytest.mark.asyncio()
async def test_register_auto_rule():
    view = SomeView()

    class SomeRule(ABCRule[MessageCute]):
        async def check(self, event: MessageCute) -> bool:
            ...
    
    view.auto_rules.append(SomeRule())
    assert len(view.auto_rules) == 1
    assert isinstance(view.auto_rules[0], SomeRule)


@pytest.mark.asyncio()
async def test_register_return_manager():
    view = SomeView()

    @view.return_manager.register_manager(bytes)
    async def manager(value: bytes, event: MessageCute, ctx: Context) -> None:
        ...

    assert isinstance(view.return_manager, MessageReturnManager)
    assert manager in view.return_manager.managers
