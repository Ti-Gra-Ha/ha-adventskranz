"""Config flow for Adventskranz integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult

from .const import DOMAIN


class AdventskranzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Adventskranz."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="Adventskranz", data={})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )
