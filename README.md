# Weather Station e-Paper Display

[![Python 3](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Compatible-c51a4a.svg)](https://www.raspberrypi.org/)
[![Pirate Weather](https://img.shields.io/badge/Pirate%20Weather-API-purple.svg)](https://pirateweather.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Raspberry Pi weather station with a Waveshare 2.13" tri-color e-Paper display. Shows current temperature, daily max, and weather summary.

## Table of Contents

- [Quick Start](#quick-start)
- [What You Need](#what-you-need)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)
- [Credits](#credits)
- [License](#license)

---

## Quick Start

> **TL;DR** - Get it running in 4 steps:

1. **Get a free API key** from [Pirate Weather](https://pirate-weather.apiable.io/products/weather-data/plans) (10,000 requests/month free)
2. **Clone this repo** and install dependencies (see [Installation](#installation))
3. **Configure `.env`** with your API key and location
4. **Run it:** `python3 weatherstation.py`

---

## What You Need

### Hardware
- Raspberry Pi (Zero W, 3, 4, or 5)
- [Waveshare 2.13" e-Paper HAT (B)](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(B)_Manual) - the tri-color (black/white/red) version
- Internet connection

### Software
- Free [Pirate Weather API key](https://pirate-weather.apiable.io/products/weather-data/plans)
- Raspberry Pi OS or Debian-based Linux distro

---

## Installation

### 1. Enable SPI Interface

```bash
sudo raspi-config
# Navigate to "Interfacing Options" → "SPI" and enable it
```

### 2. Install System Dependencies

```bash
sudo apt install python3-pip python3-venv pipx git fonts-dejavu
```

### 3. Install Weather Station

#### Option A: Quick Install with pipx (Recommended)

```bash
pipx install "git+https://github.com/benjaminburzan/weatherstation-epaper.git"
pipx inject weatherstation-epaper "git+https://github.com/waveshareteam/e-Paper.git#subdirectory=RaspberryPi_JetsonNano/python"
```

#### Option B: Manual Setup with venv

```bash
cd ~
git clone https://github.com/benjaminburzan/weatherstation-epaper.git
cd weatherstation-epaper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install "git+https://github.com/waveshareteam/e-Paper.git#subdirectory=RaspberryPi_JetsonNano/python"
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

At minimum, set your `PIRATE_WEATHER_API_KEY`. See [Configuration](#configuration) for all available options.

---

## Configuration

All settings are configured via environment variables in your `.env` file.

### API Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `PIRATE_WEATHER_API_KEY` | Your Pirate Weather API key | **Required** |
| `LATITUDE` | Your location's latitude | 52.5200 (Berlin) |
| `LONGITUDE` | Your location's longitude | 13.4050 (Berlin) |
| `LANGUAGE` | Weather summary language ([see options](https://pirateweather.net/en/latest/API/#language)) | de |
| `UNITS` | `si` for Celsius, `us` for Fahrenheit | si |

### Display Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `FLIP_DISPLAY` | Set to `true` to rotate display 180° | false |
| `FONT_SIZE_TEMPERATURE` | Temperature text size (pixels) | 32 |
| `FONT_SIZE_SUMMARY_MAX` | Maximum summary text size (auto-shrinks to fit) | 18 |
| `FONT_SIZE_SUMMARY_MIN` | Minimum summary text size | 12 |
| `MAX_SUMMARY_LINES` | Maximum lines for summary (wraps long text) | 2 |
| `ICON_SIZE` | Weather icon size (pixels) | 48 |
| `PADDING` | Screen edge padding (pixels) | 10 |

The summary font size automatically adjusts to fit long text. It starts at `FONT_SIZE_SUMMARY_MAX` and shrinks down to `FONT_SIZE_SUMMARY_MIN` until all words fit within `MAX_SUMMARY_LINES`.

### Timing

| Variable | Description | Default |
|----------|-------------|---------|
| `UPDATE_INTERVAL_SECONDS` | How often to refresh (1800 = 30 min) | 1800 |

### Paths

| Variable | Description | Default |
|----------|-------------|---------|
| `FONT_PATH` | TrueType font file | `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` |
| `ICON_FONT_PATH` | Weather icons font file | `weathericons.ttf` |
| `LOG_FILE` | Log file location | `/var/log/weatherstation.log` |

---

## Usage

### Manual Start

```bash
cd ~/weatherstation-epaper
source venv/bin/activate
python weatherstation.py
```

### Run as System Service (recommended)

For automatic startup on boot:

```bash
sudo cp weatherstation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weatherstation
sudo systemctl start weatherstation
```

**Check status:**
```bash
sudo systemctl status weatherstation
```

**View logs:**
```bash
tail -f /var/log/weatherstation.log
```

---

## Troubleshooting

### Display not updating

1. Check SPI is enabled: `ls /dev/spi*`
2. Verify wiring connections
3. Check logs: `tail -f /var/log/weatherstation.log`

### API errors

1. Verify your API key: `echo $PIRATE_WEATHER_API_KEY`
2. Check internet: `ping pirateweather.net`
3. Ensure coordinates are valid decimal numbers

### Service not starting

1. Check status: `sudo systemctl status weatherstation`
2. Verify paths in service file match your installation
3. Ensure `.env` file exists with valid API key

### Permission errors

```bash
sudo touch /var/log/weatherstation.log
sudo chmod 666 /var/log/weatherstation.log
```

---

## File Structure

```
weatherstation-epaper/
├── weatherstation.py      # Main application
├── weatherstation.service # Systemd service file
├── requirements.txt       # Python dependencies
├── .env                   # Your configuration (create from .env.example)
├── .env.example           # Configuration template
├── icons.json             # Weather icon unicode mapping
├── weathericons.ttf       # Weather icons font
└── venv/                  # Python virtual environment (created during setup)
```

---

## Credits

- Weather icons: [Erik Flowers Weather Icons](https://github.com/erikflowers/weather-icons)
- Weather data: [Pirate Weather API](https://pirateweather.net/)
- e-Paper library: [Waveshare e-Paper](https://github.com/waveshareteam/e-Paper)

## License

MIT License - see [LICENSE](LICENSE)
