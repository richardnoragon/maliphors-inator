"""Module for managing application logging with Qt UI."""
import os
import sys
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QTimer


class QtHandler(logging.Handler):
    """Logging handler that writes to a Qt text widget."""
    
    MAX_LINES = 1000  # Maximum number of lines to keep in the widget
    CLEANUP_TRIGGER = 1200  # When to trigger cleanup
    
    def __init__(self, widget):
        """Initialize the handler."""
        super().__init__()
        self.widget = widget
        self.buffer = []  # Buffer for batching updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.flush_buffer)
        self.update_timer.start(100)  # Update every 100ms
        
    def emit(self, record):
        """Buffer the log message."""
        try:
            msg = self.format(record)
            self.buffer.append(msg)
        except Exception:
            self.handleError(record)
            
    def flush_buffer(self):
        """Flush the buffer to the widget."""
        if not self.buffer:
            return
            
        try:
            # Join all buffered messages with newlines
            text = '\n'.join(self.buffer)
            self.widget.append(text)
            self.buffer.clear()
            
            # Check if cleanup is needed
            doc = self.widget.document()
            if doc.lineCount() > self.CLEANUP_TRIGGER:
                cursor = self.widget.textCursor()
                cursor.movePosition(cursor.Start)
                cursor.movePosition(
                    cursor.Down,
                    cursor.KeepAnchor,
                    doc.lineCount() - self.MAX_LINES
                )
                cursor.removeSelectedText()
                
        except Exception as e:
            # Clear buffer to prevent memory buildup even if there's an error
            self.buffer.clear()
            print(f"Error in flush_buffer: {e}", file=sys.stderr)


class LogManager(QtWidgets.QMainWindow):
    """Manager for application logging with Qt UI."""
    
    def __init__(self, parent=None):
        """Initialize the log manager."""
        super(LogManager, self).__init__(parent)
        
        # Load the UI
        current_dir = os.path.dirname(os.path.abspath(__file__))
        from app_resources import resource_path
        ui_file = str(resource_path("log_manager.ui"))
        uic.loadUi(ui_file, self)
        
        # Set up logging
        self.logger = logging.getLogger('maliphors_inator')
        self.logger.setLevel(logging.DEBUG)
        
        # Create and add Qt handler
        self.qt_handler = QtHandler(self.logTextEdit)
        self.qt_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        self.qt_handler.setFormatter(formatter)
        self.logger.addHandler(self.qt_handler)
        
        # Connect buttons
        self.clearButton.clicked.connect(self.clear_logs)
        self.exportButton.clicked.connect(self.export_logs)
        self.actionExit.triggered.connect(self.close)
        
    async def export_logs_async(self, filepath):
        """Export logs to a file asynchronously."""
        try:
            text = self.logTextEdit.toPlainText()
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: Path(filepath).write_text(text, encoding='utf-8')
            )
            return True
        except Exception as e:
            self.logger.error(f"Error exporting logs: {str(e)}")
            return False
            
    def export_logs(self):
        """Export logs to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"maliphors_inator_log_{timestamp}.txt"
        
        filepath, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            default_filename,
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filepath:
            self.qt_handler.flush_buffer()
            asyncio.run(self.export_logs_async(filepath))
            
    def clear_logs(self):
        """Clear the log display."""
        self.qt_handler.buffer.clear()
        self.logTextEdit.clear()
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up logging handlers
        if hasattr(self, 'qt_handler'):
            self.logger.removeHandler(self.qt_handler)
            self.qt_handler.update_timer.stop()
        event.accept()


def log_message(message, level=logging.INFO):
    """Log a message using the application logger."""
    logger = logging.getLogger('maliphors_inator')
    logger.log(level, message)


if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication([])
        window = LogManager()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Failed to start Log Manager: {str(e)}")
        sys.exit(1)
