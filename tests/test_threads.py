# SPDX-License-Identifier: MIT

from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, Mock, patch

from nextcord.threads import Thread


def make_thread(thread_id: int = 123) -> Thread:
    thread = object.__new__(Thread)
    thread.id = thread_id
    return thread


class ThreadStarterMessageTests(TestCase):
    def test_starter_message_id_matches_thread_id(self) -> None:
        thread = make_thread()

        assert thread.starter_message_id == thread.id

    def test_get_partial_starter_message_uses_thread_id(self) -> None:
        thread = make_thread()
        expected = Mock()

        with patch.object(Thread, "get_partial_message", return_value=expected) as get_partial:
            assert thread.get_partial_starter_message() is expected

        get_partial.assert_called_once_with(thread.id)


class ThreadStarterMessageAsyncTests(IsolatedAsyncioTestCase):
    async def test_fetch_starter_message_uses_thread_id(self) -> None:
        thread = make_thread()
        expected = Mock()

        with patch.object(Thread, "fetch_message", AsyncMock(return_value=expected)) as fetch:
            assert await thread.fetch_starter_message() is expected

        fetch.assert_awaited_once_with(thread.id)
