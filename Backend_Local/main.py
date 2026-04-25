import sys
import os

# Make sure project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

import database
from ui.main_window import MainWindow
from ui.styles import APP_STYLE
import traceback
from PyQt6.QtWidgets import QMessageBox

def global_exception_handler(exc_type, exc_value, exc_tb):
    """Global handler for uncaught exceptions to prevent crashing."""
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"Unhandled Exception:\\n{err_msg}")
    
    # Check if a QApplication exists to show the message box
    from PyQt6.QtWidgets import QApplication
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error Crítico del Sistema")
        msg.setText("El sistema ha detectado un error inesperado, pero se ha recuperado. La acción anterior pudo no haberse completado.")
        msg.setDetailedText(err_msg)
        msg.exec()

sys.excepthook = global_exception_handler


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Llanos Core")
    app.setOrganizationName("Llanos Core")

    # Global font
    app.setFont(QFont("Segoe UI Variable", 10) if QFont("Segoe UI Variable").exactMatch() else QFont("Segoe UI", 10))

    # Global dark stylesheet
    app.setStyleSheet(APP_STYLE)

    # Initialize database (creates tables if they don't exist)
    database.init_db()

    # Launch main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
