"""Characterization tests for the slash-command dispatcher.

These pin the observable behaviour of `dispatch_command` (notifications, screen
pushes, history mutations) so the table-driven refactor is provably
behaviour-preserving.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from apps.cli.app import DeepApp
from apps.cli.commands import dispatch_command


@pytest.fixture
def app():
    return DeepApp(model="test", version="9.9.9")


def _notify_texts(app: DeepApp) -> list[str]:
    return [str(c.args[0]) for c in app.notify.mock_calls if c.args]  # type: ignore[attr-defined]


class TestSimpleCommands:
    async def test_version_notifies_version(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.notify = MagicMock()
            await dispatch_command(app, "/version")
            assert any("9.9.9" in t for t in _notify_texts(app))

    async def test_clear_empties_history_and_notifies(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.message_history = ["m1", "m2"]
            app.notify = MagicMock()
            await dispatch_command(app, "/clear")
            assert app.message_history == []
            assert any("cleared" in t.lower() for t in _notify_texts(app))

    async def test_undo_removes_last_turn(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.message_history = ["a", "b", "c", "d"]
            app.notify = MagicMock()
            await dispatch_command(app, "/undo")
            assert app.message_history == ["a", "b"]

    async def test_undo_empty_warns(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.message_history = []
            app.notify = MagicMock()
            await dispatch_command(app, "/undo")
            assert any("no messages" in t.lower() for t in _notify_texts(app))

    async def test_cost_and_tokens_notify(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.notify = MagicMock()
            await dispatch_command(app, "/cost")
            await dispatch_command(app, "/tokens")
            texts = _notify_texts(app)
            assert any("Cost" in t for t in texts)
            assert any("messages" in t for t in texts)

    async def test_save_notifies_autosave(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.notify = MagicMock()
            await dispatch_command(app, "/save")
            assert any("auto-saved" in t.lower() for t in _notify_texts(app))

    async def test_unknown_command_warns(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.notify = MagicMock()
            await dispatch_command(app, "/definitely-not-a-command")
            assert any("unknown command" in t.lower() for t in _notify_texts(app))


class TestScreenPushingCommands:
    @pytest.mark.parametrize(
        "command",
        ["/help", "/mcp", "/skills", "/settings", "/model", "/compact", "/remind"],
    )
    async def test_pushes_a_screen(self, app, command):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            before = len(app.screen_stack)
            await dispatch_command(app, command)
            await pilot.pause()
            assert len(app.screen_stack) > before


class TestAliases:
    @pytest.mark.parametrize("command", ["/quit", "/exit", "/q"])
    async def test_quit_aliases_exit(self, app, command):
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app.exit = MagicMock()
            await dispatch_command(app, command)
            app.exit.assert_called_once()
