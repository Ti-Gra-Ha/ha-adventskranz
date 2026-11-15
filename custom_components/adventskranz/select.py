"""Select platform for testing/overriding the Adventskranz phase or date."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AdventskranzState
from .const import DOMAIN

OPTION_AUTO = "Automatisch (nach Datum)"
OPTION_TEST_DATE = "Simulation: Test-Datum verwenden"
PHASE_OPTIONS = {
    0: "0: 4 neue Kerzen (Vor dem 1. Advent)",
    1: "1: 1. Advent (1 brennende Kerze)",
    2: "2: 2. Advent (2 brennende Kerzen)",
    3: "3: 3. Advent (3 brennende Kerzen)",
    4: "4: 4. Advent (4 brennende Kerzen)",
    5: "5: 4 abgebrannte Kerzen (ab So. nach 4. Advent)",
}
OPTIONS_TO_PHASE: dict[str, int | None] = {
    OPTION_AUTO: None,
    OPTION_TEST_DATE: -1,
    **{label: phase for phase, label in PHASE_OPTIONS.items()},
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Adventskranz select entity."""
    state: AdventskranzState = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AdventskranzModeSelect(state, entry.entry_id)])


class AdventskranzModeSelect(SelectEntity):
    """Select entity to switch between automatic date, simulated test date, and manual phases."""

    _attr_has_entity_name = True
    _attr_name = "Modus"
    _attr_icon = "mdi:tune-variant"
    _attr_should_poll = False
    _attr_options = list(OPTIONS_TO_PHASE.keys())

    def __init__(self, state: AdventskranzState, entry_id: str) -> None:
        """Initialize the mode select entity."""
        self._state = state
        self._attr_unique_id = f"{entry_id}_mode"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name="Adventskranz",
            manufacturer="Custom Integration",
            model="Adventskranz Status & Steuerung",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def current_option(self) -> str:
        """Return currently selected option."""
        if self._state.use_test_date:
            return OPTION_TEST_DATE
        if self._state.override_phase is None:
            return OPTION_AUTO
        return PHASE_OPTIONS.get(self._state.override_phase, OPTION_AUTO)

    async def async_select_option(self, option: str) -> None:
        """Change the selected mode/phase."""
        if option == OPTION_TEST_DATE:
            self._state.enable_test_date_mode()
            return
        phase = OPTIONS_TO_PHASE.get(option)
        self._state.set_override_phase(phase)

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
