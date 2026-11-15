"""Sensor platform for the Adventskranz integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdventskranzState
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Adventskranz sensor entities."""
    state: AdventskranzState = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            AdventskranzStatusSensor(state, entry.entry_id),
            AdventskranzPhaseSensor(state, entry.entry_id),
            AdventskranzCandlesSensor(state, entry.entry_id),
        ]
    )


class AdventskranzBaseSensor(SensorEntity):
    """Base class for Adventskranz sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, state: AdventskranzState, entry_id: str) -> None:
        """Initialize the base sensor."""
        self._state = state
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Adventskranz",
            manufacturer="Custom Integration",
            model="Adventskranz Status & Steuerung",
            entry_type=DeviceEntryType.SERVICE,
        )

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


class AdventskranzStatusSensor(AdventskranzBaseSensor):
    """Main status sensor representing the current Adventskranz state."""

    _attr_name = "Status"
    _attr_icon = "mdi:candycane"

    def __init__(self, state: AdventskranzState, entry_id: str) -> None:
        """Initialize the status sensor."""
        super().__init__(state, entry_id)
        self._attr_unique_id = f"{entry_id}_status"

    @property
    def native_value(self) -> str:
        """Return the human-readable short status label."""
        return self._state.phase_info["short_label"]

    @property
    def icon(self) -> str:
        """Return dynamic icon based on lit candles."""
        info = self._state.phase_info
        if info["burned_down"]:
            return "mdi:candle"
        if info["candles_lit"] > 0:
            return "mdi:candle"
        return "mdi:pine-tree"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return rich attributes for automations and the custom card."""
        info = self._state.phase_info
        dates = self._state.advent_dates
        return {
            "phase": info["phase"],
            "phase_key": info["key"],
            "description": info["label"],
            "candles_lit": info["candles_lit"],
            "burned_down": info["burned_down"],
            "default_image": info["default_image"],
            "effective_date": self._state.effective_date.isoformat(),
            "is_test_override": (
                self._state.override_phase is not None or self._state.use_test_date
            ),
            "use_test_date": self._state.use_test_date,
            "calculated_phase": self._state.calculated_phase_index,
            **dates,
        }


class AdventskranzPhaseSensor(AdventskranzBaseSensor):
    """Numeric phase sensor (0..5) for easy use in automations."""

    _attr_name = "Phase"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, state: AdventskranzState, entry_id: str) -> None:
        """Initialize the phase sensor."""
        super().__init__(state, entry_id)
        self._attr_unique_id = f"{entry_id}_phase"

    @property
    def native_value(self) -> int:
        """Return the active phase index (0..5)."""
        return self._state.current_phase_index


class AdventskranzCandlesSensor(AdventskranzBaseSensor):
    """Numeric sensor for number of currently burning candles (0..4)."""

    _attr_name = "Brennende Kerzen"
    _attr_icon = "mdi:candle"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, state: AdventskranzState, entry_id: str) -> None:
        """Initialize the burning candles sensor."""
        super().__init__(state, entry_id)
        self._attr_unique_id = f"{entry_id}_candles_lit"

    @property
    def native_value(self) -> int:
        """Return number of lit candles (0..4)."""
        return self._state.phase_info["candles_lit"]
