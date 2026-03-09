from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from reminder_window import ReminderWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Reminder Prototype")
    app.setQuitOnLastWindowClosed(True)
#- rest / activity / drink 已经能正常显示
#- meeting 报错问题已修复
    # Change this value locally when you want to preview another reminder type.
    reminder_type = "rest"

    try:
        window = ReminderWindow(reminder_type=reminder_type)
        window.show()
        return app.exec()
    except Exception as exc:
        traceback.print_exc()
        QMessageBox.critical(
            None,
            "启动失败",
            f"提醒弹窗原型启动失败：\n{exc}",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
