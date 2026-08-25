"""Data update coordinator for the ImmerGas integration."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import aiohttp
import async_timeout

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PATH,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    DATA_KEY_BOILER,
    DATA_KEY_HEATING,
    DATA_KEY_TEMPERATURE,
    DATA_KEY_THROTTLE,
    DEFAULT_HOST,
    DEFAULT_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STABLE_THRESHOLD,
    DEFAULT_TIMEOUT,
    DOMAIN,
    STABLE_KEY_TEMPERATURE,
    STABLE_KEY_THROTTLE,
    CONF_STABLE_THRESHOLD,
)

_LOGGER = logging.getLogger(__name__)

RAW_KEYS = (DATA_KEY_TEMPERATURE, DATA_KEY_THROTTLE, DATA_KEY_HEATING, DATA_KEY_BOILER)
STABLE_MAP: dict[str, str] = {
    DATA_KEY_TEMPERATURE: STABLE_KEY_TEMPERATURE,
    DATA_KEY_THROTTLE: STABLE_KEY_THROTTLE,
}


class ImmerGasCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls the ImmerGas REST endpoint."""

    def __init__(self, hass: HomeAssistant, config_entry: Any) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self._host = config_entry.data.get(CONF_HOST, DEFAULT_HOST)
        self._port = config_entry.data.get(CONF_PORT, DEFAULT_PORT)
        self._path = config_entry.data.get(CONF_PATH, DEFAULT_PATH)
        self._timeout = config_entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
        self._stable_threshold = config_entry.data.get(
            CONF_STABLE_THRESHOLD, DEFAULT_STABLE_THRESHOLD
        )
        self._url = f"http://{self._host}:{self._port}{self._path}"
        self._auth = aiohttp.BasicAuth(
            config_entry.data[CONF_USERNAME], config_entry.data[CONF_PASSWORD]
        )
        self._session = async_get_clientsession(hass)
        self._last_values: dict[str, Any] = {}
        self._last_changed: dict[str, datetime] = {}

        update_interval = config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=dt_util.parse_duration(f"{update_interval}s"),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the ImmerGas REST endpoint."""
        now = dt_util.utcnow()
        data: dict[str, Any] = {}

        try:
            async with async_timeout.timeout(self._timeout):
                response = await self._session.get(
                    self._url,
                    auth=self._auth,
                    ssl=False,
                )
            response.raise_for_status()
            raw = await response.json()
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with ImmerGas device: {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with ImmerGas device: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error while fetching ImmerGas data: {err}") from err

        for key in RAW_KEYS:
            data[key] = raw.get(key)

        for key, stable_key in STABLE_MAP.items():
            current = data.get(key)
            if current != self._last_values.get(key):
                self._last_values[key] = current
                self._last_changed[key] = now
                data[stable_key] = False
            else:
                changed_at = self._last_changed.get(key, now)
                elapsed = (now - changed_at).total_seconds()
                data[stable_key] = elapsed > self._stable_threshold

        return data
