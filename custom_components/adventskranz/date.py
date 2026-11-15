"""Date platform for simulating a test date in the Adventskranz integration."""
from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import AdventskranzState
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Adventskranz test date entity."""
    state: AdventskranzState = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AdventskranzTestDateEntity(state, entry.entry_id)])


class AdventskranzTestDateEntity(DateEntity):
    """Date entity allowing the user to pick any date to test the Advent calculation."""

    _attr_has_entity_name = True
    _attr_name = "Test-Datum"
    _attr_icon = "mdi:calendar-edit"
    _attr_should_poll = False

    def __init__(self, state: AdventskranzState, entry_id: str) -> None:
        """Initialize the test date entity."""
        self._state = state
        self._attr_unique_id = f"{entry_id}_test_date"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Adventskranz",
            manufacturer="Custom Integration",
            model="Adventskranz Status & Steuerung",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> date:
        """Return the currently selected test date (or today if not set)."""
        return self._state.test_date or dt_util.now().date()

    async def async_set_value(self, value: date) -> None:
        """Set a new test date and automatically switch to date simulation mode."""
        self._state.set_test_date(value)

    async def async_added_to_hass(self) -> None:
        """Register state listener."""
        self._state.listeners.append(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister state listener."""
        if self._handle_update in self._state.listeners:
            self._state.listeners.remove(self._handle_update)

    @callback
    def _handle_update(self) -> None:
        """Write updated state to Home Assistant."""
        self.async_write_ha_state()
