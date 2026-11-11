from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QProgressBar
import json
from app_resources import resource_path


class SettingsManagerUI(QtWidgets.QMainWindow):
    def __init__(self, json_file_path=None):
        super(SettingsManagerUI, self).__init__()
        
        # Load UI
        uic.loadUi(str(resource_path('settings_manager.ui')), self)
        
        self.current_file = json_file_path
        self.settings_data = {}
        
        # Add progress bar to status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.hide()
        self.statusBar().addPermanentWidget(self.progress_bar)
        
        # Connect signals
        self.loadButton.clicked.connect(self.load_file)
        self.saveButton.clicked.connect(self.save_file)
        self.exportButton.clicked.connect(self.export_file)
        self.importButton.clicked.connect(self.import_file)
        
        # Add tooltips
        self.loadButton.setToolTip("Load settings from a JSON file")
        self.saveButton.setToolTip("Save current settings to the loaded file")
        self.exportButton.setToolTip("Export settings to a new file")
        self.importButton.setToolTip("Import settings from another file")
        self.contentTextEdit.setToolTip("JSON content editor")
        self.feedbackLabel.setToolTip("Status and feedback messages")
        
        # Initialize
        if json_file_path:
            self.load_json_file(json_file_path)
        
        self.show()
    
    def show_progress(self, show=True):
        """Show or hide progress bar with indeterminate progress"""
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate
            self.progress_bar.show()
        else:
            self.progress_bar.hide()
            self.progress_bar.setRange(0, 100)  # Reset to determinate
    
    def show_status(self, message, success=True):
        """Show status message with color indication"""
        if success:
            self.statusBar().setStyleSheet("QStatusBar { color: green }")
        else:
            self.statusBar().setStyleSheet("QStatusBar { color: red }")
        self.statusBar().showMessage(message)
    
    def load_json_file(self, file_path):
        """Load and display JSON file content"""
        try:
            self.show_progress()
            with open(file_path, 'r', encoding='utf-8') as f:
                self.settings_data = json.load(f)
                self.contentTextEdit.setPlainText(
                    json.dumps(self.settings_data, indent=2)
                )
            self.show_progress(False)
            self.show_status(f"Successfully loaded: {file_path}")
        except Exception as e:
            self.show_progress(False)
            self.show_status(f"Failed to load JSON file: {str(e)}", False)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load JSON file: {str(e)}"
            )
    
    def load_file(self):
        """Show dialog for loading a JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load JSON File",
            "",
            "JSON files (*.json);;All files (*.*)"
        )
        if file_path:
            self.current_file = file_path
            self.load_json_file(file_path)
    
    def save_file(self):
        """Save current content to JSON file"""
        try:
            content = self.contentTextEdit.toPlainText()
            # Validate JSON
            json.loads(content)  # Just validate, no need to store
            
            if not self.current_file:
                self.current_file, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save JSON File",
                    "",
                    "JSON files (*.json);;All files (*.*)"
                )
            
            if self.current_file:
                self.show_progress()
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.show_progress(False)
                self.show_status(f"Successfully saved to: {self.current_file}")
        except json.JSONDecodeError:
            self.show_progress(False)
            msg = "Invalid JSON format. Please check the content."
            self.show_status(msg, False)
            QMessageBox.critical(self, "Error", msg)
        except Exception as e:
            self.show_progress(False)
            self.show_status(f"Failed to save file: {str(e)}", False)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save file: {str(e)}"
            )
    
    def export_file(self):
        """Export current content to a new JSON file"""
        try:
            content = self.contentTextEdit.toPlainText()
            # Validate JSON
            json.loads(content)  # Just validate, no need to store
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export JSON File",
                "",
                "JSON files (*.json);;All files (*.*)"
            )
            
            if file_path:
                self.show_progress()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.show_progress(False)
                self.show_status(f"Successfully exported to: {file_path}")
        except json.JSONDecodeError:
            self.show_progress(False)
            msg = "Invalid JSON format. Please check the content."
            self.show_status(msg, False)
            QMessageBox.critical(self, "Error", msg)
        except Exception as e:
            self.show_progress(False)
            self.show_status(f"Failed to export file: {str(e)}", False)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export file: {str(e)}"
            )
    
    def import_file(self):
        """Import and merge JSON from another file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import JSON File",
                "",
                "JSON files (*.json);;All files (*.*)"
            )
            
            if file_path:
                self.show_progress()
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                    
                # If there's existing content, try to merge
                try:
                    current = self.contentTextEdit.toPlainText()
                    current_data = json.loads(current)
                    # Merge logic depends on the structure
                    if isinstance(current_data, dict):
                        current_data.update(imported_data)
                    elif isinstance(current_data, list):
                        current_data.extend(imported_data)
                    else:
                        current_data = imported_data
                except (json.JSONDecodeError, ValueError):
                    current_data = imported_data
                
                self.contentTextEdit.setPlainText(
                    json.dumps(current_data, indent=2)
                )
                self.show_progress(False)
                self.show_status(
                    f"Successfully imported and merged: {file_path}"
                )
        except json.JSONDecodeError:
            self.show_progress(False)
            msg = "Invalid JSON format in imported file."
            self.show_status(msg, False)
            QMessageBox.critical(self, "Error", msg)
        except Exception as e:
            self.show_progress(False)
            self.show_status(f"Failed to import file: {str(e)}", False)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to import file: {str(e)}"
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = SettingsManagerUI()
    app.exec_()
