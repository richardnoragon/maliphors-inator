#!/usr/bin/env python3
import sys
import os
import logging
import traceback
import json
import importlib
from PyQt6.QtWidgets import QApplication

def debug_imports():
    """Test all necessary imports and report status."""
    logger = logging.getLogger(__name__)
    required_modules = [
        ('pytest', 'pytest'),
        ('PyQt6', 'PyQt6'),
        ('tkinter', 'tkinter'),
        ('json', 'json'),
        ('unittest', 'unittest'),
        ('pytest-qt', 'pytestqt'),
        ('pytest-cov', 'pytest_cov'),
        ('pytest-asyncio', 'pytest_asyncio'),
        ('pytest-xvfb', 'pytest_xvfb')
    ]
    
    success = True
    for module_name, import_name in required_modules:
        try:
            __import__(import_name)
            logger.info(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            logger.error(f"✗ Failed to import {module_name}: {str(e)}")
            success = False
    return success

def check_test_files():
    """Verify all test files are present and importable."""
    logger = logging.getLogger(__name__)
    test_files = [
        'test_maliphors_inator_logic.py',
        'test_maliphors_inator_ui.py',
        'test_logging.py',
        'test_config.py'
    ]
    
    success = True
    for file in test_files:
        if os.path.exists(file):
            try:
                module_name = os.path.splitext(file)[0]
                __import__(module_name)
                logger.info(f"✓ Successfully loaded {file}")
            except Exception as e:
                logger.error(f"✗ Error importing {file}: {str(e)}")
                logger.debug(traceback.format_exc())
                success = False
        else:
            logger.error(f"✗ Test file not found: {file}")
            success = False
    return success

def check_test_data():
    """Verify test data files are present and valid."""
    logger = logging.getLogger(__name__)
    required_files = [
        ('malaphors.json', check_json_file),
        ('test_malaphors.json', check_json_file),
        ('log_manager.ui', check_ui_file),
        ('settings_manager.ui', check_ui_file)
    ]
    
    success = True
    for file, checker in required_files:
        if os.path.exists(file):
            try:
                if checker(file):
                    logger.info(f"✓ Validated {file}")
                else:
                    logger.error(f"✗ Invalid file format: {file}")
                    success = False
            except Exception as e:
                logger.error(f"✗ Error validating {file}: {str(e)}")
                success = False
        else:
            logger.error(f"✗ Missing required file: {file}")
            success = False
    return success

def check_json_file(filepath):
    """Validate JSON file format."""
    with open(filepath, 'r', encoding='utf-8') as f:
        json.load(f)
    return True

def check_ui_file(filepath):
    """Validate UI file format."""
    if not filepath.endswith('.ui'):
        return False
    # Basic check - file exists and has content
    return os.path.getsize(filepath) > 0

def check_qt_environment():
    """Verify Qt environment is properly set up."""
    logger = logging.getLogger(__name__)
    try:
        app = QApplication.instance() or QApplication([])
        logger.info("✓ Qt environment is properly configured")
        return True
    except Exception as e:
        logger.error(f"✗ Qt environment error: {str(e)}")
        return False

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)
    
    logger.info("=== Test Environment Diagnostics ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    
    # Run diagnostics
    imports_ok = debug_imports()
    files_ok = check_test_files()
    data_ok = check_test_data()
    qt_ok = check_qt_environment()
    
    if all([imports_ok, files_ok, data_ok, qt_ok]):
        logger.info("\n✓ All diagnostics passed. Ready to run tests.")
        return 0
    else:
        logger.error("\n✗ Some checks failed. Please fix the issues above before running tests.")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nDiagnostics interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print(traceback.format_exc())
        sys.exit(1)