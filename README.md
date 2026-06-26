# 🖥️ Anti-Idle / Screen Timeout Prevention Script (v2 — Hybrid)

Three-layer defense against system idle timeouts and screen locks. Safe to run while actively working — mouse movements are suppressed when user activity is detected.

---

## How It Works

| Layer | Method | When Active | User Impact |
|-------|--------|-------------|-------------|
| 1 | `SetThreadExecutionState` | Always (every 55s) | Zero — invisible OS-level flag |
| 2 | F15 key press | Always (every 60-90s) | Zero — no application responds to F15 |
| 3 | Mouse jiggle + keyboard | Only when idle (120s+ no movement) | None while you're working |

**You can leave this running 24/7 while actively working.** The script detects your mouse activity and only engages visible actions (layer 3) after you've been away for 2+ minutes.

---

## Why Three Layers?

- **Layer 1 (OS flag):** What video players use to keep the screen on. Tells Windows "don't sleep, don't blank." Invisible, no input simulation.
- **Layer 2 (F15):** Resets the Windows idle timer at the HID level. F15 exists in the keyboard spec but no application uses it — completely invisible even if you're mid-typing.
- **Layer 3 (Mouse jiggle):** For the most aggressive corporate monitoring tools that require actual mouse/keyboard HID events. Only fires when you're genuinely away.

---

## Requirements

```bash
pip install pyautogui pynput
```

| Package | Purpose |
|---------|---------|
| `pyautogui` | Mouse movement with easing/tweening |
| `pynput` | Keyboard input simulation (F15) + keyboard activity listener (idle detection) |
| `ctypes` | Windows API access (built-in, no install needed) |

### Platform

- **Windows only** — uses `SetThreadExecutionState` and VK_F15 (0x7E)
- Python 3.7+

---

## Installation

```bash
pip install pyautogui pynput
```

---

## Usage

```bash
# Start (runs until Ctrl+C)
python anti_idle.py

# Run minimized in background
start /MIN python anti_idle.py

# Run completely hidden (no console window)
pythonw anti_idle.py
```

### Emergency Stop

- **Ctrl+C** in the terminal — graceful shutdown, restores normal power management
- **Move mouse to top-left corner (0,0)** — PyAutoGUI fail-safe kills the script instantly

On exit, the script always calls `clear_execution_state()` to restore normal Windows power management.

---

## Configuration

```python
# Layer 1: OS-level (always active, invisible)
EXECUTION_STATE_INTERVAL = 55   # Seconds between SetThreadExecutionState refreshes

# Layer 2: F15 key (always active, invisible)
F15_INTERVAL_MIN = 60           # Minimum seconds between F15 taps
F15_INTERVAL_MAX = 90           # Maximum seconds between F15 taps

# Layer 3: Mouse jiggle (only when user is idle)
USER_IDLE_THRESHOLD = 120       # Seconds of no mouse movement before jiggle activates
MOUSE_CHECK_INTERVAL = 10      # How often to check if user moved the mouse
MOUSE_JITTER_INTENSITY = 35     # Average size of small movements (pixels)

# Optional keyboard simulation (beyond F15)
ENABLE_KEYBOARD_TYPING = False  # Only set True if you control the focused window
KEYBOARD_ACTION_PROB = 0.20     # Chance of arrow key/modifier activity when idle

# Auto-stop
STOP_HOUR = 18                  # Hour (24h format) to auto-stop (18 = 6 PM, 0 = disabled)
```

### Recommended Settings by Scenario

| Scenario | Idle Threshold | F15 Interval | Jiggle Intensity | Stop Hour |
|----------|---------------|-------------|------------------|-----------|
| Standard (5-min timeout) | 120s | 60-90s | 35 | 18 (6 PM) |
| Aggressive (2-min timeout) | 60s | 30-45s | 25 | 18 |
| Relaxed (10-min timeout) | 180s | 60-90s | 40 | 19 (7 PM) |
| Night shift | 120s | 60-90s | 35 | 23 (11 PM) |
| No auto-stop | 120s | 60-90s | 35 | 0 (disabled) |

---

## Idle Detection Logic

```
Every 10 seconds:
  ├── Check mouse position
  ├── Check keyboard listener (any keypress resets timer)
  ├── If mouse moved OR key pressed → reset idle timer (user is active)
  │   └── Only Layer 1 fires (OS flag — completely invisible)
  └── If no mouse AND no keyboard for 120s → user is idle
      └── All three layers fire (F15 + mouse jiggle)
```

