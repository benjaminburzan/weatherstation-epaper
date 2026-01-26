# Weather Station e-Paper Display

A Raspberry Pi weather station with a Waveshare 2.13" tri-color e-Paper display. Shows current temperature, daily max, and weather summary.

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

---

## Installation

### 1. Enable SPI Interface

```bash
sudo raspi-config
# Navigate to "Interfacing Options" → "SPI" and enable it
```

### 2. Install System Dependencies

```bash
sudo apt install python3-rpi.gpio python3-spidev python3-pip python3-pil \
    python3-numpy git python3-rpi-lgpio python3-lgpio python3-aiohttp \
    liblgpio-dev fonts-dejavu python3.11-venv swig build-essential \
    python3-dev python3-cairosvg
```

### 3. Install Waveshare e-Paper Library

```bash
pip3 install "git+https://github.com/waveshareteam/e-Paper.git#subdirectory=RaspberryPi_JetsonNano/python" --break-system-packages
```

### 4. Clone and Setup Weather Station

```bash
cd ~
git clone https://github.com/benjaminburzan/weatherstation-epaper.git
cd weatherstation-epaper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your settings:

```
PIRATE_WEATHER_API_KEY=your_api_key_here
LATITUDE=52.5200
LONGITUDE=13.4050
LANGUAGE=en
UNITS=si
```

---

## Configuration

### Environment Variables

Set these in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `PIRATE_WEATHER_API_KEY` | Your Pirate Weather API key | **Required** |
| `LATITUDE` | Your location's latitude | 52.5200 (Berlin) |
| `LONGITUDE` | Your location's longitude | 13.4050 (Berlin) |
| `LANGUAGE` | Weather summary language ([see options](https://pirateweather.net/en/latest/API/#language)) | de |
| `UNITS` | `si` for Celsius, `us` for Fahrenheit | si |

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

## Advanced Configuration

These settings are in `weatherstation.py`. Edit the file directly to customize:

### Display Settings

| Constant | Default | Description |
|----------|---------|-------------|
| `FONT_SIZE_TEMPERATURE` | 32 | Temperature text size (pixels) |
| `FONT_SIZE_SUMMARY` | 18 | Weather summary text size (max) |
| `MIN_FONT_SIZE_SUMMARY` | 10 | Minimum summary size (auto-shrinks for long text) |
| `ICON_SIZE` | 40 | Weather icon size (pixels) |
| `PADDING` | 10 | Screen edge padding (pixels) |

### Timing

| Constant | Default | Description |
|----------|---------|-------------|
| `UPDATE_INTERVAL_SECONDS` | 1800 | How often to refresh (1800 = 30 min) |

### Paths

| Constant | Default | Description |
|----------|---------|-------------|
| `FONT_PATH` | `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf` | TrueType font file |
| `LOG_FILE` | `/var/log/weatherstation.log` | Log file location |

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
├── icons.json             # Weather icon mapping
├── weather-icons/         # PNG weather icons
└── venv/                  # Python virtual environment (created during setup)
```

---

## Credits

- Weather icons: [Erik Flowers Weather Icons](https://github.com/erikflowers/weather-icons)
- Weather data: [Pirate Weather API](https://pirateweather.net/)
- e-Paper library: [Waveshare e-Paper](https://github.com/waveshareteam/e-Paper)

## License

MIT License - see [LICENSE](LICENSE)
