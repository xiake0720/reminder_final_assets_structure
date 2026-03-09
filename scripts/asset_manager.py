from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class AssetError(FileNotFoundError):
    """Raised when a required local asset is missing or invalid."""


@dataclass(frozen=True, slots=True)
class ReminderAssets:
    reminder_type: str
    message: str
    auto_close_ms: int
    cat_path: Path
    cat_frame_paths: tuple[Path, ...]
    dot_path: Path
    platform_path: Path
    line_path: Path | None
    icon_path: Path | None
    sparkle_primary_path: Path
    sparkle_secondary_path: Path
    text_color: str
    accent_color: str
    close_button_color: str


class AssetManager:
    """Resolve reminder assets from the project root."""

    def __init__(self, base_dir: Path | None = None) -> None:
        default_base_dir = Path(__file__).resolve().parent.parent
        self.base_dir = (base_dir or default_base_dir).resolve()
        self.assets_dir = self.base_dir / "assets"

    def get_reminder_assets(self, reminder_type: str) -> ReminderAssets:
        normalized_type = reminder_type.strip().lower()
        configs = self._reminder_configs()

        if normalized_type not in configs:
            supported = ", ".join(sorted(configs))
            raise ValueError(
                f"Unsupported reminder type: '{normalized_type}'. Supported types: {supported}."
            )

        config = configs[normalized_type]
        return ReminderAssets(
            reminder_type=normalized_type,
            message=str(config["message"]),
            auto_close_ms=int(config["auto_close_ms"]),
            cat_path=self._resolve_required_path(str(config["cat"])),
            cat_frame_paths=self._resolve_optional_paths(config.get("cat_frames", [])),
            dot_path=self._resolve_required_path(str(config["dot"])),
            platform_path=self._resolve_required_path(str(config["platform"])),
            line_path=self._resolve_optional_path(config.get("line")),
            icon_path=self._resolve_optional_path(config.get("icon")),
            sparkle_primary_path=self._resolve_required_path(str(config["sparkle_primary"])),
            sparkle_secondary_path=self._resolve_required_path(str(config["sparkle_secondary"])),
            text_color=str(config["text_color"]),
            accent_color=str(config["accent_color"]),
            close_button_color=str(config["close_button_color"]),
        )

    def _resolve_required_path(self, relative_path: str) -> Path:
        path = (self.base_dir / relative_path).resolve()
        if not path.exists():
            raise AssetError(f"Missing required asset: {relative_path} (expected at {path})")
        if not path.is_file():
            raise AssetError(
                f"Required asset path is not a file: {relative_path} (resolved to {path})"
            )
        return path

    def _resolve_optional_path(self, relative_path: str | None) -> Path | None:
        if not relative_path:
            return None

        path = (self.base_dir / relative_path).resolve()
        if not path.exists():
            return None
        if not path.is_file():
            return None
        return path

    def _resolve_optional_paths(self, relative_paths: list[str] | tuple[str, ...]) -> tuple[Path, ...]:
        paths: list[Path] = []
        for relative_path in relative_paths:
            path = self._resolve_optional_path(relative_path)
            if path is not None:
                paths.append(path)
        return tuple(paths)

    @staticmethod
    def _reminder_configs() -> dict[str, dict[str, str | int | None]]:
        return {
            "drink": {
                "message": "该喝水啦，起来补一口水～",
                "auto_close_ms": 6000,
                "cat": "assets/cats/cat_hold_bottle_idle.png",
                "cat_frames": [
                    "assets/cats/cat_hold_bottle_idle.png",
                    "assets/cats/cat_hold_bottle_blink.png",
                    "assets/cats/cat_hold_bottle_idle.png",
                    "assets/cats/cat_hold_bottle_wink.png",
                ],
                "dot": "assets/effects/fx_dot_center_blue.png",
                "line": "assets/effects/fx_line_glow_cyan_long.png",
                "platform": "assets/effects/fx_platform_glow_cyan.png",
                "icon": "assets/icons/icon_water_drop.png",
                "sparkle_primary": "assets/effects/fx_sparkle_1.png",
                "sparkle_secondary": "assets/effects/fx_sparkle_2.png",
                "text_color": "#0B4B63",
                "accent_color": "#63E6FF",
                "close_button_color": "#0B3146",
            },
            "activity": {
                "message": "坐太久啦，起来活动一下吧～",
                "auto_close_ms": 6000,
                "cat": "assets/cats/cat_wave_left_1.png",
                "cat_frames": [
                    "assets/cats/cat_wave_left_1.png",
                    "assets/cats/cat_wave_left_2.png",
                    "assets/cats/cat_wave_left_1.png",
                    "assets/cats/cat_cheer_smile.png",
                ],
                "dot": "assets/effects/fx_dot_center_blue.png",
                "line": "assets/effects/fx_line_glow_blue_long.png",
                "platform": "assets/effects/fx_platform_glow_blue.png",
                "icon": "assets/icons/icon_alert.png",
                "sparkle_primary": "assets/effects/fx_sparkle_1.png",
                "sparkle_secondary": "assets/effects/fx_sparkle_2.png",
                "text_color": "#143E76",
                "accent_color": "#7CB8FF",
                "close_button_color": "#132C52",
            },
            "meeting": {
                "message": "会议快开始啦，别忘啦～",
                "auto_close_ms": 6000,
                "cat": "assets/cats/cat_notice_up.png",
                "cat_frames": [
                    "assets/cats/cat_notice_up.png",
                    "assets/cats/cat_notice_blink.png",
                    "assets/cats/cat_notice_up.png",
                    "assets/cats/cat_point_bubble.png",
                ],
                "dot": "assets/effects/fx_dot_center_blue.png",
                "line": None,
                "platform": "assets/effects/fx_platform_glow_green.png",
                "icon": "assets/icons/icon_clock.png",
                "sparkle_primary": "assets/effects/fx_sparkle_1.png",
                "sparkle_secondary": "assets/effects/fx_sparkle_2.png",
                "text_color": "#1D5D3E",
                "accent_color": "#87E7A8",
                "close_button_color": "#173B2B",
            },
            "rest": {
                "message": "休息一下吧，放松放松～",
                "auto_close_ms": 6000,
                "cat": "assets/cats/cat_sleepy_closed.png",
                "cat_frames": [
                    "assets/cats/cat_sleepy_open.png",
                    "assets/cats/cat_sleepy_closed.png",
                    "assets/cats/cat_sleepy_closed.png",
                    "assets/cats/cat_sleepy_paw.png",
                ],
                "dot": "assets/effects/fx_dot_center_blue.png",
                "line": "assets/effects/fx_line_glow_yellow_long.png",
                "platform": "assets/effects/fx_platform_glow_yellow.png",
                "icon": "assets/icons/icon_zzz.png",
                "sparkle_primary": "assets/effects/fx_sparkle_1.png",
                "sparkle_secondary": "assets/effects/fx_sparkle_2.png",
                "text_color": "#6A4B0B",
                "accent_color": "#FFD36B",
                "close_button_color": "#5D4513",
            },
        }
