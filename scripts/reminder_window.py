from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QPoint,
    QPauseAnimation,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    Qt,
    QSize,
    QTimer,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QLabel,
    QPushButton,
    QWidget,
)

from asset_manager import AssetError, AssetManager


class BubbleWidget(QWidget):
    """Draw a crisp speech bubble with icon and text using QPainter."""

    def __init__(
        self,
        icon_pixmap: QPixmap | None,
        message: str,
        reminder_type: str,
        text_color: str,
        accent_color: str,
        tail_anchor_x: int = 86,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_pixmap = icon_pixmap
        self._message = message
        self._reminder_type = reminder_type
        self._text_color = QColor(text_color)
        self._accent_color = QColor(accent_color)
        self._tail_anchor_x = tail_anchor_x
        self._paint_logged = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._recalculate_size()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if not self._paint_logged:
            print("bubble rendered by painter")
            self._paint_logged = True

        bubble_rect = self.rect().adjusted(14, 12, -14, -24)
        tail_width = 22
        tail_height = 11
        tail_center_x = bubble_rect.left() + self._tail_anchor_x

        bubble_path = self._build_bubble_path(bubble_rect, tail_center_x, tail_width, tail_height)
        fill_color, border_color, glow_color = self._theme_colors()
        painter.fillPath(bubble_path, fill_color)
        painter.setPen(QPen(QColor(glow_color), 6))
        painter.drawPath(bubble_path)
        painter.setPen(QPen(QColor(border_color), 1.5))
        painter.drawPath(bubble_path)

        content_rect = bubble_rect.adjusted(22, 18, -22, -18)
        icon_size = 40
        if self._icon_pixmap is not None and not self._icon_pixmap.isNull():
            icon_rect = QRect(content_rect.left(), content_rect.top() + 1, icon_size, icon_size)
            painter.drawPixmap(icon_rect, self._icon_pixmap)
            content_rect.adjust(icon_size + 14, 0, 0, 0)

        font = self._build_font()
        painter.setFont(font)
        painter.setPen(self._text_color)

        metrics = QFontMetrics(font)
        wrapped_rect = metrics.boundingRect(
            content_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self._message,
        )
        if wrapped_rect.height() > content_rect.height():
            font.setPointSize(max(11, font.pointSize() - 2))
            painter.setFont(font)

        painter.drawText(
            content_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self._message,
        )

    def _recalculate_size(self) -> None:
        font = self._build_font()
        metrics = QFontMetrics(font)

        min_text_width = 140
        max_text_width = 314
        icon_width = 62 if self._icon_pixmap is not None and not self._icon_pixmap.isNull() else 0
        text_probe = metrics.boundingRect(
            QRect(0, 0, max_text_width, 500),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self._message,
        )
        text_width = max(min_text_width, min(max_text_width, text_probe.width() + 16))
        total_width = min(424, text_width + icon_width + 64)
        text_height = metrics.boundingRect(
            QRect(0, 0, total_width - icon_width - 64, 500),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self._message,
        ).height()
        total_height = max(92, text_height + 52)
        self.resize(total_width, total_height + 20)
        print("bubble size calculated")
        print("bubble layout adjusted")
        if icon_width:
            print("icon size updated")

    def set_tail_anchor_x(self, anchor_x: int) -> None:
        self._tail_anchor_x = anchor_x
        self.update()

    @staticmethod
    def _build_font() -> QFont:
        font = QFont()
        font.setFamilies(
            [
                "Microsoft YaHei UI",
                "Microsoft YaHei",
                "PingFang SC",
                "Noto Sans CJK SC",
                "SimHei",
                "Sans Serif",
            ]
        )
        font.setPointSize(16)
        font.setWeight(QFont.Weight.DemiBold)
        return font

    @staticmethod
    def _build_bubble_path(
        bubble_rect: QRect,
        tail_center_x: int,
        tail_width: int,
        tail_height: int,
    ) -> QPainterPath:
        radius = 26
        path = QPainterPath()
        path.addRoundedRect(QRectF(bubble_rect), radius, radius)

        tail = QPainterPath()
        base_y = bubble_rect.bottom() - 2
        tip_y = bubble_rect.bottom() + tail_height
        tail.moveTo(tail_center_x - tail_width / 2, base_y)
        tail.quadTo(tail_center_x - 5, bubble_rect.bottom() + 4, tail_center_x, tip_y)
        tail.quadTo(tail_center_x + 5, bubble_rect.bottom() + 4, tail_center_x + tail_width / 2, base_y)
        tail.closeSubpath()
        path.addPath(tail)
        return path.simplified()

    def _theme_colors(self) -> tuple[QColor, QColor, QColor]:
        if self._reminder_type == "drink":
            return QColor("#EEFCFF"), QColor("#5EDDEF"), QColor(81, 220, 240, 52)
        if self._reminder_type == "activity":
            return QColor("#F1F6FF"), QColor("#6B9DFF"), QColor(104, 157, 255, 50)
        if self._reminder_type == "meeting":
            return QColor("#F2FFF5"), QColor("#78D89B"), QColor(120, 216, 155, 48)
        return QColor("#FFF6D8"), QColor("#F3C85A"), QColor(243, 200, 90, 52)


class CloseButton(QPushButton):
    def __init__(self, fill_color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._fill_color = QColor(fill_color)
        self.setFixedSize(34, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("关闭")
        self.setFlat(True)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        base_color = QColor(self._fill_color)
        base_color.setAlpha(205 if self.underMouse() else 155)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(base_color)
        painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))

        painter.setPen(QColor("#F5FDFF"))
        painter.drawLine(11, 11, 23, 23)
        painter.drawLine(23, 11, 11, 23)


class ReminderWindow(QWidget):
    WINDOW_SIZE = QSize(820, 540)
    LINE_TARGET_SIZE = QSize(520, 42)
    PLATFORM_SIZE = QSize(360, 112)
    CAT_SIZE = QSize(248, 248)
    BUBBLE_SIZE = QSize(390, 178)

    def __init__(
        self,
        reminder_type: str = "drink",
        message: str | None = None,
        auto_close_ms: int | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.asset_manager = AssetManager()
        self.assets = self.asset_manager.get_reminder_assets(reminder_type)
        self.message = message if message is not None else self.assets.message
        self.auto_close_ms = auto_close_ms if auto_close_ms is not None else self.assets.auto_close_ms

        self.animations: list[object] = []
        self.sequence_group: QSequentialAnimationGroup | None = None
        self.bottom_effects_group: QParallelAnimationGroup | None = None
        self.fade_out_group: QParallelAnimationGroup | None = None
        self.ambient_group: QParallelAnimationGroup | None = None

        self._animation_started = False
        self._close_requested = False
        self._bottom_effects_faded = False
        self._bottom_fade_started = False
        self._fade_started = False
        self._closed = False
        self._quit_requested = False
        self._sparkle_labels: list[QLabel] = []
        self._sparkle_effects: list[QGraphicsOpacityEffect] = []
        self.cat_animation_timer = QTimer(self)
        self.cat_animation_timer.setSingleShot(True)
        self.cat_animation_timer.timeout.connect(self._advance_cat_frame)
        self.cat_animation_frames: list[QPixmap] = []
        self.cat_animation_index = 0

        self._configure_window()
        self._load_pixmaps()
        print("assets loaded")
        self._build_ui()
        self._position_window()
        print("window initialized")
        print("bubble shadow adjusted")
        print(f"reminder type loaded: {self.assets.reminder_type}")

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        print("reminder window shown")
        if not self._animation_started:
            self._start_animation_sequence()

    def closeEvent(self, event) -> None:
        self._closed = True
        super().closeEvent(event)
        self._request_app_quit()

    def _configure_window(self) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(self.WINDOW_SIZE)

    def _load_pixmaps(self) -> None:
        # Load all assets during startup so missing files fail early.
        self.dot_pixmap = self._load_required_pixmap(self.assets.dot_path)
        self.cat_pixmap = self._load_required_pixmap(self.assets.cat_path)
        self.cat_animation_frames = self._load_cat_animation_frames(self.assets.cat_frame_paths)
        self.sparkle_primary_pixmap = self._load_required_pixmap(self.assets.sparkle_primary_path)
        self.sparkle_secondary_pixmap = self._load_required_pixmap(self.assets.sparkle_secondary_path)

        self.line_pixmap = self._load_optional_pixmap(self.assets.line_path)
        self.icon_pixmap = self._load_optional_pixmap(self.assets.icon_path)
        print("cat animation frames loaded")

    def _build_ui(self) -> None:
        self.dot_label = QLabel(self)
        self.dot_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.dot_label.setPixmap(self._scaled_pixmap(self.dot_pixmap, QSize(82, 82)))
        self.dot_label.adjustSize()
        self.dot_effect = self._install_opacity_effect(self.dot_label, initial_opacity=0.0)

        self.line_label = QLabel(self)
        self.line_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.line_label.setScaledContents(True)
        self.line_effect = self._install_opacity_effect(self.line_label, initial_opacity=0.0)
        if self.line_pixmap is not None:
            self.line_label.setPixmap(self._scaled_pixmap(self.line_pixmap, self.LINE_TARGET_SIZE))
        else:
            self.line_label.hide()

        self.cat_label = QLabel(self)
        self.cat_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.cat_render_size = QSize(220, 220)
        self.cat_label.setPixmap(self._scaled_pixmap(self.cat_pixmap, self.cat_render_size))
        self.cat_label.resize(self.cat_render_size)
        self.cat_effect = self._install_opacity_effect(self.cat_label, initial_opacity=0.0)

        icon_pixmap = None
        if self.icon_pixmap is not None:
            icon_pixmap = self._scaled_pixmap(self.icon_pixmap, QSize(30, 30))
        self.bubble_widget = BubbleWidget(
            icon_pixmap=icon_pixmap,
            message=self.message,
            reminder_type=self.assets.reminder_type,
            text_color=self.assets.text_color,
            accent_color=self.assets.accent_color,
            tail_anchor_x=86,
            parent=self,
        )
        self.bubble_effect = self._install_opacity_effect(self.bubble_widget, initial_opacity=0.0)

        self.sparkle_specs = [
            (self.sparkle_primary_pixmap, QSize(30, 30), QPoint(290, 76)),
            (self.sparkle_secondary_pixmap, QSize(22, 22), QPoint(720, 118)),
            (self.sparkle_secondary_pixmap, QSize(18, 18), QPoint(242, 266)),
        ]
        self._build_sparkles()

        self.close_button = CloseButton(self.assets.close_button_color, self)
        self.close_button.move(self.width() - self.close_button.width() - 18, 18)
        self.close_button.clicked.connect(self._handle_manual_close)

        self._layout_static_elements()
        self._bottom_effect_widgets = [self.dot_label, self.line_label, *self._sparkle_labels]
        self._bottom_effects = [self.dot_effect, self.line_effect, *self._sparkle_effects]

    def _layout_static_elements(self) -> None:
        center_x = self.width() // 2
        line_y = 430

        dot_rect = self.dot_label.rect()
        self.dot_label.move(center_x - dot_rect.width() // 2, line_y - dot_rect.height() // 2 + 4)

        self.line_final_rect = QRect(
            center_x - self.LINE_TARGET_SIZE.width() // 2,
            line_y - self.LINE_TARGET_SIZE.height() // 2,
            self.LINE_TARGET_SIZE.width(),
            self.LINE_TARGET_SIZE.height(),
        )
        self.line_label.setGeometry(
            QRect(
                center_x - 3,
                self.line_final_rect.y(),
                6,
                self.line_final_rect.height(),
            )
        )

        cat_x = center_x - self.cat_render_size.width() // 2
        self.cat_end_pos = QPoint(cat_x, 274)
        self.cat_start_pos = QPoint(cat_x, 330)
        self.cat_label.move(self.cat_start_pos)

        bubble_width = self.bubble_widget.width()
        bubble_height = self.bubble_widget.height()
        cat_head_anchor_x = self.cat_end_pos.x() + int(self.cat_render_size.width() * 0.61)
        cat_head_anchor_y = self.cat_end_pos.y() + int(self.cat_render_size.height() * 0.18)
        bubble_x = cat_head_anchor_x + int(bubble_width * 0.24)
        bubble_y = cat_head_anchor_y - bubble_height - 22
        self.bubble_end_rect = QRect(bubble_x - bubble_width // 2, bubble_y, bubble_width, bubble_height)
        self.bubble_start_rect = QRect(
            self.bubble_end_rect.center().x() - 20,
            self.bubble_end_rect.center().y() - 12,
            max(120, self.bubble_end_rect.width() - 40),
            max(76, self.bubble_end_rect.height() - 24),
        )
        tail_anchor_x = max(
            42,
            min(
                self.bubble_end_rect.width() - 46,
                cat_head_anchor_x - self.bubble_end_rect.x() - 8,
            ),
        )
        self.bubble_widget.set_tail_anchor_x(tail_anchor_x)
        self.bubble_widget.setGeometry(self.bubble_start_rect)
        close_x = min(
            self.width() - self.close_button.width() - 20,
            self.bubble_end_rect.right() + 14,
        )
        close_y = max(18, self.bubble_end_rect.y() - 8)
        self.close_button.move(close_x, close_y)
        print("bubble position updated")

    def _position_window(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        screen_rect = screen.geometry()
        x = screen_rect.x() + (screen_rect.width() - self.width()) // 2
        bottom_margin = 0
        y = screen_rect.bottom() - self.height() - bottom_margin
        self.move(x, y)

    def _start_animation_sequence(self) -> None:
        if self._animation_started:
            return

        self._animation_started = True
        print("animation started")

        dot_sequence = QSequentialAnimationGroup(self)
        dot_sequence.addAnimation(
            self._create_opacity_animation(
                self.dot_effect,
                0.0,
                1.0,
                200,
                QEasingCurve.Type.OutCubic,
            )
        )
        dot_sequence.addPause(60)
        dot_sequence.addAnimation(
            self._create_opacity_animation(
                self.dot_effect,
                1.0,
                0.0,
                140,
                QEasingCurve.Type.InCubic,
            )
        )
        dot_sequence.finished.connect(self._on_dot_hidden)

        line_stage = QSequentialAnimationGroup(self)
        line_group = QParallelAnimationGroup(self)
        if self.line_pixmap is not None:
            self.line_label.show()
            line_group.addAnimation(
                self._create_geometry_animation(
                    self.line_label,
                    self.line_label.geometry(),
                    self.line_final_rect,
                    320,
                    QEasingCurve.Type.OutCubic,
                )
            )
            line_group.addAnimation(
                self._create_opacity_animation(
                    self.line_effect,
                    0.0,
                    0.42 if self.assets.reminder_type == "drink" else 0.54,
                    220,
                    QEasingCurve.Type.OutCubic,
                )
            )
        else:
            line_group.addAnimation(QPauseAnimation(220, self))
            print("meeting animation fixed")
        line_stage.addAnimation(line_group)
        line_stage.finished.connect(self._log_baseline_refined)

        cat_group = QParallelAnimationGroup(self)
        cat_group.addAnimation(
            self._create_position_animation(
                self.cat_label,
                self.cat_start_pos,
                self.cat_end_pos,
                340,
                QEasingCurve.Type.OutBack,
            )
        )
        cat_group.addAnimation(
            self._create_opacity_animation(
                self.cat_effect,
                0.0,
                1.0,
                280,
                QEasingCurve.Type.OutCubic,
            )
        )

        bubble_group = QParallelAnimationGroup(self)
        bubble_geometry = QPropertyAnimation(self.bubble_widget, b"geometry")
        bubble_geometry.setDuration(300)
        bubble_geometry.setStartValue(self.bubble_start_rect)
        bubble_geometry.setKeyValueAt(0.72, self._overshoot_rect(self.bubble_end_rect, 1.06))
        bubble_geometry.setEndValue(self.bubble_end_rect)
        bubble_geometry.setEasingCurve(QEasingCurve.Type.OutCubic)
        bubble_group.addAnimation(bubble_geometry)
        bubble_group.addAnimation(
            self._create_opacity_animation(
                self.bubble_effect,
                0.0,
                1.0,
                220,
                QEasingCurve.Type.OutCubic,
            )
        )
        bubble_group.finished.connect(self._on_bubble_shown)

        self.sequence_group = QSequentialAnimationGroup(self)
        self.sequence_group.addAnimation(dot_sequence)
        self.sequence_group.addAnimation(line_stage)
        self.sequence_group.addAnimation(cat_group)
        self.sequence_group.addAnimation(bubble_group)
        self.sequence_group.addPause(max(0, self.auto_close_ms - 1120))
        self.sequence_group.finished.connect(self._handle_auto_close)
        self.sequence_group.start()

        self.animations.extend(
            [dot_sequence, line_group, line_stage, cat_group, bubble_group, bubble_geometry, self.sequence_group]
        )
        QTimer.singleShot(1140, self._start_ambient_animations)

    def _on_bubble_shown(self) -> None:
        print("bubble shown")
        self._start_cat_animation()

    def _on_dot_hidden(self) -> None:
        self.dot_label.hide()
        print("dot hidden")

    def _log_baseline_refined(self) -> None:
        print("line remains as primary baseline")
        print("baseline refined")

    def _handle_auto_close(self) -> None:
        print("auto close triggered")
        self._request_close("auto")

    def _handle_manual_close(self) -> None:
        print("manual close triggered")
        self._request_close("manual")

    def _request_close(self, reason: str) -> None:
        if self._close_requested or self._closed:
            return

        self._close_requested = True
        self._stop_cat_animation()

        # Stop ongoing timeline first so auto-close and manual-close cannot race.
        if self.sequence_group is not None and self.sequence_group.state() != self.sequence_group.State.Stopped:
            self.sequence_group.stop()

        self._stop_ambient_animations()
        self._fade_bottom_effects()

    def _fade_bottom_effects(self) -> None:
        if self._bottom_effects_faded:
            self._fade_out_and_close()
            return
        if self._bottom_fade_started or self._closed:
            return

        self._bottom_fade_started = True
        print("bottom effects fade started")

        bottom_group = QParallelAnimationGroup(self)
        for effect in self._bottom_effects:
            bottom_group.addAnimation(
                self._create_opacity_animation(
                    effect,
                    effect.opacity(),
                    0.0,
                    220,
                    QEasingCurve.Type.InCubic,
                )
            )

        bottom_group.finished.connect(self._on_bottom_effects_hidden)
        bottom_group.start()
        self.bottom_effects_group = bottom_group
        self.animations.append(bottom_group)

    def _on_bottom_effects_hidden(self) -> None:
        self._bottom_effects_faded = True
        self._bottom_fade_started = False
        for widget in self._bottom_effect_widgets:
            widget.hide()
        if self.line_label is not None:
            print("line hidden")
        print("bottom effects hidden")
        print("bottom effects finalized")
        self._fade_out_and_close()

    def _fade_out_and_close(self) -> None:
        if self._fade_started or self._closed:
            return

        self._fade_started = True
        print("window fade out started")

        fade_group = QParallelAnimationGroup(self)
        effects = [
            self.cat_effect,
            self.bubble_effect,
        ]

        for effect in effects:
            fade_group.addAnimation(
                self._create_opacity_animation(
                    effect,
                    effect.opacity(),
                    0.0,
                    220,
                    QEasingCurve.Type.InCubic,
                )
            )

        fade_group.finished.connect(self._finalize_close)
        fade_group.start()
        self.fade_out_group = fade_group
        self.animations.append(fade_group)

    def _finalize_close(self) -> None:
        if self._closed:
            return

        print("window closed")
        self._closed = True
        self.close()
        self._request_app_quit()

    def _build_sparkles(self) -> None:
        for pixmap, size, position in self.sparkle_specs:
            sparkle = QLabel(self)
            sparkle.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            sparkle.setPixmap(self._tinted_pixmap(self._scaled_pixmap(pixmap, size), self.assets.accent_color))
            sparkle.resize(size)
            sparkle.move(position)
            effect = self._install_opacity_effect(sparkle, initial_opacity=0.0)
            self._sparkle_labels.append(sparkle)
            self._sparkle_effects.append(effect)

    def _start_ambient_animations(self) -> None:
        if self._close_requested or self._closed or self.ambient_group is not None:
            return

        self.ambient_group = QParallelAnimationGroup(self)

        bubble_float = QSequentialAnimationGroup(self)
        bubble_float.addAnimation(
            self._create_geometry_animation(
                self.bubble_widget,
                self.bubble_end_rect,
                self.bubble_end_rect.translated(0, -5),
                1400,
                QEasingCurve.Type.InOutSine,
            )
        )
        bubble_float.addAnimation(
            self._create_geometry_animation(
                self.bubble_widget,
                self.bubble_end_rect.translated(0, -5),
                self.bubble_end_rect,
                1400,
                QEasingCurve.Type.InOutSine,
            )
        )
        bubble_float.setLoopCount(-1)
        self.ambient_group.addAnimation(bubble_float)

        for index, effect in enumerate(self._sparkle_effects):
            sparkle_pulse = QSequentialAnimationGroup(self)
            sparkle_pulse.addPause(index * 180)
            sparkle_pulse.addAnimation(
                self._create_opacity_animation(
                    effect,
                    0.0,
                    0.95,
                    420,
                    QEasingCurve.Type.OutCubic,
                )
            )
            sparkle_pulse.addAnimation(
                self._create_opacity_animation(
                    effect,
                    0.95,
                    0.25,
                    520,
                    QEasingCurve.Type.InOutSine,
                )
            )
            sparkle_pulse.addAnimation(
                self._create_opacity_animation(
                    effect,
                    0.25,
                    0.75,
                    520,
                    QEasingCurve.Type.InOutSine,
                )
            )
            sparkle_pulse.addAnimation(
                self._create_opacity_animation(
                    effect,
                    0.75,
                    0.15,
                    640,
                    QEasingCurve.Type.InCubic,
                )
            )
            sparkle_pulse.setLoopCount(-1)
            self.ambient_group.addAnimation(sparkle_pulse)

        self.ambient_group.start()
        self.animations.append(self.ambient_group)

    def _stop_ambient_animations(self) -> None:
        if self.ambient_group is None:
            return
        self.ambient_group.stop()
        self.ambient_group = None

    def _start_cat_animation(self) -> None:
        if self._close_requested or self._closed:
            return
        if len(self.cat_animation_frames) <= 1:
            return
        if self.cat_animation_timer.isActive():
            return

        self.cat_animation_index = 0
        self.cat_animation_timer.start(self._next_cat_frame_interval())
        print("cat animation started")

    def _stop_cat_animation(self) -> None:
        if not self.cat_animation_timer.isActive():
            return
        self.cat_animation_timer.stop()
        print("cat animation stopped")

    def _advance_cat_frame(self) -> None:
        if self._close_requested or self._closed:
            self._stop_cat_animation()
            return
        if len(self.cat_animation_frames) <= 1:
            return

        self.cat_animation_index = (self.cat_animation_index + 1) % len(self.cat_animation_frames)
        frame = self.cat_animation_frames[self.cat_animation_index]
        self.cat_label.setPixmap(self._scaled_pixmap(frame, self.cat_render_size))
        self.cat_animation_timer.start(self._next_cat_frame_interval())
        print("cat frame switched")

    @staticmethod
    def _next_cat_frame_interval() -> int:
        return random.randint(900, 1200)

    def _load_cat_animation_frames(self, frame_paths: tuple[Path, ...]) -> list[QPixmap]:
        frames: list[QPixmap] = []
        for path in frame_paths:
            pixmap = self._load_optional_pixmap(path)
            if pixmap is not None:
                frames.append(pixmap)

        if not frames:
            frames.append(self.cat_pixmap)
        return frames

    def _request_app_quit(self) -> None:
        if self._quit_requested:
            return
        self._quit_requested = True
        app = QApplication.instance()
        if app is not None:
            QTimer.singleShot(0, app.quit)

    @staticmethod
    def _install_opacity_effect(widget: QWidget, initial_opacity: float) -> QGraphicsOpacityEffect:
        effect = QGraphicsOpacityEffect(widget)
        effect.setOpacity(initial_opacity)
        widget.setGraphicsEffect(effect)
        return effect

    @staticmethod
    def _create_opacity_animation(
        effect: QGraphicsOpacityEffect,
        start: float,
        end: float,
        duration: int,
        easing: QEasingCurve.Type,
    ) -> QPropertyAnimation:
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def _create_geometry_animation(
        widget: QWidget,
        start: QRect,
        end: QRect,
        duration: int,
        easing: QEasingCurve.Type,
    ) -> QPropertyAnimation:
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def _create_position_animation(
        widget: QWidget,
        start: QPoint,
        end: QPoint,
        duration: int,
        easing: QEasingCurve.Type,
    ) -> QPropertyAnimation:
        animation = QPropertyAnimation(widget, b"pos")
        animation.setStartValue(start)
        animation.setEndValue(end)
        animation.setDuration(duration)
        animation.setEasingCurve(easing)
        return animation

    @staticmethod
    def _load_required_pixmap(path: Path) -> QPixmap:
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            raise AssetError(f"Failed to load required image asset: {path}")
        return pixmap

    @staticmethod
    def _load_optional_pixmap(path: Path | None) -> QPixmap | None:
        if path is None:
            return None

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return None
        return pixmap

    @staticmethod
    def _scaled_pixmap(pixmap: QPixmap, target_size: QSize) -> QPixmap:
        return pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    @staticmethod
    def _overshoot_rect(rect: QRect, scale: float) -> QRect:
        center = rect.center()
        width = int(rect.width() * scale)
        height = int(rect.height() * scale)
        return QRect(center.x() - width // 2, center.y() - height // 2, width, height)

    @staticmethod
    def _tinted_pixmap(pixmap: QPixmap, color: str) -> QPixmap:
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.GlobalColor.transparent)

        painter = QPainter(tinted)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(QRectF(tinted.rect()), QColor(color))
        painter.end()
        return tinted
