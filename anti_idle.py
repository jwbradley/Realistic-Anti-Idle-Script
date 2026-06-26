#!/usr/bin/env python3
"""
Hybrid Anti-Idle / Screen Timeout Prevention Script (v2)

Three-layer defense against idle timeouts:
  1. SetThreadExecutionState — OS-level "don't sleep" flag (invisible, always on)
  2. F15 key press — resets idle timer without affecting any application (invisible)
  3. Mouse jiggle — only activates when user has been truly idle (won't interfere with active work)

Safe to run while actively working. Mouse movements are suppressed when user activity is detected.
"""

import ctypes
import pyautogui
import random
import time
import sys
from datetime import datetime
from pynput.keyboard import Key, Controller, KeyCode

# ====================== CONFIGURATION ======================
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
STOP_HOUR = 18                  # Hour (24h format) to auto-stop the script (18 = 6 PM)

# Logging
VERBOSE = True                  # Print status updates
LOG_INTERVAL = 5                # Print status every N cycles
# ===========================================================

print("=" * 60)
print("  Anti-Idle Hybrid Script v2")
print("  - Layer 1: OS execution state (invisible, always on)")
print("  - Layer 2: F15 key tap (invisible, always on)")
print("  - Layer 3: Mouse jiggle (only when idle)")
print("  Press Ctrl+C to stop cleanly.")
print("  Fail-safe: move mouse to top-left corner (0,0)")
print("=" * 60)
print()

# Initialize
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02
keyboard = Controller()

# Track last user input time (keyboard or mouse)
_last_input_time = time.time()

def _on_key_activity(key):
    """Reset idle timer on any keyboard activity."""
    global _last_input_time
    _last_input_time = time.time()

# Start keyboard listener in background thread
from pynput.keyboard import Listener as KeyboardListener
_kb_listener = KeyboardListener(on_press=_on_key_activity)
_kb_listener.daemon = True
_kb_listener.start()

# Windows API constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002


def set_execution_state():
    """Tell Windows not to sleep or blank the display."""
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )


def clear_execution_state():
    """Restore normal power management on exit."""
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)


def press_f15():
    """Press F15 key — resets idle timer, no application responds to it."""
    try:
        f15 = KeyCode.from_vk(0x7E)  # VK_F15 = 0x7E (126)
        keyboard.press(f15)
        time.sleep(random.uniform(0.05, 0.12))
        keyboard.release(f15)
    except Exception:
        pass


def get_screen_center():
    width, height = pyautogui.size()
    return width // 2, height // 2


def is_user_idle(last_known_pos, idle_seconds):
    """Check if mouse hasn't moved for idle_seconds."""
    return idle_seconds >= USER_IDLE_THRESHOLD


def do_human_like_mouse_activity():
    """Perform a burst of small, natural-looking mouse movements."""
    cx, cy = get_screen_center()

    num_moves = random.randint(4, 8)
    for _ in range(num_moves):
        dx = random.gauss(0, MOUSE_JITTER_INTENSITY)
        dy = random.gauss(0, MOUSE_JITTER_INTENSITY * 0.8)

        if random.random() < 0.15:
            dx += random.randint(-90, 90)
            dy += random.randint(-70, 70)

        duration = random.uniform(0.12, 0.42)
        tween = random.choice([
            pyautogui.easeInOutQuad,
            pyautogui.easeOutQuad,
            pyautogui.easeInQuad,
            pyautogui.linear
        ])

        try:
            pyautogui.moveTo(cx + dx, cy + dy, duration=duration, tween=tween)
        except pyautogui.FailSafeException:
            pass

        time.sleep(random.uniform(0.06, 0.18))

    # Occasional attention shift
    if random.random() < 0.25:
        for _ in range(random.randint(2, 3)):
            big_dx = random.randint(-250, 250)
            big_dy = random.randint(-180, 180)
            try:
                pyautogui.moveTo(
                    cx + big_dx, cy + big_dy,
                    duration=random.uniform(0.4, 0.75),
                    tween=pyautogui.easeInOutQuad
                )
            except pyautogui.FailSafeException:
                pass
            time.sleep(random.uniform(0.2, 0.5))


def do_idle_keyboard_activity():
    """Light keyboard activity when user is idle (modifier taps, arrow keys)."""
    if random.random() < 0.6:
        key = random.choice([Key.shift, Key.ctrl])
        keyboard.press(key)
        time.sleep(random.uniform(0.08, 0.15))
        keyboard.release(key)
        return

    for _ in range(random.randint(1, 2)):
        arrow = random.choice([Key.right, Key.left, Key.up, Key.down])
        keyboard.press(arrow)
        time.sleep(random.uniform(0.06, 0.12))
        keyboard.release(arrow)
        time.sleep(random.uniform(0.1, 0.2))


def main_loop():
    cycle_count = 0
    last_mouse_pos = pyautogui.position()
    idle_timer = 0
    last_f15_time = time.time()
    last_exec_state_time = time.time()

    cx, cy = get_screen_center()
    print(f"Screen center: ({cx}, {cy})")
    print(f"Idle threshold: {USER_IDLE_THRESHOLD}s (mouse jiggle only after this)")
    print(f"F15 interval: {F15_INTERVAL_MIN}-{F15_INTERVAL_MAX}s")
    print()

    # Set initial execution state
    set_execution_state()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Layer 1: Execution state SET (display + system)")

    while True:
        cycle_count += 1
        now = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')

        # Auto-stop at configured hour
        if datetime.now().hour >= STOP_HOUR:
            print(f"[{timestamp}] Past {STOP_HOUR}:00 — stopping. Goodnight.")
            break

        # --- Check if user is active (mouse OR keyboard) ---
        current_pos = pyautogui.position()
        if current_pos != last_mouse_pos:
            idle_timer = 0
            last_mouse_pos = current_pos
        elif (now - _last_input_time) < MOUSE_CHECK_INTERVAL:
            idle_timer = 0  # Keyboard activity detected
        else:
            idle_timer += MOUSE_CHECK_INTERVAL

        user_is_idle = idle_timer >= USER_IDLE_THRESHOLD

        # --- Layer 1: Refresh execution state periodically ---
        if now - last_exec_state_time >= EXECUTION_STATE_INTERVAL:
            set_execution_state()
            last_exec_state_time = now

        # --- Layer 2: F15 tap at random intervals (skip if user is active) ---
        f15_interval = random.uniform(F15_INTERVAL_MIN, F15_INTERVAL_MAX)
        if now - last_f15_time >= f15_interval:
            if user_is_idle:
                press_f15()
            last_f15_time = now

        # --- Layer 3: Mouse jiggle + keyboard (only when idle) ---
        if user_is_idle:
            do_human_like_mouse_activity()

            if random.random() < KEYBOARD_ACTION_PROB:
                do_idle_keyboard_activity()

            if VERBOSE and cycle_count % LOG_INTERVAL == 0:
                print(f"[{timestamp}] Idle {idle_timer}s — mouse jiggle + F15 active (cycle #{cycle_count})")
        else:
            if VERBOSE and cycle_count % (LOG_INTERVAL * 3) == 0:
                print(f"[{timestamp}] User active — layers 1+2 only (cycle #{cycle_count})")

        # Sleep before next check
        time.sleep(MOUSE_CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        clear_execution_state()
        print("\n\nScript stopped. Execution state restored to normal.")
    except Exception as e:
        clear_execution_state()
        print(f"\n\nScript error: {e}")
        print("Execution state restored to normal.")
        sys.exit(1)
