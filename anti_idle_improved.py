#!/usr/bin/env python3
"""
Realistic Anti-Idle / Screen Timeout Prevention Script
Generates human-like mouse and keyboard activity to prevent idle timeouts
while being much harder to detect than traditional scripts.
"""

import pyautogui
import random
import time
from datetime import datetime
from pynput.keyboard import Key, Controller

# ====================== CONFIGURATION ======================
ACTIVITY_INTERVAL_MIN = 60      # Minimum seconds between activity bursts
ACTIVITY_INTERVAL_MAX = 240     # Maximum seconds between activity bursts

MOUSE_JITTER_INTENSITY = 35     # Average size of small movements (pixels)

ENABLE_KEYBOARD_TYPING = False  # ⚠️ Only set to True if you control the focused window
KEYBOARD_ACTION_PROB = 0.35     # Chance of doing keyboard activity each cycle (0.0 - 1.0)

print("Anti-idle script starting. Press Ctrl+C to stop cleanly.\n")
# ===========================================================

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02
keyboard = Controller()

def get_screen_center():
    width, height = pyautogui.size()
    return width // 2, height // 2

def do_human_like_mouse_activity():
    """Perform a burst of small, natural-looking mouse movements."""
    cx, cy = get_screen_center()

    # Small natural fidgets
    num_moves = random.randint(5, 12)
    for _ in range(num_moves):
        dx = random.gauss(0, MOUSE_JITTER_INTENSITY)
        dy = random.gauss(0, MOUSE_JITTER_INTENSITY * 0.8)

        if random.random() < 0.18:
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

        time.sleep(random.uniform(0.06, 0.22))

    # Occasional medium "attention shift"
    if random.random() < 0.28:
        for _ in range(random.randint(2, 4)):
            big_dx = random.randint(-280, 280)
            big_dy = random.randint(-200, 200)
            try:
                pyautogui.moveTo(
                    cx + big_dx, cy + big_dy,
                    duration=random.uniform(0.45, 0.85),
                    tween=pyautogui.easeInOutQuad
                )
            except pyautogui.FailSafeException:
                pass
            time.sleep(random.uniform(0.25, 0.6))

def do_keyboard_activity():
    """Perform occasional keyboard input."""
    if random.random() < 0.6:
        key = random.choice([Key.shift, Key.ctrl])
        keyboard.press(key)
        time.sleep(random.uniform(0.08, 0.18))
        keyboard.release(key)
        return

    if random.random() < 0.7:
        for _ in range(random.randint(1, 3)):
            arrow = random.choice([Key.right, Key.left, Key.up, Key.down])
            keyboard.press(arrow)
            time.sleep(random.uniform(0.06, 0.14))
            keyboard.release(arrow)
            time.sleep(random.uniform(0.1, 0.25))
        return

    if ENABLE_KEYBOARD_TYPING:
        phrases = [
            "status check ok", "reviewing updates", "log entry noted",
            "page refreshed", "changes saved", "ticket updated"
        ]
        phrase = random.choice(phrases)
        try:
            keyboard.type(phrase, interval=random.uniform(0.07, 0.16))
            if random.random() < 0.25:
                time.sleep(random.uniform(0.15, 0.3))
                for _ in range(random.randint(1, 3)):
                    keyboard.press(Key.backspace)
                    keyboard.release(Key.backspace)
                    time.sleep(0.08)
                keyboard.type(" " + random.choice(["done", "ok", "noted"]))
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        except Exception:
            pass

def main_loop():
    activity_count = 0
    cx, cy = get_screen_center()
    print(f"Screen center detected at ({cx}, {cy})")
    print("Running with randomized human-like activity patterns.\n")

    while True:
        activity_count += 1
        now = datetime.now().strftime("%H:%M:%S")

        do_human_like_mouse_activity()

        if random.random() < KEYBOARD_ACTION_PROB:
            do_keyboard_activity()

        if activity_count % 5 == 0:
            print(f"[{now}] Activity cycle #{activity_count} completed.")

        sleep_seconds = random.uniform(ACTIVITY_INTERVAL_MIN, ACTIVITY_INTERVAL_MAX)
        print(f"[{now}] Next activity in ~{sleep_seconds:.0f} seconds...")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\nScript stopped cleanly by user.")
