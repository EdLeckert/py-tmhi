## T-Mobile Home Internet API Client

A python client for the T-Mobile Home Internet API.

It was created for use by [ha-tmobilehome](https://github.com/EdLeckert/ha-tmobilehome)

Tested against a Sercomm TMO-G4SE gateway, hardware version `R02` and software version `1.03.20`.

## Installation

```bash
pip install pytmhi
```

## Usage

```python
from pytmhi import TmiApiClient
client = TmiApiClient("admin",<admin-password>)
version = client.get_version()
```

## Functions

All functions are synchronous (blocking).

### Retrieve gateway device details, basic received signal values, and current time.
```python
client.get_gateway_config()
```

### Retrieve basic received signal values (same as included in above).
```python
client.get_gateway_signal()
```

### Retrieve detailed cell tower and received signal values.
```python
client.get_cell()
```

### Retrieve sim card data.
```python
client.get_sim()
```

### Retrieve wired and wireless client details.
```python
client.get_clients()
```

### Retrieve access point (wireless) settings.
```python
client.get_ap_config()
```

### Set access point (wireless) settings. Gateway will reset and may lose communications for a minute or more.
```python
client.set_ap_config(new_ap_config)
```
| Parameter       | Type | Required?    | Description
| ---------       | ---- | ---------    | -----------
| `new_ap_config` | dict | **required** | Contains entire contents from get_ap_config() with any changes to be made. (See example below.)

### Cause immediate reboot of gateway.
```python
client.reboot_gateway()
```

### Retrieve current version of API.
```python
client.get_version()
```


## Examples

### Retrieve 4G RSRQ

```python
rsrq__4g = client.get_gateway_signal()["signal"]["4g"]["rsrq"]
```

### Retrieve 5G Cell Tower ECGI (Cell Global Identifier)

```python
ecgi_5g = client.get_cell()["cell"]["5g"]["ecgi"]
```

### Turn off 2.4GHz WiFi

Do not turn off WiFi unless you are connected to the gateway via a cable!

Note that the gateway will reset and may lose communications for a minute or more.

```python
access_point_config = client.get_ap_config()
access_point_config["2.4ghz"]["isRadioEnabled"] = False
client.set_ap_config(access_point_config)
```

## Acknowledgement

Thanks to Michael R. Torres (micrictor) for providing the original version of this fork. 
Also thanks to Zachary Wander (zacharee), author of HINTControl, which provided a much-needed API reference.
