"""Config flow for the ImmerGas integration."""

import logging
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_MINIMUM_THROTTLE_THRESHOLD,
    CONF_PATH,
    CONF_STABLE_THRESHOLD,
    DEFAULT_HOST,
    DEFAULT_MINIMUM_THROTTLE_THRESHOLD,
    DEFAULT_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_STABLE_THRESHOLD,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.positive_int,
        vol.Required(CONF_PATH, default=DEFAULT_PATH): str,
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(CONF_STABLE_THRESHOLD, default=DEFAULT_STABLE_THRESHOLD): cv.positive_int,
        vol.Optional(
            CONF_MINIMUM_THROTTLE_THRESHOLD, default=DEFAULT_MINIMUM_THROTTLE_THRESHOLD
        ): cv.positive_int,
    }
)


def _options_schema(entry: ConfigEntry) -> vol.Schema:
    """Return the options schema for an existing config entry."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=entry.options.get(
                    CONF_SCAN_INTERVAL,
                    entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ),
            ): cv.positive_int,
            vol.Optional(
                CONF_TIMEOUT,
                default=entry.options.get(
                    CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
                ),
            ): cv.positive_int,
            vol.Optional(
                CONF_STABLE_THRESHOLD,
                default=entry.options.get(
                    CONF_STABLE_THRESHOLD,
                    entry.data.get(CONF_STABLE_THRESHOLD, DEFAULT_STABLE_THRESHOLD),
                ),
            ): cv.positive_int,
            vol.Optional(
                CONF_MINIMUM_THROTTLE_THRESHOLD,
                default=entry.options.get(
                    CONF_MINIMUM_THROTTLE_THRESHOLD,
                    entry.data.get(
                        CONF_MINIMUM_THROTTLE_THRESHOLD, DEFAULT_MINIMUM_THROTTLE_THRESHOLD
                    ),
                ),
            ): cv.positive_int,
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input by trying to reach the device."""
    session = async_get_clientsession(hass)
    url = f"http://{data[CONF_HOST]}:{data[CONF_PORT]}{data[CONF_PATH]}"
    username = data.get(CONF_USERNAME, "")
    password = data.get(CONF_PASSWORD, "")
    auth = aiohttp.BasicAuth(username, password) if username or password else None
    timeout = data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    try:
        async with async_timeout.timeout(timeout):
            response = await session.get(url, auth=auth, ssl=False)
        response.raise_for_status()
        await response.json()
    except TimeoutError as err:
        raise CannotConnect from err
    except aiohttp.ClientError as err:
        raise CannotConnect from err
    except Exception as err:
        raise InvalidAuth from err

    return {"title": f"ImmerGas ({data[CONF_HOST]})"}


class ImmerGasConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ImmerGas."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                unique_id = f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_PATH]}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow for this handler."""
        return ImmerGasOptionsFlowHandler(config_entry)


class ImmerGasOptionsFlowHandler(OptionsFlow):
    """Handle options flow for ImmerGas."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(self.config_entry),
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid auth."""