This means:
- **Typing (mouse still):** Script detects keyboard activity — stays silent. No F15, no jiggle.
- **Moving the mouse:** Script detects mouse movement — stays silent.
- **On another monitor:** No mouse or keyboard detected on this machine → after 2 min, F15 + jiggle kick in.
- **Away from desk:** Full protection (all layers) within 2 minutes of leaving.
- **Only Layer 1 (SetThreadExecutionState) runs while you're active** — it's a pure OS flag with zero observable behavior.

---

## Output

```
============================================================
  Anti-Idle Hybrid Script v2
  - Layer 1: OS execution state (invisible, always on)
  - Layer 2: F15 key tap (invisible, always on)
  - Layer 3: Mouse jiggle (only when idle)
  Press Ctrl+C to stop cleanly.
  Fail-safe: move mouse to top-left corner (0,0)
============================================================

Screen center: (960, 540)
Idle threshold: 120s (mouse jiggle only after this)
F15 interval: 60-90s

[09:15:23] Layer 1: Execution state SET (display + system)
[09:17:30] User active — layers 1+2 only (cycle #45)
[09:22:10] Idle 130s — mouse jiggle + F15 active (cycle #75)
[09:25:40] User active — layers 1+2 only (cycle #96)
```

---

## Safety Features

| Feature | Description |
|---------|-------------|
| **Idle detection** | Mouse jiggle + F15 only fire after 120s of no mouse AND no keyboard activity |
| **Keyboard listener** | Background thread detects any keypress and resets idle timer — typing keeps you "active" |
| **Fail-safe corner** | Moving mouse to (0,0) instantly kills the script |
| **Clean exit** | Ctrl+C restores normal power management before stopping |
| **Error recovery** | Any uncaught exception also restores power management |
| **No typing by default** | `ENABLE_KEYBOARD_TYPING=False` prevents accidental input |
| **F15 is invisible** | No application in existence responds to F15 — safe during typing |
| **Execution state restored** | Script always cleans up — your laptop will sleep normally after stopping |
| **Auto-stop timer** | Automatically exits at configured hour (default 6 PM) — no need to remember to kill it |

---

## What Each Layer Defeats

| Threat | Layer 1 (OS) | Layer 2 (F15) | Layer 3 (Mouse) |
|--------|:---:|:---:|:---:|
| Windows screen blank | Yes | Yes | Yes |
| Windows lock screen | Yes | Yes | Yes |
| Teams/Slack "Away" status | No | Yes | Yes |
| HID-based idle monitoring | No | Yes | Yes |
| Corporate DLP mouse tracking | No | No | Yes |
| "Last input" timestamp checks | No | Yes | Yes |

---

## Running on Startup

### Windows Task Scheduler

1. Open Task Scheduler → Create Basic Task
2. Trigger: "At log on"
3. Action: Start a program
   - Program: `pythonw.exe` (no console window)
   - Arguments: `C:\Users\DT17787\anti_idle.py`
4. Conditions: Uncheck "Start only if on AC power"

### Simple Startup Folder

