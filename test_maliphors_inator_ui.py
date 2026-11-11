import json
import unittest
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import tkinter as tk
from PyQt6 import QtWidgets
from PyQt6.QtTest import QTest
from maliphors_inator_ui import MaliphorsInatorApp
from maliphors_inator_logic import MalaphorGenerator

@pytest.mark.gui
class TestMalaphorUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Qt application and Tkinter root for all tests."""
        cls.qapp = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        # Create a root window that will be available for all tests
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the window but keep it active

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock clipboard methods
        self.root.clipboard_clear = MagicMock()
        self.root.clipboard_append = MagicMock()
        self.root.clipboard_get = MagicMock(return_value="")
        
        # Initialize the app with our root window
        self.app = MaliphorsInatorApp(root=self.root)
        self.app.generator.stop_auto_save()
        self.app.generator = MagicMock(spec=MalaphorGenerator)
        self.app.generator.history = []
        self.app.generator.proverbs = []
        self.app.generator.favorites = []
        
        # Set up mock generator responses
        self.app.generator.generate_malaphor.return_value = {
            "malaphor": "Test malaphor",
            "source1": "Source 1",
            "source2": "Source 2"
        }

    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'app'):
            self.app.close()
            
    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment."""
        if hasattr(cls, 'root'):
            cls.root.destroy()
        QTest.qWait(100)  # Process any pending Qt events

    @patch('tkinter.messagebox.showinfo')
    def test_generate_button(self, mock_showinfo):
        """Test the generate button functionality."""
        # Trigger generation
        self.app.generate_malaphor()
        
        # Verify generator was called
        self.app.generator.generate_malaphor.assert_called_once()
        # Verify label was updated
        self.assertIn("Test malaphor", self.app.sentence_label.cget("text"))

    @patch('tkinter.messagebox.showinfo')
    def test_generate_button_uses_selected_language(self, mock_showinfo):
        """The selected language should be passed to the generator when creating a malaphor."""
        self.app.language_var.set("es")

        self.app.generate_malaphor()

        self.app.generator.generate_malaphor.assert_called_once_with(language="es")

    def test_main_window_exposes_quick_win_actions(self):
        """Quick-win actions should be visible in the main window for users to access."""
        self.assertTrue(hasattr(self.app, "copy_stats_button"))
        self.assertTrue(hasattr(self.app, "recent_searches_button"))
        self.assertIsNotNone(self.app.copy_stats_button)
        self.assertIsNotNone(self.app.recent_searches_button)
        self.assertIn("copy_generation_stats", self.app.copy_stats_button.cget("command"))
        self.assertIn("show_recent_searches", self.app.recent_searches_button.cget("command"))

    @patch('tkinter.messagebox.showinfo')
    def test_copy_to_clipboard(self, mock_showinfo):
        """Test the copy to clipboard functionality."""
        test_text = "Test malaphor to copy"
        self.app.sentence_label.config(text=test_text)
        
        # Trigger copy action
        self.app.copy_to_clipboard()
        
        # Verify clipboard operations
        self.root.clipboard_clear.assert_called_once()
        self.root.clipboard_append.assert_called_once_with(test_text)
        mock_showinfo.assert_called_once()

    @patch('tkinter.messagebox.showinfo')
    def test_add_to_favorites(self, mock_showinfo):
        """Test adding to favorites functionality."""
        test_text = "Test favorite malaphor"
        self.app.sentence_label.config(text=test_text)
        
        # Add to favorites
        self.app.add_to_favorites()
        
        # Verify addition
        self.app.generator.add_to_favorites.assert_called_once_with(test_text)
        mock_showinfo.assert_called_once()

    @patch.object(MalaphorGenerator, 'start_auto_save')
    @patch.object(MalaphorGenerator, 'stop_auto_save')
    def test_app_auto_save_lifecycle(self, mock_stop_auto_save, mock_start_auto_save):
        """Test the app starts and stops periodic auto-save during its lifecycle."""
        root = tk.Tk()
        root.withdraw()
        try:
            app = MaliphorsInatorApp(root=root)
            mock_start_auto_save.assert_called_once_with(interval_seconds=300.0)

            app.close()
            mock_stop_auto_save.assert_called_once()
        finally:
            root.destroy()

    def test_history_update(self):
        """Test history display update."""
        test_history = [
            {
                "malaphor": "Malaphor 1",
                "source1": "Source 1-1",
                "source2": "Source 1-2"
            },
            {
                "malaphor": "Malaphor 2",
                "source1": "Source 2-1",
                "source2": "Source 2-2"
            }
        ]
        self.app.generator.history = test_history[-2:]
        
        # Update history display
        self.app.update_history()
        
        # Verify history was updated
        history_text = self.app.history_text.get("1.0", tk.END)
        self.assertIn("Malaphor 1", history_text)
        self.assertIn("Malaphor 2", history_text)
        self.assertIn("Source 1-1", history_text)
        self.assertIn("Source 2-2", history_text)

    @patch('tkinter.Toplevel')
    def test_manual_combine_dialog(self, mock_toplevel):
        """Test the manual combine dialog."""
        # Mock proverbs
        mock_proverbs = [
            {"original": "Test proverb 1"},
            {"original": "Test proverb 2"}
        ]
        self.app.generator.get_all_proverbs.return_value = mock_proverbs
        
        # Show the dialog
        self.app.show_manual_combine_dialog()
        
        # Verify proverbs were loaded
        self.app.generator.get_all_proverbs.assert_called_once()

    def test_add_proverb_dialog(self):
        """Test the add proverb dialog."""
        # Show the dialog
        dialog = self.app.show_add_proverb_dialog()
        
        # Verify dialog creation
        self.assertIsNotNone(dialog)

    def test_manage_phrases_dialog(self):
        """Test the phrase management dialog."""
        # Mock proverbs
        mock_proverbs = [
            {"original": "Test proverb 1"},
            {"original": "Test proverb 2"}
        ]
        self.app.generator.get_all_proverbs.return_value = mock_proverbs
        
        # Show the dialog
        dialog = self.app.show_manage_phrases_dialog()
        
        # Verify dialog creation and data loading
        self.assertIsNotNone(dialog)
        self.app.generator.get_all_proverbs.assert_called_once()

    @patch('tkinter.messagebox.showinfo')
    @patch('tkinter.filedialog')
    def test_import_export_dialogs(self, mock_filedialog, mock_showinfo):
        """Test import/export dialog creation."""
        test_file = "test_export.json"
        mock_filedialog.asksaveasfilename.return_value = test_file
        mock_filedialog.askopenfilename.return_value = test_file
        
        # Test export dialogs
        self.app.export_originals_dialog()
        self.app.export_generated_dialog()
        self.app.export_favorites_dialog()
        
        # Test import dialog
        self.app.import_malaphors_dialog()
        
        # Verify dialogs were shown
        self.assertGreater(mock_filedialog.asksaveasfilename.call_count, 0)
        mock_filedialog.askopenfilename.assert_called_once()


