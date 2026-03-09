---
name: desktop-reminder-prototype
description: Build or update a one-shot PySide6 desktop reminder popup that OpenClaw can invoke with command-line arguments. Use when working on desktop reminder popups, reminder windows, notification popups, alert dialogs, animated desktop prompts, or CLI-triggered reminder UIs. Also use when the request refers to Chinese reminder scenarios such as zhuomian tixing, tixing tanchuang, jiuzuo tixing, heshui tixing, huiyi tixing, xiuxi tixing, OpenClaw diaoyong, minglinghang chuan can, or danci tixing chuangkou. This skill is for a single-run popup process that receives parameters, shows the reminder, auto-closes, and exits.
---

# Desktop Reminder Prototype

Use `scripts/main.py` as the only entry point.

Treat the app as a one-shot popup process:
- Parse CLI arguments
- Normalize reminder type
- Resolve assets and defaults
- Show the popup
- Auto-close and exit cleanly

Do not add scheduler logic, tray icons, polling, background daemons, or long-running loops. OpenClaw handles scheduling externally.

Keep runnable application code in `scripts/`.

Keep bundled reminder images in `assets/` and resolve them from the skill root. When adding new reminder styles, update `scripts/asset_manager.py` rather than hardcoding style decisions in the window.

Use `scripts/asset_manager.py` as the style and defaults registry:
- Normalize raw reminder types into `drink`, `activity`, `meeting`, or `rest`
- Provide default message and duration
- Resolve image paths and optional animation frames

Use `scripts/reminder_window.py` for the transparent topmost popup, painter-drawn bubble, cat frame switching, and Qt animation sequence.

Prefer Qt animation classes such as `QPropertyAnimation`, `QParallelAnimationGroup`, `QSequentialAnimationGroup`, `QPauseAnimation`, `QGraphicsOpacityEffect`, and low-frequency `QTimer` frame switching.

If assets are missing, raise clear local file errors for required files and gracefully skip optional files.

When editing the CLI contract, preserve support for:
- `--type`
- `--message`
- `--duration`

When unknown reminder types are received, normalize them to `meeting` instead of failing.

Keep logs concise and useful for OpenClaw integration, especially around:
- raw and normalized reminder type
- default versus custom message resolution
- duration resolution
- popup show and close
- cat frame animation start, switch, and stop

Typical Chinese requests that should map to this skill:
- make a desktop reminder popup for OpenClaw
- add CLI reminder type and message support
- build a one-shot reminder window
- support drink, activity, meeting, and rest reminders

Typical English requests that should map to this skill:
- build a desktop reminder popup
- create a one-shot reminder window
- show an animated reminder dialog from CLI
- make an OpenClaw-invoked desktop alert
- pass reminder type, message, and duration via command line
