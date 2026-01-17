# MagTag GitHub Contribution Graph

A CircuitPython project that displays a GitHub user's contribution graph on an Adafruit MagTag e-ink display. Updates daily and shows a full year of contribution activity in a heatmap-style visualization.

## Features

- Fetches real GitHub contribution data via GraphQL API
- Displays 52 weeks (1 year) of contributions
- Grayscale heatmap visualization optimized for e-ink
- Daily auto-updates via deep sleep (24-hour cycle)
- Fake data mode for testing without network

## Hardware Required

- Adafruit MagTag 2.9" Grayscale E-Ink WiFi Display

## Setup

1. **Install CircuitPython 9.x** on your MagTag
   - Download from [circuitpython.org](https://circuitpython.org/board/adafruit_magtag_2.9_grayscale/)

2. **Copy required libraries** to `lib/` folder on CIRCUITPY drive:
   - `adafruit_display_shapes`
   - `adafruit_display_text`
   - `adafruit_bitmap_font`
   - `adafruit_requests.mpy`
   - `adafruit_magtag`
   - `adafruit_portalbase`
   - `adafruit_minimqtt`
   - `adafruit_ticks.mpy`
   - `adafruit_io`
   - `adafruit_fakerequests.mpy`
   - `neopixel.mpy`
   - `simpleio.mpy`

   Download from [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases)

3. **Create secrets.py** (see `secrets.py.example`)
   - Add your WiFi credentials
   - Generate a GitHub Personal Access Token with `read:user` scope at https://github.com/settings/tokens
   - Add the token to secrets.py

4. **Configure** `code.py`:
   - Set `GITHUB_USER` to the username you want to track
   - Set `USE_FAKE_DATA = False` to fetch real data

5. **Deploy** to your MagTag and enjoy!

## Configuration

- `GITHUB_USER`: GitHub username to display
- `USE_FAKE_DATA`: Set to `True` for testing, `False` for real data
- `UPDATE_INTERVAL`: Update frequency in seconds (default: 24 hours)

## Development

Uses VS Code tasks for easy deployment:
- `Cmd+Shift+B` - Deploy code.py only
- "Deploy All to MagTag" - Sync entire project

### Creating/Modifying the GitHub Logo

The GitHub logo bitmap is created using ImageMagick. To regenerate or modify:

```bash
# Resize to 40x40, preserve transparency, convert to indexed color BMP
convert GitHub_Invertocat_Black.png -resize 40x40 -background none \
  -gravity center -extent 40x40 -colors 4 -type Palette BMP3:github-logo.bmp
```

Adjust the `-resize 40x40` parameter to change the size. The `-colors 4` creates a 2-bit palette suitable for e-ink displays.

## License

MIT