def test_history_persists_and_loads(monkeypatch, tmp_path):
    """History entries should be saved to disk and restored on startup."""
    monkeypatch.chdir(tmp_path)
    malaphors = {
        "proverbs": [
            {"original": "A bird in the hand", "beginning": "A bird in the hand", "ending": "is worth two in the bush"},
            {"original": "Too many cooks spoil the broth", "beginning": "Too many cooks", "ending": "spoil the broth"},
        ]
    }
    (tmp_path / "malaphors.json").write_text(json.dumps(malaphors), encoding="utf-8")

    generator = MalaphorGenerator()
    result = generator.generate_malaphor()

    history_file = tmp_path / "history.json"
    assert history_file.exists()
    saved_history = json.loads(history_file.read_text(encoding="utf-8"))
    assert isinstance(saved_history, list)
    assert saved_history[-1]["malaphor"] == result["malaphor"]
    assert "timestamp" in saved_history[-1]

    saved_history = [
        {
            "malaphor": "Persisted malaphor",
            "source1": "Source one",
            "source2": "Source two",
            "timestamp": "2026-09-08T00:00:00+00:00",
        }
    ]
    history_file.write_text(json.dumps(saved_history), encoding="utf-8")

    reloaded = MalaphorGenerator()
    assert reloaded.history == saved_history

if __name__ == '__main__':
    print("Running MalaphorUI tests...")
    sys.stdout.flush()  # Ensure output is displayed immediately
    unittest.main(verbosity=2, buffer=False)