"""Locate source-checkout or wheel-installed application resources."""
from pathlib import Path
import sysconfig


def resource_path(name):
    local = Path(__file__).resolve().parent / name
    if local.is_file():
        return local
    return Path(sysconfig.get_path('data')) / 'share' / 'maliphors-inator' / name

SNAPSHOT_FILES = [
    'main.py', 'maliphors_inator_cli.py', 'maliphors_inator_logic.py',
    'maliphors_inator_ui.py', 'user_assistance.py', 'desktop_workflows.py',
    'app_storage.py', 'app_resources.py', 'app_version.py', 'library_workflows.py',
    'USER_GUIDE.md', 'CHANGELOG.md', 'LICENSE', 'malaphors.json', 'requirements.txt',
]