1. Press `Win+R` → type `shell:startup` → Enter
2. Create a shortcut to: `pythonw.exe C:\Users\DT17787\anti_idle.py`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: pyautogui` | `pip install pyautogui pynput` |
| Mouse jiggling while I'm working | Should not happen — keyboard + mouse detection prevents it. Increase `USER_IDLE_THRESHOLD` if needed |
| F15 firing while typing | Should not happen in v2 — F15 only fires when idle. Check that `pynput` keyboard listener started |
| Screen still blanks | Check if Group Policy overrides execution state; F15 should still help |
| Teams still shows "Away" | Reduce `F15_INTERVAL_MAX` to 45s |
| Script killed on exit but screen won't sleep | Run `python -c "import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)"` to reset |
| F15 not working | Some keyboards don't support VK 0x7E; the other layers compensate |
| Laptop still sleeps on battery | Task Scheduler condition "Start only if on AC power" may be checked |
| Keyboard listener not detecting activity | Ensure `pynput` has accessibility permissions (macOS) or is running as same user |

---

## Comparison to v1

| Feature | v1 | v2 (Hybrid) |
|---------|-----|-------------|
| Safe while working | No (mouse moves randomly) | Yes (keyboard + mouse idle detection) |
| Detects keyboard activity | No | Yes (background listener resets idle timer) |
| Invisible layers | No | Yes (OS flag always; F15 only when idle) |
| Works on other monitor | No (needs mouse on screen) | Yes (OS flag always active) |
| Works away from desk | Yes | Yes (all layers after 120s no input) |
| Restores power management on exit | No | Yes |
| Defeats Teams "Away" | Yes (mouse) | Yes (F15 + mouse when idle) |
| Auto-stop at end of day | No | Yes (configurable STOP_HOUR) |

---

## Warnings

- Use responsibly and in compliance with your organization's policies
- `ENABLE_KEYBOARD_TYPING=True` will type into the focused window — leave it off
- The script modifies Windows power management state — always exit cleanly (Ctrl+C)
- If the script crashes without cleanup, run: `python -c "import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)"`

---

## License

Personal use. Use responsibly.

Three-layer defense against system idle timeouts and screen locks. Safe to run while actively working — mouse movements are suppressed when user activity is detected.

---

## How It Works

| Layer | Method | When Active | User Impact |
|-------|--------|-------------|-------------|
| 1 | `SetThreadExecutionState` | Always (every 55s) | Zero — invisible OS-level flag |
| 2 | F15 key press | Always (every 60-90s) | Zero — no application responds to F15 |
| 3 | Mouse jiggle + keyboard | Only when idle (120s+ no movement) | None while you're working |

**You can leave this running 24/7 while actively working.** The script detects your mouse activity and only engages visible actions (layer 3) after you've been away for 2+ minutes.

---

## Why Three Layers?

- **Layer 1 (OS flag):** What video players use to keep the screen on. Tells Windows "don't sleep, don't blank." Invisible, no input simulation.
- **Layer 2 (F15):** Resets the Windows idle timer at the HID level. F15 exists in the keyboard spec but no application uses it — completely invisible even if you're mid-typing.
- **Layer 3 (Mouse jiggle):** For the most aggressive corporate monitoring tools that require actual mouse/keyboard HID events. Only fires when you're genuinely away.

---

## Requirements

```bash
pip install pyautogui pynput
```

| Package | Purpose |
|---------|---------|
| `pyautogui` | Mouse movement with easing/tweening |
| `pynput` | Keyboard input simulation (F15, modifier keys) |
| `ctypes` | Windows API access (built-in, no install needed) |

### Platform

- **Windows only** — uses `SetThreadExecutionState` and VK_F15 (0x7E)
- Python 3.7+

---

## Installation

```bash
pip install pyautogui pynput
```

---

## Usage

```bash
# Start (runs until Ctrl+C)
python anti_idle.py

# Run minimized in background
start /MIN python anti_idle.py

# Run completely hidden (no console window)
pythonw anti_idle.py
```

### Emergency Stop

- **Ctrl+C** in the terminal — graceful shutdown, restores normal power management
- **Move mouse to top-left corner (0,0)** — PyAutoGUI fail-safe kills the script instantly

On exit, the script always calls `clear_execution_state()` to restore normal Windows power management.

---

## Configuration

```python
# Layer 1: OS-level (always active, invisible)
EXECUTION_STATE_INTERVAL = 55   # Seconds between SetThreadExecutionState refreshes

# Layer 2: F15 key (always active, invisible)
F15_INTERVAL_MIN = 60           # Minimum seconds between F15 taps
F15_INTERVAL_MAX = 90           # Maximum seconds between F15 taps

# Layer 3: Mouse jiggle (only when user is idle)
USER_IDLE_THRESHOLD = 120       # Seconds of no mouse movement before jiggle activates
MOUSE_CHECK_INTERVAL = 10      # How often to check if user moved the mouse
MOUSE_JITTER_INTENSITY = 35     # Average size of small movements (pixels)

# Optional keyboard simulation (beyond F15)
ENABLE_KEYBOARD_TYPING = False  # Only set True if you control the focused window
KEYBOARD_ACTION_PROB = 0.20     # Chance of arrow key/modifier activity when idle

