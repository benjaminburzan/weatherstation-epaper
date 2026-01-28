# Claude Code Context

## Project Overview
Raspberry Pi weather station that displays current weather on a Waveshare 2.13" tri-color e-Paper display. Fetches data from Pirate Weather API.

## Tech Stack
- Python 3
- Pirate Weather API for weather data
- Waveshare e-Paper library for display
- PIL/Pillow for image rendering
- pytest for testing

## Key Files
- `weatherstation.py` - Main application with WeatherStation class and display logic
- `weathericons.ttf` - Erik Flowers weather icons font
- `icons.json` - Maps weather condition names to font unicode characters
- `.env.example` - Environment variable template
- `weatherstation.service` - Systemd service file for auto-start

## Running Tests
```bash
.venv/bin/python -m pytest tests/ -v
```

**Always run tests locally before pushing.**

Tests mock the hardware dependencies (`waveshare_epd`, `pirateweather`) since they require actual Raspberry Pi hardware.

## Development Notes
- Hardware libraries are mocked in tests - see `tests/test_weatherstation.py`
- Display uses landscape orientation (212x104 pixels)
- Supports tri-color: black, white, and red (red used when current temp >= max temp)
- All config via environment variables (see `.env.example`)
- Weather icons use font glyphs, not PNG files

## Common Tasks
- Update icon mappings: Edit `icons.json`
- Change display layout: Modify `display_weather()` in `weatherstation.py`
- Add new config options: Add to environment variables section at top of `weatherstation.py`
