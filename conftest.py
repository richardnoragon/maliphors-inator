import pytest
import sys
import os
import json
import tempfile
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
import tkinter as tk

# Ensure we're using the test configuration
os.environ['MALIPHORS_INATOR_TEST_MODE'] = 'True'

@pytest.fixture(scope='session')
def qapp():
    """Create a Qt application for the entire test session."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def mock_tkinter(monkeypatch):
    """Mock tkinter components for testing."""
    class MockTk:
        def __init__(self):
            self.calls = []
            
        def title(self, *args):
            self.calls.append(('title', args))
            
        def geometry(self, *args):
            self.calls.append(('geometry', args))
            
        def configure(self, *args, **kwargs):
            self.calls.append(('configure', args, kwargs))
            
        def destroy(self):
            self.calls.append(('destroy',))
            
        def clipboard_clear(self):
            self.calls.append(('clipboard_clear',))
            
        def clipboard_append(self, text):
            self.calls.append(('clipboard_append', text))
            
        def update(self):
            self.calls.append(('update',))
            
        def mainloop(self):
            self.calls.append(('mainloop',))
    
    mock_tk = MockTk()
    monkeypatch.setattr('tkinter.Tk', lambda: mock_tk)
    return mock_tk

@pytest.fixture
def qt_log_manager(qapp):
    """Create a Qt-based log manager for testing."""
    from log_manager import LogManager
    log_manager = LogManager()
    yield log_manager
    log_manager.close()

@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory(prefix='maliphors_inator_test_') as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield temp_dir
        os.chdir(old_cwd)

@pytest.fixture
def test_malaphors():
    """Create a sample malaphors dataset for testing."""
    return {
        "proverbs": [
            {
                "original": "Test proverb 1",
                "beginning": "Test",
                "ending": "proverb 1"
            },
            {
                "original": "Test proverb 2",
                "beginning": "Another",
                "ending": "test"
            }
        ]
    }

@pytest.fixture
def mock_generator():
    """Create a mock malaphor generator."""
    mock = MagicMock()
    mock.generate_malaphor.return_value = {
        "malaphor": "Test malaphor",
        "source1": "Test proverb 1",
        "source2": "Test proverb 2"
    }
    return mock

@pytest.fixture(autouse=True)
def setup_test_env(temp_test_dir, test_malaphors, monkeypatch):
    """Set up test environment before each test."""
    monkeypatch.setenv("MALIPHORS_INATOR_DATA_DIR", temp_test_dir)
    # Create test data files
    with open('test_malaphors.json', 'w') as f:
        json.dump(test_malaphors, f)
    
    # Create empty favorites file
    with open('favorites.json', 'w') as f:
        json.dump({"favorites": []}, f)
    
    yield
    
    # Cleanup is handled by temp_test_dir fixture

def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", 
                           "gui: mark test as requiring GUI (Qt/tkinter)")
    config.addinivalue_line("markers", 
                           "core: mark test as testing core functionality")
    config.addinivalue_line("markers", 
                           "logging: mark test as testing logging functionality")
    config.addinivalue_line("markers", 
                           "slow: mark test as taking longer to run")
    config.addinivalue_line("markers", 
                           "integration: mark test as integration test")
    config.addinivalue_line("markers", 
                           "unit: mark test as unit test")