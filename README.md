<p align="center">
  <img src="assets/logo.png" alt="LEDsplay logo" width="120">
</p>

<h1 align="center">LEDsplay</h1>

<p align="center"><strong>Turn your piano into an interactive LED learning system.</strong></p>

![Version](https://img.shields.io/github/v/release/PabloCSScobar/ledsplay)
![License](https://img.shields.io/badge/license-proprietary-blue)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-c51a4a)

LEDsplay connects your digital piano to an LED strip via MIDI on a Raspberry Pi. Every key lights up in real time as you play. Learn songs, practice scales, play games - all controlled from a web app on your phone, tablet, or computer.

---

## Features

- 🎹 **Real-time LED visualization** - every key lights up instantly as you play
- 🎨 **LED animations** - Rainbow, Sparkle, Gradient, Bubble, Tetris, Police and more
- 🎵 **Song learning** - follow the lights, adjust tempo, practice hands separately, loop sections
- 🎼 **Sheet music display** - real notation in the browser with notes highlighted as you play
- 🎯 **Scales & note training** - all major scales with LED guides, 3 difficulty levels
- 🎮 **Piano games** - Reaction Game, Piano Battle (2-player), LED Keeper
- 📱 **Web interface** - control everything from your phone, tablet, or any browser

11 public domain demo songs included (Canon in D, Für Elise, Moonlight Sonata, and more). Upload your own MIDI/MusicXML files with the paid version.

---

## What it looks like

<p align="center">
  <img src="assets/hero.gif" alt="LEDsplay in action" width="700">
</p>

<p align="center">
  <img src="assets/rainbow.jpg" alt="Rainbow LED animation" width="700">
</p>

<table align="center"><tr>
<td valign="top">
  <img src="assets/ui/practice_mode__fullscreen_learning.png" alt="Sheet music learning mode" width="200"><br>
  <img src="assets/ui/practice-hub.png" alt="Practice hub" width="200">
</td>
<td valign="top">
  <img src="assets/ui/animations.png" alt="LED animations" width="200">
</td>
<td valign="top">
  <img src="assets/ui/note_learning_1.png" alt="Note learning" width="200"><br>
  <img src="assets/ui/games_1.png" alt="Piano games" width="200">
</td>
</tr></table>

<details>
<summary>More screenshots</summary>

### LED visualisation
<p>
  <img src="assets/ui/effects.png" width="220">
  &nbsp;
  <img src="assets/ui/effects_background.png" width="220">
  &nbsp;
  <img src="assets/ui/leds_conf.png" width="220">
</p>

### Song learning & practice
<p>
  <img src="assets/ui/practice_mode_1.png" width="220">
  &nbsp;
  <img src="assets/ui/practice_mode__fullscreen_learning.png" width="220">
  &nbsp;
  <img src="assets/ui/practice_mode_falling_notes.png" width="220">
</p>

### Free piano
<p>
  <img src="assets/ui/free_piano_2.png" width="220">
  &nbsp;
  <img src="assets/ui/free_piano_3.png" width="220">
  &nbsp;
  <img src="assets/ui/free_piano_drums.png" width="220">
</p>

### Note learning & scales
<p>
  <img src="assets/ui/note_learning_1.png" width="220">
  &nbsp;
  <img src="assets/ui/note_learning_2.png" width="220">
  &nbsp;
  <img src="assets/ui/note_learning_3.png" width="220">
</p>
<p>
  <img src="assets/ui/scales.png" width="220">
</p>

### Games
<p>
  <img src="assets/ui/games_1.png" width="220">
  &nbsp;
  <img src="assets/ui/games_2.png" width="220">
  &nbsp;
  <img src="assets/ui/games_3.png" width="220">
</p>

### System
<p>
  <img src="assets/ui/wifi_networks.png" width="220">
  &nbsp;
  <img src="assets/ui/updating_version_2.png" width="220">
  &nbsp;
  <img src="assets/ui/led_mapping.png" width="220">
</p>

</details>

---

## Free vs Paid

The free version works forever - no time limit, no account needed.

| | Free | Paid (one-time) |
|---|:---:|:---:|
| Real-time key lighting | ✅ | ✅ |
| All LED animations | ✅ | ✅ |
| 11 demo songs | ✅ | ✅ |
| Upload your own songs (MIDI/MusicXML) | ❌ | ✅ |
| Sheet music display | ❌ | ✅ |
| Scale & note learning | ❌ | ✅ |
| Piano games | ❌ | ✅ |
| MIDI recording & playback | ❌ | ✅ |
| All future features | ❌ | ✅ |

**No subscription.** Pay once, own it forever. No monthly fees, no cloud dependency - LEDsplay runs entirely on your Raspberry Pi. Up to 3 devices per license.

**[→ Get LEDsplay](https://ledsplay.lemonsqueezy.com)** - 14-day free trial, no credit card needed

---

## What you need

### Hardware

| Part | Details | Est. cost |
|------|---------|-----------|
| Raspberry Pi | **Zero 2W** (fits the custom PCB/case) or **4B/5** (standalone setup) | $15 *(Zero 2W)* |
| microSD card | 8 GB or larger, Class 10 / A1 recommended | $5 |
| WS2812B LED strip | 144 LEDs/m, individually addressable (look for *"2 m in a single piece"* if you don't want to solder) | $8–15 |
| Digital piano | Any with **USB MIDI** output (tested on Roland FP-30) | - |
| USB cable | Piano side: usually USB-B. Pi side: micro USB (Zero 2W) or USB-A (Pi 4/5) | $3–5 |
| Power supply | **5 V, 3 A minimum.** micro USB for the DIY build (Pi Zero 2W) or USB-C for the custom PCB - see [Power & brightness](#power--brightness) | $5–15 |
| Other / optional | Jumper wires to connect components to the Pi (female end for the GPIO header); heat-shrink tubing; screws **or** glue to join the case halves; double-sided tape or velcro to attach the case to the piano | $1–5 |

**Estimated total (without piano): $40–60** with a Pi Zero 2W and components you don't already have.

---

## Build options

LEDsplay runs the same software on any supported Pi. You can choose between two physical builds:

- **DIY build** - components wired straight into the GPIO header. Cheapest, little to no soldering required.
- **Build with custom PCB and 3D case** - skips almost all of the wiring work. Design files included with the paid version.

Works with any digital piano that has USB MIDI output. Primary testing is done on a **Roland FP-30**.

---

### DIY build

> **A note from me:** I'm not an electronics engineer. This is the wiring I've been running for over a year without any issues, but it may not be the most elegant or textbook-correct setup. If you have ideas for improvements, I'd love to hear them - [open an issue](https://github.com/PabloCSScobar/ledsplay/issues).
>
> The **custom PCB** (see the other build below) was designed by a professional hardware engineer.

You can put this build together your own way - design your own enclosure or adapt a stock Pi case to fit your needs. The two status LEDs and the standby button are completely optional - the device and the app run perfectly without them.

For the LED strip and status LEDs, no soldering is needed - wrap each wire around its GPIO pin and secure it with heat-shrink tubing. The standby button usually needs its wires soldered to the contacts, unless you pick a model with screw terminals or a pre-wired breakout board.

<p align="center">
  <img src="assets/setup/diy-build-overview.jpg" alt="DIY build - everything laid out" width="600">
</p>

<p align="center"><em>Everything laid out: Raspberry Pi Zero 2W, WS2812B strip, USB MIDI cable, power supply. Optional: 2 status LEDs and a standby button.</em></p>

**Wiring** - which Pi pin goes where:

| Component | Wire | Raspberry Pi pin |
|-----------|------|------------------|
| LED strip | DIN (data) | **GPIO 18** |
| LED strip | +5V | **5V** |
| LED strip | GND | **GND** |
| Status LEDs *(optional)* | DIN (data) | **GPIO 21** (daisy-chained: LED #1 DOUT → LED #2 DIN) |
| Status LEDs *(optional)* | +5V | **5V** |
| Status LEDs *(optional)* | GND | **GND** |
| Standby button *(optional)* | one leg | **GPIO 17** |
| Standby button *(optional)* | other leg | **GND** |

Then plug your piano into any USB port on the Pi.

<p align="center">
  <img src="assets/setup/diy-build-gpio-closeup.jpg" alt="Close-up of GPIO wiring" width="600">
</p>

<p align="center"><em>Close-up of the GPIO header with all wires connected - LED strip, two status LEDs, and the standby button.</em></p>

**Build examples**

A few different ways the DIY build can be put together:

<table align="center">
<tr>
<td valign="top" width="50%">
  <img src="assets/setup/diy-stock-case-closed.jpg" alt="Pi Zero in a stock case with drilled holes" width="100%"><br>
  <em>Pi Zero 2W in a generic plastic enclosure - holes drilled in the sides for the LED strip socket, USB MIDI, and power.</em>
</td>
<td valign="top" width="50%">
  <img src="assets/setup/diy-stock-case-open.png" alt="Inside view of the stock case" width="100%"><br>
  <em>Inside view of the same stock case - just the Pi, no PCB needed.</em>
</td>
</tr>
<tr>
<td valign="top" width="50%">
  <img src="assets/setup/diy-stock-case-on-piano.png" alt="Stock case build installed on piano" width="100%"><br>
  <em>The stock-case build mounted on the piano next to the LED strip.</em>
</td>
<td valign="top" width="50%">
  <img src="assets/setup/diy-build-pi4b.jpg" alt="Raspberry Pi 4B variant" width="100%"><br>
  <em>Raspberry Pi 4B variant with all optional extras connected: status LEDs, standby button, LED strip.</em>
</td>
</tr>
</table>

---

### Build with custom PCB and 3D case

A custom PCB and 3D-printed case sized for the Pi Zero 2W. Skips almost all of the wiring work - the only thing you need to do is swap the LED strip's end connector for a 3-pin JST plug so it fits the PCB socket. Everything else just snaps together: Pi onto the PCB, PCB into the case, lid on top.

> **PCB Gerber files and 3D case STLs** are included with the paid version. See [Free vs Paid](#free-vs-paid).

<p align="center">
  <img src="assets/setup/pcb-build-exploded.jpg" alt="PCB build - exploded view" width="600">
</p>

<p align="center"><em>What's in the kit: 3D-printed case parts, custom PCB, Raspberry Pi Zero 2W.</em></p>

<table align="center"><tr>
<td valign="top">
  <img src="assets/setup/pcb-build-assembled.jpg" alt="PCB + Pi inside the open case" width="320"><br>
  <em>Pi snaps into the PCB, which sits inside the case.</em>
</td>
<td valign="top">
  <img src="assets/setup/pcb-build-closed.jpg" alt="Closed case" width="320"><br>
  <em>Closed case with a piano-key relief on the lid.</em>
</td>
</tr></table>

<p align="center">
  <img src="assets/setup/jst-connector.jpg" alt="JST 3-pin connector" width="450">
</p>

<p align="center"><em>To connect the LED strip to the custom PCB, its end has to be terminated with a 3-pin JST plug.</em></p>

<p align="center">
  <img src="assets/setup/pcb-build-on-piano-lit.jpg" alt="LEDsplay running on a Roland FP-30" width="700">
</p>

<p align="center"><em>Installed on a Roland FP-30 - LED strip running across the keys.</em></p>

---

## Installation

There are two ways to install LEDsplay:

---

### Option 1 - Script install
Install on any fresh Raspberry Pi OS. Works on all Pi models.

**1. Flash Raspberry Pi OS Lite** onto a microSD card. You can use [Raspberry Pi Imager](https://www.raspberrypi.com/software/) or any other tool. If using Raspberry Pi Imager, open the settings and configure:
- **Hostname:** `ledsplay` - this lets you reach the Pi at `ledsplay.local`
- **WiFi credentials** - so the Pi connects to your network on first boot
- **Enable SSH** - so you can log in remotely without a monitor

**2. Boot the Pi and connect via SSH:**

```bash
ssh pi@ledsplay.local
# or use the IP address assigned by your router
```

**3. Run the setup script:**

```bash
curl -fsSL https://raw.githubusercontent.com/PabloCSScobar/ledsplay/main/setup.sh | sudo bash
```

This downloads the latest release from GitHub, installs all dependencies, and configures the system. **On Raspberry Pi Zero 2W, setup takes ~15 minutes** - most of that is installing Python packages.

**4. Reboot** if prompted.

**5. Done.** If everything is connected correctly, the LED strip will show a startup animation. Open **http://ledsplay.local** in your browser to access the app.

<details>
<summary>What the installer does</summary>

- Downloads the latest release from GitHub
- Installs system dependencies (Python 3, GPIO libraries, MIDI tools)
- Sets up a Python virtual environment at `/opt/ledsplay/`
- Configures GPIO and SPI for LED control
- Pre-generates MusicXML cache for bundled demo songs
- Creates a systemd service (`ledsplay.service`) that starts on boot
- Full log at `/var/log/ledsplay-setup.log`

</details>

---

### Option 2 - Pre-built image

Download a ready-to-use system image - Raspberry Pi OS Lite with LEDsplay already installed. No SSH or terminal needed.

**1. Download the latest image** from the [Releases page](https://github.com/PabloCSScobar/ledsplay/releases/latest).

**2. Flash it** using [Raspberry Pi Imager](https://www.raspberrypi.com/software/): instead of choosing a system from the list, select **"Use custom"** and pick the downloaded image file.

**3. Boot the Raspberry Pi.** If everything is connected, the LED strip will show a startup animation.

**4. Connect to the LEDsplay hotspot** from your phone, tablet, or PC:

| | |
|---|---|
| **SSID** | `LEDsplay-Setup` |
| **Password** | `ledsplay` |

**5. Configure WiFi:** Open **http://ledsplay.local** in your browser. Tap the **More** icon at the bottom → go to **Network settings** → select your home WiFi network and connect. After a few seconds the `LEDsplay-Setup` hotspot will turn off and the Pi will join your network.

**6. Done.** Open **http://ledsplay.local** - you're in.

---

## Updating

Updates are available through the web interface: **System > Updates**.

The app checks for new releases from this repository and performs safe updates with automatic rollback.

<details>
<summary>Manual update</summary>

```bash
sudo /opt/ledsplay/venv/bin/python3 /opt/ledsplay/updater.py update
```

</details>

---

## Power & brightness

LEDsplay is designed to run on a single shared power supply for both the Raspberry Pi and the LED strip. Brightness is managed in software to stay within safe power limits:

- Key brightness: max 30%
- Background brightness: max 25%

These values provide vivid, clearly visible lighting while keeping power draw well within the supply's capacity.

---

## Service management

```bash
sudo systemctl status ledsplay.service     # Check status
sudo systemctl restart ledsplay.service    # Restart
sudo journalctl -u ledsplay.service -f     # View logs
```

---

## Status LEDs

LEDsplay supports 2 small indicator LEDs (GPIO pin 21) to show system state at a glance. They are optional - the app works without them.

| Color / animation | Meaning |
|---|---|
| 🔴 Red (solid) | System starting up |
| 🟢 Green (solid) | Ready - everything OK |
| 🔵 Blue (pulsing) | WiFi hotspot active - waiting for network setup |
| 🟡 Yellow (pulsing) | No MIDI device detected |
| 🟢🔵🟣 Cycling | LED animation or screensaver running |
| ⚫ Off | Status LEDs disabled in settings |

Color and brightness can be customised under **System > Status LEDs** in the app.

---

## Feedback & support

LEDsplay is actively developed - new features and fixes ship regularly. Found a bug or have an idea? [Open an issue](https://github.com/PabloCSScobar/ledsplay/issues) - all reports and suggestions are welcome, and I do my best to look at every one.

Need support for another language? Open an issue - I'd love to add it. The app currently supports **English** and **Polish**.

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Hardware | Raspberry Pi + WS281x LED strip + MIDI USB |
| Backend | Python, Flask, SocketIO |
| Frontend | Angular + Ionic |
| Communication | WebSocket + REST API |

---

## License

LEDsplay is proprietary software. Free tier available at no cost. See [pricing](#free-vs-paid) for details.