# Auto-stop
STOP_HOUR = 18                  # Hour (24h format) to auto-stop (18 = 6 PM, 0 = disabled)
```

### Recommended Settings by Scenario

| Scenario | Idle Threshold | F15 Interval | Jiggle Intensity | Stop Hour |
|----------|---------------|-------------|------------------|-----------|
| Standard (5-min timeout) | 120s | 60-90s | 35 | 18 (6 PM) |
| Aggressive (2-min timeout) | 60s | 30-45s | 25 | 18 |
| Relaxed (10-min timeout) | 180s | 60-90s | 40 | 19 (7 PM) |
| Night shift | 120s | 60-90s | 35 | 23 (11 PM) |
| No auto-stop | 120s | 60-90s | 35 | 0 (disabled) |

---

## Idle Detection Logic

```
Every 10 seconds:
  ├── Check mouse position
  ├── If moved → reset idle timer (user is active)
  │   └── Only layers 1 + 2 fire (invisible)
  └── If same position for 120s → user is idle
      └── All three layers fire (including mouse jiggle)
```

This means:
- **Working at your desk:** Script is invisible. F15 and execution state keep the system alive.
- **On another monitor:** Mouse hasn't moved on this screen → after 2 min, jiggle kicks in.
- **Away from desk:** Full protection (all layers) within 2 minutes of leaving.

---

## Output

```
============================================================
  Anti-Idle Hybrid Script v2
  - Layer 1: OS execution state (invisible, always on)
  - Layer 2: F15 key tap (invisible, always on)
  - Layer 3: Mouse jiggle (only when idle)
  Press Ctrl+C to stop cleanly.
  Fail-safe: move mouse to top-left corner (0,0)
============================================================

Screen center: (960, 540)
Idle threshold: 120s (mouse jiggle only after this)
F15 interval: 60-90s

