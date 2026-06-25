# 🖥️ Realistic Anti-Idle Script

**Prevents screen timeout and idle lockouts** by simulating natural human mouse and keyboard behavior. Designed to be significantly harder to detect than traditional anti-idle scripts.

## The Goal

Many corporate environments enforce aggressive screen lock / idle timeout policies (commonly 5, 10, or 15 minutes). When you step away or get pulled into a long meeting, your machine locks, which can interrupt workflows, VPN sessions, or long-running processes.

Simple scripts that draw perfect circles or type the same message on a fixed schedule are increasingly easy for modern monitoring systems (mouse trackers, keyloggers, or endpoint detection) to flag as automated behavior.

**This script takes a different approach**: it generates **irregular, high-entropy, human-like input** so the activity looks like a real person who is present but not constantly typing or clicking.

## Why This Version Is Better

Traditional anti-idle scripts are often easy to detect because they use:
- Perfect geometric shapes (circles, squares)
- Fixed timing intervals
- Repetitive, identical keyboard input
- Constant speed and movement patterns

This improved version counters those detection methods by using:

- **Gaussian jitter** and random relative movements instead of perfect paths
- **Easing functions** (`easeInOutQuad`, `easeOutQuad`, etc.) for natural acceleration and deceleration
- **Probabilistic timing** — activity happens at random intervals between configurable min/max values
- **Varied keyboard actions** — mix of modifier keys, arrow navigation, and optional short varied phrases
- **Multi-scale movement** — small natural fidgets + occasional larger “attention shifts”

The result is input that is much closer to real human behavior and significantly harder to fingerprint as scripted.

## Features

- Human-like mouse movement with variable speed and natural jitter
- Probabilistic keyboard activity (Shift, Ctrl, arrows, and optional typing)
- Fully configurable timing and intensity
- Clean error handling and `FAILSAFE` protection
- Graceful exit with `Ctrl + C`
- Low resource usage
- Works on Windows 10/11 (primary target)

## Installation

### 1. Install Python (if not already installed)

Download the latest Python 3 from [python.org](https://www.python.org/downloads/).  
During installation, **check the box** that says “Add Python to PATH”.

### 2. Install Required Packages

Open Command Prompt or PowerShell and run:

```bash
pip install pyautogui pynput
