"""Tests for the CLI settings screen."""

from __future__ import annotations

import pytest
from textual.widgets import Checkbox, Input

from apps.cli.app import DeepApp
from apps.cli.config import CliConfig
from apps.cli.screens.settings import SettingsScreen


@pytest.fixture
def app():
    return DeepApp(model="test", version="0.3.3")


class TestSettingsScreen:
    async def test_composes_and_shows_resolved_config_path(self, app):
        """The header renders the real config path, not the literal placeholder.

        Regression: the header Static was missing its f-string prefix, so it
        rendered the source text `{self._config_path}` instead of the path.
        """
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(SettingsScreen())
            await pilot.pause()

            screen = app.screen
            assert isinstance(screen, SettingsScreen)

            from textual.widgets import Static

            header = screen.query(Static).first()
            rendered = str(header.render())
            assert "{self._config_path}" not in rendered
            assert ".pydantic-deep" in rendered

    async def test_model_input_seeded_from_config(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(SettingsScreen())
            await pilot.pause()

            model_input = app.screen.query_one("#cfg-model", Input)
            assert model_input.value == CliConfig().model

    async def test_feature_checkboxes_present(self, app):
        async with app.run_test(size=(120, 40)) as pilot:
            await app.push_screen(SettingsScreen())
            await pilot.pause()

            skills = app.screen.query_one("#cfg-include_skills", Checkbox)
            assert skills.value is CliConfig().include_skills
