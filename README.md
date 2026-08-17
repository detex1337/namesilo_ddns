# NameSilo Dynamic DNS Updater

Simple **Dynamic DNS (DDNS) updater for NameSilo** written in Python.

The script detects the current public **IPv4 and IPv6 addresses** of the machine and updates the corresponding **A** and **AAAA** DNS records in NameSilo when the address has changed.

Useful for servers or home connections with a dynamic public IP where you want to keep a domain or subdomain pointing to the current address.

## Features

* Updates both **IPv4 (A)** and **IPv6 (AAAA)** records.
* Automatically detects the current public IP.
* Uses several IP detection services as fallbacks.
* Only updates DNS when the IP has actually changed.
* Works with the root domain or a subdomain.
* Simple configuration directly in the script.
* Suitable for running periodically with `cron` or a systemd timer.
* No external DDNS service required besides NameSilo.

## Requirements

* Python **3.10+**
* A domain using NameSilo DNS
* A NameSilo API key
* Existing **A** and **AAAA** records for the host you want to update
* Python package:

```bash
pip install requests
```

## Installation

Clone the repository:

```bash
git clone https://github.com/detex1337/namesilo_ddns.git
cd namesilo_ddns
```

Install the required dependency:

```bash
pip install requests
```

## Configuration

Edit `namesilo_ddns.py` and configure the following values:

```python
API_KEY = "your_namesilo_api_key"
DOMAIN = "example.com"
HOST = "@"
TTL = 3600
```

### `API_KEY`

Your NameSilo API key.

You can generate/manage API keys from your NameSilo account under:

**Account → API**

Do not publish or commit your real API key.

### `DOMAIN`

The main domain managed by NameSilo:

```python
DOMAIN = "example.com"
```

### `HOST`

The hostname that should be updated.

For the root domain:

```python
HOST = "@"
```

This updates:

```text
example.com
```

For a subdomain:

```python
HOST = "home"
```

This updates:

```text
home.example.com
```

### `TTL`

TTL for the DNS record, in seconds:

```python
TTL = 3600
```

## Usage

Run the script manually:

```bash
python3 namesilo_ddns.py
```

Example output:

```text
==================================================
 NameSilo Dynamic DNS Updater
==================================================
[✓] IP pública detectada: 203.0.113.10
[…] Consultando registros DNS de example.com…
[✓] La IP ya está actualizada (203.0.113.10). No se requiere cambio.
==================================================
[✓] IPv6 pública detectada: 2001:db8::10
[…] Consultando registros DNS de example.com…
[✓] La IPv6 ya está actualizada (2001:db8::10). No se requiere cambio.
==================================================
```

If the detected address differs from the current DNS record, the record is automatically updated through the NameSilo API.

## Automatic updates with cron

The script can be executed periodically using `cron`.

Edit your crontab:

```bash
crontab -e
```

For example, to check the IP every 5 minutes:

```cron
*/5 * * * * /usr/bin/python3 /path/to/namesilo_ddns/namesilo_ddns.py >> /var/log/namesilo_ddns.log 2>&1
```

Replace `/path/to/namesilo_ddns/` with the actual path where the repository is installed.

You can verify the configured job with:

```bash
crontab -l
```

## How it works

On every execution the script:

1. Detects the public IPv4 address.
2. Retrieves the DNS records from NameSilo.
3. Finds the configured `A` record.
4. Compares its current value with the detected IPv4 address.
5. Updates the record only when necessary.
6. Repeats the process for the public IPv6 address and the corresponding `AAAA` record.

Several external IP detection services are configured as fallbacks, so if one service is unavailable the script automatically tries the next one.

## Important

The script currently expects both IPv4 and IPv6 connectivity.

It **updates existing DNS records but does not create them automatically**. Create the corresponding `A` and `AAAA` records in NameSilo before running the updater.

The API key is stored directly in `namesilo_ddns.py`. Make sure it is never committed to a public repository.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [LICENSE](LICENSE) for details.
