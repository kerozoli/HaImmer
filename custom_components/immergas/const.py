"""Constants for the ImmerGas integration."""

from typing import Final

DOMAIN: Final = "immergas"

CONF_PATH: Final = "path"
CONF_TIMEOUT: Final = "timeout"
CONF_STABLE_THRESHOLD: Final = "stable_threshold"
CONF_MINIMUM_THROTTLE_THRESHOLD: Final = "minimum_throttle_threshold"

DEFAULT_HOST: Final = "192.168.1.200"
DEFAULT_PORT: Final = 8099
DEFAULT_PATH: Final = "/Immer/immerrestdata"
DEFAULT_SCAN_INTERVAL: Final = 1
DEFAULT_TIMEOUT: Final = 5
DEFAULT_STABLE_THRESHOLD: Final = 10
DEFAULT_MINIMUM_THROTTLE_THRESHOLD: Final = 15

MINIMUM_THROTTLE_VALUE_KW: Final = 1

DATA_KEY_TEMPERATURE: Final = "temperaute"
DATA_KEY_THROTTLE: Final = "throttle"
DATA_KEY_HEATING: Final = "heating"
DATA_KEY_BOILER: Final = "boilerOn"

STABLE_KEY_TEMPERATURE: Final = "stable_temperature"
STABLE_KEY_THROTTLE: Final = "stable_throttle"
