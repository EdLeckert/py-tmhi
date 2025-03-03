## TMobile Home Internet API Client

A python client for the T-Mobile Home Internet API.

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

```python
client.get_gateway_config()
```
Retrieve gateway device details, basic received signal values, and current time.

```python
client.get_gateway_signal()
```
Retrieve basic received signal values (same as included in above).

```python
client.get_cell()
```
Retrieve detailed cell tower and received signal values.

```python
client.get_sim()
```
Retrieve sim card data.

```python
client.get_clients()
```
Retrieve wired and wireless client details.

```python
client.get_ap_config()
```
Retrieve access point (wireless) settings.

```python
client.set_ap_config(new_ap_config)
```
Set access point (wireless) settings. Gateway will reset and may lose communications for a minute or more.
Parameter:
  new_ap_config - Contains entire contents from get_ap_config() with any changes to be made.

```python
client.reboot_gateway()
```
Causes immediate reboot of gateway.

