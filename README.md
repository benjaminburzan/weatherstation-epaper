# Weather Station e-Paper Display

A Raspberry Pi-based weather station that displays current weather data on a Waveshare 2.13" tri-color e-Paper display. Weather data is fetched from the Pirate Weather API.

## Features

- Displays current temperature and daily maximum temperature
- Shows weather summary in German
- Weather icons for visual representation
- Auto-updates every 30 minutes
- Low power consumption with e-Paper display sleep mode
- Temperature displayed in red when current temp equals or exceeds daily max

## Hardware Requirements

- Raspberry Pi (tested on Pi Zero W, Pi 3, Pi 4)
- Waveshare 2.13" e-Paper HAT (B/C variant - black/white/red)
- Internet connection for weather data

## Installation

### 1. Enable SPI Interface

```bash
sudo raspi-config
# Navigate to "Interfacing Options" → "SPI" and enable it
```

### 2. Install System Dependencies

```bash
sudo apt install python3-rpi.gpio python3-spidev python3-pip python3-pil \
    python3-numpy git vim python3-rpi-lgpio python3-lgpio python3-aiohttp \
    liblgpio-dev fonts-dejavu python3.11-venv swig build-essential \
    python3-dev python3-cairosvg
```

### 3. Install Waveshare e-Paper Library

```bash
git clone https://github.com/waveshareteam/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
pip3 install . --break-system-packages
```

### 4. Clone and Setup Weather Station

```bash
git clone https://github.com/yourusername/weatherstation-epaper.git
cd weatherstation-epaper
pip3 install --break-system-packages -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
cp .env.example .env
nano .env
```

Edit `.env` with your settings:

```
PIRATE_WEATHER_API_KEY=your_api_key_here
LATITUDE=52.5200
LONGITUDE=13.4050
```

Get your free API key from [Pirate Weather](https://pirateweather.net/).

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PIRATE_WEATHER_API_KEY` | Your Pirate Weather API key | Required |
| `LATITUDE` | Location latitude | 52.5200 (Berlin) |
| `LONGITUDE` | Location longitude | 13.4050 (Berlin) |

## Usage

### Manual Start

```bash
python3 weatherstation.py
```

### Run as System Service

Install the systemd service for automatic startup:

```bash
sudo cp weatherstation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weatherstation
sudo systemctl start weatherstation
```

Check service status:

```bash
sudo systemctl status weatherstation
```

View logs:

```bash
tail -f /var/log/weatherstation.log
```

## File Structure

```
weatherstation-epaper/
├── weatherstation.py      # Main application
├── weatherstation.service # Systemd service file
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration (create from .env.example)
├── .env.example           # Environment template
├── translation.json       # Weather summary translations (EN→DE)
├── icons.json             # Weather icon mapping
└── weather-icons/         # PNG weather icons
```

## Troubleshooting

### Display not updating

1. Check SPI is enabled: `ls /dev/spi*`
2. Verify wiring connections
3. Check logs: `tail -f /var/log/weatherstation.log`

### API errors

1. Verify your API key is set: `echo $PIRATE_WEATHER_API_KEY`
2. Check internet connectivity: `ping pirateweather.net`
3. Ensure coordinates are valid decimal numbers

### Service not starting

1. Check service status: `sudo systemctl status weatherstation`
2. Verify paths in service file match your installation
3. Ensure `.env` file exists with valid API key

### Permission errors

The service runs as root to access GPIO. Ensure log file is writable:

```bash
sudo touch /var/log/weatherstation.log
sudo chmod 666 /var/log/weatherstation.log
```

## Credits

- Weather icons: [Erik Flowers Weather Icons](https://github.com/erikflowers/weather-icons)
- Weather data: [Pirate Weather API](https://pirateweather.net/)
- e-Paper library: [Waveshare e-Paper](https://github.com/waveshareteam/e-Paper)

## License

MIT License
