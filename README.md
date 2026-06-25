# 🖥️ Realistic Anti-Idle Script

**Prevents screen timeout / idle lock** by simulating natural human mouse and keyboard activity. Designed to be significantly harder for mouse movement trackers and keyloggers to detect as automated behavior.

## Why This Script?

Corporate environments often have aggressive screen lock / idle timeout policies (typically 5–15 minutes). Simple scripts that draw perfect circles or type the same message on a fixed schedule are easily flagged by modern detection systems.

This script uses **high-entropy, human-like behavior**:
- Variable speed and acceleration
- Natural jitter and irregular paths
- Probabilistic timing
- Mixed keyboard actions

## Features

- **Human-like mouse movement** using Gaussian jitter + easing functions (`easeInOutQuad`, `easeOutQuad`, etc.)
- Small natural fidgets + occasional medium "attention shifts" across the screen
- **Varied keyboard activity**: Shift/Ctrl presses, arrow keys, and (optional) short varied phrases typed at human speed with occasional corrections
- **Highly randomized timing** — no fixed intervals or predictable patterns
- Clean error handling and `FAILSAFE` protection
- Easy to configure via variables at the top of the script
- Cross-platform (best on Windows)

## Improvements Over the Original Script

| Aspect                    | Original                          | Improved Version                              |
|---------------------------|-----------------------------------|-----------------------------------------------|
| Mouse Path                | Perfect mathematical circle       | Random jitter + easing + variable paths       |
| Timing                    | Fixed modulo + regular sleeps     | Probabilistic + random 60–240s intervals      |
| Keyboard                  | Same message every 2 cycles       | Mix of safe keys + varied optional phrases    |
| Detectability             | High (geometric + rhythmic)       | Much lower (high entropy, human-like)         |
| Robustness                | Basic, had bugs                   | Proper structure + error handling             |
| Configurability           | Hardcoded                         | Clear config section at top                   |

## Installation

```bash
pip install pyautogui pynput
