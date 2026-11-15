"""Diagnostics support for Adventskranz."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import AdventskranzState
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    state: AdventskranzState = hass.data[DOMAIN][entry.entry_id]
    return {
        "effective_date": state.effective_date.isoformat(),
        "current_phase_index": state.current_phase_index,
        "calculated_phase_index": state.calculated_phase_index,
        "use_test_date": state.use_test_date,
        "override_phase": state.override_phase,
        "phase_info": state.phase_info,
        "advent_dates": state.advent_dates,
    }
