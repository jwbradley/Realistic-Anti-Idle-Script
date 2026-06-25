#!/usr/bin/env python3
"""
Improved Anti-Idle / Screen Timeout Prevention Script
More resistant to mouse movement trackers and keyloggers.
"""

import pyautogui
import random
import time
from datetime import datetime
from pynput.keyboard import Key, Controller

# ====================== CONFIGURATION ======================
# Tune these based on your company's idle timeout policy.
# Typical corporate timeouts are 5–15 minutes. Activity every 1.5–3.5 min is usually safe.

ACTIVITY_INTERVAL_MIN = 60      # seconds (minimum time between activity bursts)
ACTIVITY_INTERVAL_MAX = 240     # seconds (maximum)

MOUSE_JITTER_INTENSITY = 35     # pixels - how far small movements wander
ENABLE_KEYBOARD_TYPING = False  # ⚠️ WARNING: Only set True if you have a safe text field focused.
                                # Typing goes to whatever window currently has focus.

KEYBOARD_ACTION_PROB = 0.35     # 0.0–1.0 chance of doing keyboard activity per cycle

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

    # === Primary: Small natural fidgets / adjustments (most human-like) ===
    num_moves = random.randint(5, 12)
    for _ in range(num_moves):
        # Gaussian distribution feels more natural than uniform random
        dx = random.gauss(0, MOUSE_JITTER_INTENSITY)
        dy = random.gauss(0, MOUSE_JITTER_INTENSITY * 0.8)

        # Occasionally a slightly larger "purposeful" glance
        if random.random() < 0.18:
            dx += random.randint(-90, 90)
            dy += random.randint(-70, 70)

        duration = random.uniform(0.12, 0.42)

        # Use easing functions for acceleration/deceleration (more human)
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

    # === Secondary: Occasional medium "attention shift" to another screen area ===
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
    """Occasional keyboard input. Mix of safe actions + optional typing."""
    if random.random() < 0.6:
        # Most common: just press Shift or Ctrl (very common in anti-idle scripts, low side effects)
        key = random.choice([Key.shift, Key.ctrl])
        keyboard.press(key)
        time.sleep(random.uniform(0.08, 0.18))
        keyboard.release(key)
        return

    if random.random() < 0.7:
        # Arrow keys (common when reading documents or logs)
        for _ in range(random.randint(1, 3)):
            arrow = random.choice([Key.right, Key.left, Key.up, Key.down])
            keyboard.press(arrow)
            time.sleep(random.uniform(0.06, 0.14))
            keyboard.release(arrow)
            time.sleep(random.uniform(0.1, 0.25))
        return

    # Rare: short varied phrase (only if you explicitly enabled it)
    if ENABLE_KEYBOARD_TYPING:
        phrases = [
            "status check ok",
            "reviewing updates",
            "log entry noted",
            "page refreshed",
            "changes saved",
            "ticket updated"
        ]
        phrase = random.choice(phrases)

        try:
            # Type slowly with human-like variation
            keyboard.type(phrase, interval=random.uniform(0.07, 0.16))

            # Occasional "correction" (backspace + retype) - very human
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

        # === Main Activity Burst ===
        do_human_like_mouse_activity()

        # Keyboard activity (probabilistic)
        if random.random() < KEYBOARD_ACTION_PROB:
            do_keyboard_activity()

        # Occasional status line (only every 5th cycle)
        if activity_count % 5 == 0:
            print(f"[{now}] Activity cycle #{activity_count} completed — still preventing timeout.")

        # === Randomized sleep (this is critical for evading pattern detection) ===
        sleep_seconds = random.uniform(ACTIVITY_INTERVAL_MIN, ACTIVITY_INTERVAL_MAX)
        print(f"[{now}] Next activity in ~{sleep_seconds:.0f} seconds...")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\nScript stopped cleanly by user. Goodbye!")