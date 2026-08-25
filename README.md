# HaImmer

A custom [HACS](https://hacs.xyz/) integration for Home Assistant that polls an ImmerGas REST device and exposes its values as sensors and binary sensors.

## Features

- Polls the ImmerGas REST endpoint every second (configurable).
- Supports HTTP Basic Authentication.
- Replaces the YAML `rest` configuration below with a UI-configurable integration.
- Adds two new boolean sensors:
  - **ImmerGas Stable Temperaute** – `on` when the temperature value has not changed for more than the configured stable threshold.
  - **ImmerGas Stable Throttle** – `on` when the throttle value has not changed for more than the configured stable threshold.

## Original YAML configuration

```yaml
rest:
  - authentication: basic
    scan_interval: 2
    timeout: 1
    resource: http://192.168.1.200:8099/Immer/immerrestdata
    sensor:
      - name: "ImmerGas Temperaute"
        value_template: "{{ value_json.temperaute }}"
        state_class: measurement
      - name: "ImmerGas Throttle"
        value_template: "{{ value_json.throttle }}"
        state_class: measurement
        unit_of_measurement: kW
    binary_sensor:
      - name: "ImmerGas Heating"
        value_template: "{{ value_json.heating }}"
      - name: "ImmerGas Boiler"
        value_template: "{{ value_json.boilerOn }}"
```

## Installation

1. Add this repository to HACS as a custom repository (type: **Integration**).
2. Install the **ImmerGas** integration.
3. Restart Home Assistant.
4. Go to **Settings > Devices & services > Add integration** and search for **ImmerGas**.
5. Enter the host, port, API path, credentials, and polling options.

## Configuration

| Option | Default | Description |
| --- | --- | --- |
| Host | `192.168.1.200` | IP address or hostname of the ImmerGas device. |
| Port | `8099` | HTTP port of the REST endpoint. |
| Path | `/Immer/immerrestdata` | REST endpoint path. |
| Username | (required) | Basic auth username. |
| Password | (required) | Basic auth password. |
| Update interval | `1` | Seconds between polls. |
| Request timeout | `5` | Seconds to wait for a single request. |
| Stable threshold | `10` | Seconds a value must stay unchanged before the stable binary sensor turns on. |

## Entities

| Entity | Type | Source field |
| --- | --- | --- |
| ImmerGas Temperaute | sensor | `temperaute` |
| ImmerGas Throttle | sensor | `throttle` |
| ImmerGas Heating | binary_sensor | `heating` |
| ImmerGas Boiler | binary_sensor | `boilerOn` |
| ImmerGas Stable Temperaute | binary_sensor | computed |
| ImmerGas Stable Throttle | binary_sensor | computed |
