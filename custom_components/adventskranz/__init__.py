"""The Adventskranz integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import hashlib
import logging
from pathlib import Path
from typing import Any, Callable

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    PHASES,
    PLATFORMS,
    STATIC_URL_BASE,
    PhaseInfo,
    calculate_advent_dates,
    get_phase_for_date,
)

_LOGGER = logging.getLogger(__name__)

CARD_VERSION = "1.2.5"
CARD_FILENAME = "adventskranz-card.js"


def _compute_card_resource_url(frontend_dir: Path) -> str:
    """Build the Lovelace resource URL with a short SHA-256 content hash."""
    bundled_card = frontend_dir / CARD_FILENAME
    card_hash = ""
    if bundled_card.is_file():
        card_hash = hashlib.sha256(bundled_card.read_bytes()).hexdigest()[:8]
    version_tag = f"{CARD_VERSION}-{card_hash}" if card_hash else CARD_VERSION
    return f"{STATIC_URL_BASE}/{CARD_FILENAME}?v={version_tag}"


async def _async_register_lovelace_resource(
    hass: HomeAssistant, resource_url: str
) -> None:
    """Automatically register or update the Adventskranz Lovelace card resource."""
    try:
        lovelace_data: Any = hass.data.get("lovelace")
        if not lovelace_data:
            return
        resources = getattr(lovelace_data, "resources", None)
        if not resources:
            return
        if not getattr(resources, "loaded", True):
            await resources.async_load()

        for item in resources.async_items():
            url = item.get("url", "")
            if CARD_FILENAME in url:
                if url != resource_url:
                    await resources.async_update_item(
                        item["id"],
                        {"res_type": "module", "url": resource_url},
                    )
                return

        await resources.async_create_item(
            {"res_type": "module", "url": resource_url}
        )
        _LOGGER.info("Registered Lovelace resource: %s", resource_url)
    except Exception as exc:  # noqa: BLE001
        _LOGGER.debug("Could not auto-register Lovelace resource: %s", exc)


async def _async_unregister_lovelace_resource(hass: HomeAssistant) -> None:
    """Remove the Adventskranz Lovelace card resource when the entry is deleted."""
    try:
        lovelace_data: Any = hass.data.get("lovelace")
        if not lovelace_data:
            return
        resources = getattr(lovelace_data, "resources", None)
        if not resources:
            return
        if not getattr(resources, "loaded", True):
            await resources.async_load()

        for item in list(resources.async_items()):
            url = item.get("url", "")
            if CARD_FILENAME in url:
                await resources.async_delete_item(item["id"])
    except Exception as exc:  # noqa: BLE001
        _LOGGER.debug("Could not unregister Lovelace resource: %s", exc)


@dataclass
class AdventskranzState:
    """Holds current state, simulated date, and test override for Adventskranz."""

    hass: HomeAssistant
    override_phase: int | None = None
    use_test_date: bool = False
    test_date: date | None = None
    listeners: list[Callable[[], None]] = field(default_factory=list)
    unsub_midnight: Callable[[], None] | None = None

    @property
    def effective_date(self) -> date:
        """Return the date used for calculation (simulated test_date or real today)."""
        if self.use_test_date and self.test_date is not None:
            return self.test_date
        return dt_util.now().date()

    @property
    def current_phase_index(self) -> int:
        """Return active phase index (0..5), respecting phase override or test_date."""
        if self.override_phase is not None:
            return self.override_phase
        return get_phase_for_date(self.effective_date)

    @property
    def calculated_phase_index(self) -> int:
        """Return date-calculated phase index (0..5) for the effective date."""
        return get_phase_for_date(self.effective_date)

    @property
    def phase_info(self) -> PhaseInfo:
        """Return full metadata for the active phase."""
        return PHASES[self.current_phase_index]

    @property
    def advent_dates(self) -> dict[str, str]:
        """Return ISO formatted Advent dates for the effective year."""
        dates = calculate_advent_dates(self.effective_date.year)
        return {k: v.isoformat() for k, v in dates.items()}

    @callback
    def set_override_phase(self, phase: int | None) -> None:
        """Set a direct phase override (or reset to automatic)."""
        self.override_phase = phase
        self.use_test_date = False
        self.notify_listeners()

    @callback
    def set_test_date(self, new_date: date) -> None:
        """Set a simulated test date and activate date simulation mode."""
        self.test_date = new_date
        self.use_test_date = True
        self.override_phase = None
        self.notify_listeners()

    @callback
    def enable_test_date_mode(self) -> None:
        """Switch mode to simulated test date (initializing to today if unset)."""
        if self.test_date is None:
            self.test_date = dt_util.now().date()
        self.use_test_date = True
        self.override_phase = None
        self.notify_listeners()

    @callback
    def notify_listeners(self) -> None:
        """Notify all registered entities of a state update."""
        for listener in list(self.listeners):
            listener()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Adventskranz from a config entry."""
    # Remove any orphaned entity registry entries from previous installs so entity_ids never get a _2 suffix
    ent_reg = er.async_get(hass)
    for ent in list(ent_reg.entities.values()):
        if ent.platform == DOMAIN and ent.config_entry_id != entry.entry_id:
            ent_reg.async_remove(ent.entity_id)

    domain_data = hass.data.setdefault(DOMAIN, {})
    frontend_dir = Path(__file__).parent / "frontend"

    if not domain_data.get("static_registered") and getattr(hass, "http", None) is not None:
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    STATIC_URL_BASE,
                    str(frontend_dir),
                    cache_headers=False,
                )
            ]
        )
        domain_data["static_registered"] = True

    resource_url = await hass.async_add_executor_job(
        _compute_card_resource_url, frontend_dir
    )
    await _async_register_lovelace_resource(hass, resource_url)

    state = AdventskranzState(hass=hass, test_date=dt_util.now().date())

    @callback
    def _handle_midnight(_now) -> None:
        state.notify_listeners()

    state.unsub_midnight = async_track_time_change(
        hass, _handle_midnight, hour=0, minute=0, second=1
    )

    domain_data[entry.entry_id] = state
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        state: AdventskranzState = hass.data[DOMAIN].pop(entry.entry_id)
        if state.unsub_midnight:
            state.unsub_midnight()
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Clean up Lovelace resource when entry is deleted."""
    await _async_unregister_lovelace_resource(hass)