[09:15:23] Layer 1: Execution state SET (display + system)
[09:17:30] User active — layers 1+2 only (cycle #45)
[09:22:10] Idle 130s — mouse jiggle + F15 active (cycle #75)
[09:25:40] User active — layers 1+2 only (cycle #96)
```

---

## Safety Features

| Feature | Description |
|---------|-------------|
| **Idle detection** | Mouse jiggle only fires after 120s of no movement — never interferes with active work |
| **Fail-safe corner** | Moving mouse to (0,0) instantly kills the script |
| **Clean exit** | Ctrl+C restores normal power management before stopping |
| **Error recovery** | Any uncaught exception also restores power management |
| **No typing by default** | `ENABLE_KEYBOARD_TYPING=False` prevents accidental input |
| **F15 is invisible** | No application in existence responds to F15 — safe during typing |
| **Execution state restored** | Script always cleans up — your laptop will sleep normally after stopping |
| **Auto-stop timer** | Automatically exits at configured hour (default 6 PM) — no need to remember to kill it |

---

## What Each Layer Defeats

| Threat | Layer 1 (OS) | Layer 2 (F15) | Layer 3 (Mouse) |
|--------|:---:|:---:|:---:|
| Windows screen blank | Yes | Yes | Yes |
| Windows lock screen | Yes | Yes | Yes |
| Teams/Slack "Away" status | No | Yes | Yes |
| HID-based idle monitoring | No | Yes | Yes |
| Corporate DLP mouse tracking | No | No | Yes |
| "Last input" timestamp checks | No | Yes | Yes |

---

## Running on Startup

### Windows Task Scheduler

1. Open Task Scheduler → Create Basic Task
2. Trigger: "At log on"
3. Action: Start a program
   - Program: `pythonw.exe` (no console window)
   - Arguments: `C:\Users\DT17787\anti_idle.py`
4. Conditions: Uncheck "Start only if on AC power"

### Simple Startup Folder

1. Press `Win+R` → type `shell:startup` → Enter
2. Create a shortcut to: `pythonw.exe C:\Users\DT17787\anti_idle.py`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: pyautogui` | `pip install pyautogui pynput` |
| Mouse jiggling while I'm working | Increase `USER_IDLE_THRESHOLD` (default 120s) |
| Screen still blanks | Check if Group Policy overrides execution state; F15 should still help |
| Teams still shows "Away" | Reduce `F15_INTERVAL_MAX` to 45s |
| Script killed on exit but screen won't sleep | Run `python -c "import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)"` to reset |
| F15 not working | Some keyboards don't support VK 0x7E; the other layers compensate |
| Laptop still sleeps on battery | Task Scheduler condition "Start only if on AC power" may be checked |

---

## Comparison to v1

| Feature | v1 | v2 (Hybrid) |
|---------|-----|-------------|
| Safe while working | No (mouse moves randomly) | Yes (idle detection) |
| Invisible layers | No | Yes (OS flag + F15) |
| Works on other monitor | No (needs mouse on screen) | Yes (F15 + OS flag always active) |
| Works away from desk | Yes | Yes (all layers after 120s) |
| Restores power management on exit | No | Yes |
| Defeats Teams "Away" | Yes (mouse) | Yes (F15 + mouse when idle) |

---

## Warnings

- Use responsibly and in compliance with your organization's policies
- `ENABLE_KEYBOARD_TYPING=True` will type into the focused window — leave it off
- The script modifies Windows power management state — always exit cleanly (Ctrl+C)
- If the script crashes without cleanup, run: `python -c "import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)"`

---

## License

Personal use. Use responsibly.

Three-layer defense against system idle timeouts and screen locks. Safe to run while actively working — mouse movements are suppressed when user activity is detected.

---

## How It Works

| Layer | Method | When Active | User Impact |
|-------|--------|-------------|-------------|
| 1 | `SetThreadExecutionState` | Always (every 55s) | Zero — invisible OS-level flag |
| 2 | F15 key press | Always (every 60-90s) | Zero — no application responds to F15 |
| 3 | Mouse jiggle + keyboard | Only when idle (120s+ no movement) | None while you're working |

**You can leave this running 24/7 while actively working.** The script detects your mouse activity and only engages visible actions (layer 3) after you've been away for 2+ minutes.

---

## Why Three Layers?

- **Layer 1 (OS flag):** What video players use to keep the screen on. Tells Windows "don't sleep, don't blank." Invisible, no input simulation.
- **Layer 2 (F15):** Resets the Windows idle timer at the HID level. F15 exists in the keyboard spec but no application uses it — completely invisible even if you're mid-typing.
- **Layer 3 (Mouse jiggle):** For the most aggressive corporate monitoring tools that require actual mouse/keyboard HID events. Only fires when you're genuinely away.

---

## Requirements

```bash
pip install pyautogui pynput
```

| Package | Purpose |
|---------|---------|
| `pyautogui` | Mouse movement with easing/tweening |
| `pynput` | Keyboard input simulation (F15, modifier keys) |
| `ctypes` | Windows API access (built-in, no install needed) |

### Platform

- **Windows only** — uses `SetThreadExecutionState` and VK_F15 (0x7E)
- Python 3.7+

---

## Installation

```bash
pip install pyautogui pynput
```

---

## Usage

```bash
# Start (runs until Ctrl+C)
python anti_idle.py

# Run minimized in background
start /MIN python anti_idle.py

# Run completely hidden (no console window)
pythonw anti_idle.py
```

### Emergency Stop

- **Ctrl+C** in the terminal — graceful shutdown, restores normal power management
- **Move mouse to top-left corner (0,0)** — PyAutoGUI fail-safe kills the script instantly

On exit, the script always calls `clear_execution_state()` to restore normal Windows power management.

---

## Configuration

```python
# Layer 1: OS-level (always active, invisible)
EXECUTION_STATE_INTERVAL = 55   # Seconds between SetThreadExecutionState refreshes

# Layer 2: F15 key (always active, invisible)
F15_INTERVAL_MIN = 60           # Minimum seconds between F15 taps
F15_INTERVAL_MAX = 90           # Maximum seconds between F15 taps

# Layer 3: Mouse jiggle (only when user is idle)
USER_IDLE_THRESHOLD = 120       # Seconds of no mouse movement before jiggle activates
MOUSE_CHECK_INTERVAL = 10      # How often to check if user moved the mouse
MOUSE_JITTER_INTENSITY = 35     # Average size of small movements (pixels)

# Optional keyboard simulation (beyond F15)
ENABLE_KEYBOARD_TYPING = False  # Only set True if you control the focused window
KEYBOARD_ACTION_PROB = 0.20     # Chance of arrow key/modifier activity when idle
```

### Recommended Settings by Scenario

| Scenario | Idle Threshold | F15 Interval | Jiggle Intensity |
|----------|---------------|-------------|------------------|
| Standard (5-min timeout) | 120s | 60-90s | 35 |
| Aggressive (2-min timeout) | 60s | 30-45s | 25 |
| Relaxed (10-min timeout) | 180s | 60-90s | 40 |
| Maximum stealth | 120s | 55-75s | 20 |

---

## Idle Detection Logic

```
Every 10 seconds:
  ├── Check mouse position
  ├── If moved → reset idle timer (user is active)
  │   └── Only layers 1 + 2 fire (invisible)
  └── If same position for 120s → user is idle
      └── All three layers fire (including mouse jiggle)
```

This means:
- **Working at your desk:** Script is invisible. F15 and execution state keep the system alive.
- **On another monitor:** Mouse hasn't moved on this screen → after 2 min, jiggle kicks in.
- **Away from desk:** Full protection (all layers) within 2 minutes of leaving.

---

## Output

```
============================================================
  Anti-Idle Hybrid Script v2
  - Layer 1: OS execution state (invisible, always on)
  - Layer 2: F15 key tap (invisible, always on)
  - Layer 3: Mouse jiggle (only when idle)
  Press Ctrl+C to stop cleanly.
  Fail-safe: move mouse to top-left corner (0,0)
============================================================

Screen center: (960, 540)
Idle threshold: 120s (mouse jiggle only after this)
F15 interval: 60-90s

[09:15:23] Layer 1: Execution state SET (display + system)
[09:17:30] User active — layers 1+2 only (cycle #45)
[09:22:10] Idle 130s — mouse jiggle + F15 active (cycle #75)
[09:25:40] User active — layers 1+2 only (cycle #96)
```

---

## Safety Features

| Feature | Description |
|---------|-------------|
| **Idle detection** | Mouse jiggle only fires after 120s of no movement — never interferes with active work |
| **Fail-safe corner** | Moving mouse to (0,0) instantly kills the script |
| **Clean exit** | Ctrl+C restores normal power management before stopping |
| **Error recovery** | Any uncaught exception also restores power management |
| **No typing by default** | `ENABLE_KEYBOARD_TYPING=False` prevents accidental input |
| **F15 is invisible** | No application in existence responds to F15 — safe during typing |
| **Execution state restored** | Script always cleans up — your laptop will sleep normally after stopping |

---

## What Each Layer Defeats

| Threat | Layer 1 (OS) | Layer 2 (F15) | Layer 3 (Mouse) |
|--------|:---:|:---:|:---:|
| Windows screen blank | Yes | Yes | Yes |
| Windows lock screen | Yes | Yes | Yes |
| Teams/Slack "Away" status | No | Yes | Yes |
| HID-based idle monitoring | No | Yes | Yes |
| Corporate DLP mouse tracking | No | No | Yes |
| "Last input" timestamp checks | No | Yes | Yes |

---

## Running on Startup

### Windows Task Scheduler

1. Open Task Scheduler → Create Basic Task
2. Trigger: "At log on"
3. Action: Start a program
   - Program: `pythonw.exe` (no console window)
   - Arguments: `C:\Users\DT17787\anti_idle.py`
4. Conditions: Uncheck "Start only if on AC power"

### Simple Startup Folder

1. Press `Win+R` → type `shell:startup` → Enter
2. Create a shortcut to: `pythonw.exe C:\Users\DT17787\anti_idle.py`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: pyautogui` | `pip install pyautogui pynput` |
| Mouse jiggling while I'm working | Increase `USER_IDLE_THRESHOLD` (default 120s) |
| Screen still blanks | Check if Group Policy overrides execution state; F15 should still help |
| Teams still shows "Away" | Reduce `F15_INTERVAL_MAX` to 45s |
| Script killed on exit but screen won't sleep | Run `python -c "import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)"` to reset |
| F15 not working | Some keyboards don't support VK 0x7E; the other layers compensate |
| Laptop still sleeps on battery | Task Scheduler condition "Start only if on AC power" may be checked |

---

## Comparison to v1

| Feature | v1 | v2 (Hybrid) |
|---------|-----|-------------|
| Safe while working | No (mouse moves randomly) | Yes (idle detection) |
| Invisible layers | No | Yes (OS flag + F15) |
| Works on other monitor | No (needs mouse on screen) | Yes (F15 + OS flag always active) |
| Works away from desk | Yes | Yes (all layers after 120s) |
| Restores power management on exit | No | Yes |
| Defeats Teams "Away" | Yes (mouse) | Yes (F15 + mouse when idle) |

---

## Warnings

- Use responsibly and in compliance with your organization's policies
- `ENABLE_KEYBOARD_TYPING=True` will type into the focused window — leave it off
- The script modifies Windows power management state — always exit cleanly (Ctrl+C)
- If the script crashes without cleanup, run: `python -c "import ctypes; ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)"`

---

## License

Personal use. Use responsibly.
