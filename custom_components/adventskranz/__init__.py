"""The Adventskranz integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import logging
from pathlib import Path
import shutil
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    PHASES,
    PLATFORMS,
    PhaseInfo,
    calculate_advent_dates,
    get_phase_for_date,
)

_LOGGER = logging.getLogger(__name__)

CARD_VERSION = "1.2.2"
CARD_FILENAME = "adventskranz-card.js"
CARD_RESOURCE_URL = f"/local/adventskranz/{CARD_FILENAME}?v={CARD_VERSION}"

BRAND_FILES = (
    "icon.png",
    "icon@2x.png",
    "logo.png",
    "logo@2x.png",
    "dark_icon.png",
    "dark_icon@2x.png",
    "dark_logo.png",
    "dark_logo@2x.png",
)

PNG_FILES = tuple(f"advent_{i}.png" for i in range(6))


def _sync_assets(config_dir: str) -> None:
    """Deploy bundled frontend card and default PNG assets to /config/www/adventskranz/."""
    comp_dir = Path(__file__).parent
    frontend_dir = comp_dir / "frontend"
    brand_dir = comp_dir / "brand"
    www_dir = Path(config_dir) / "www" / "adventskranz"

    frontend_dir.mkdir(parents=True, exist_ok=True)
    brand_dir.mkdir(parents=True, exist_ok=True)
    www_dir.mkdir(parents=True, exist_ok=True)

    # 1. Always update adventskranz-card.js in /config/www/adventskranz/ from bundled frontend/
    bundled_card = frontend_dir / CARD_FILENAME
    www_card = www_dir / CARD_FILENAME
    if bundled_card.is_file():
        if not www_card.is_file() or bundled_card.read_bytes() != www_card.read_bytes():
            shutil.copyfile(bundled_card, www_card)

    # 2. Copy default PNGs to /config/www/adventskranz/ if they do not exist yet
    for filename in PNG_FILES:
        www_file = www_dir / filename
        bundled_file = frontend_dir / filename
        if bundled_file.is_file() and not www_file.is_file():
            shutil.copyfile(bundled_file, www_file)

    # 3. Ensure brand icons exist from advent_4.png
    source_brand_png = frontend_dir / "advent_4.png"
    if not source_brand_png.is_file():
        source_brand_png = www_dir / "advent_4.png"
    if source_brand_png.is_file():
        for filename in BRAND_FILES:
            target = brand_dir / filename
            if (
                not target.is_file()
                or target.stat().st_size != source_brand_png.stat().st_size
            ):
                shutil.copyfile(source_brand_png, target)

    # 4. Clean any stale negative brand cache
    stale_cache = Path(config_dir) / ".cache" / "brands" / "integrations" / DOMAIN
    if stale_cache.is_dir():
        shutil.rmtree(stale_cache, ignore_errors=True)


async def _async_register_lovelace_resource(hass: HomeAssistant) -> None:
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
                if url != CARD_RESOURCE_URL:
                    await resources.async_update_item(
                        item["id"],
                        {"res_type": "module", "url": CARD_RESOURCE_URL},
                    )
                return

        await resources.async_create_item(
            {"res_type": "module", "url": CARD_RESOURCE_URL}
        )
        _LOGGER.info("Registered Lovelace resource: %s", CARD_RESOURCE_URL)
    except Exception as exc:  # noqa: BLE001
        _LOGGER.debug("Could not auto-register Lovelace resource: %s", exc)


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
    await hass.async_add_executor_job(_sync_assets, hass.config.path())
    await _async_register_lovelace_resource(hass)

    state = AdventskranzState(hass=hass, test_date=dt_util.now().date())

    @callback
    def _handle_midnight(_now) -> None:
        state.notify_listeners()

    state.unsub_midnight = async_track_time_change(
        hass, _handle_midnight, hour=0, minute=0, second=1
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = state
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
