"""Verify the installed launcher contract without using the user's daily data."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

pytestmark = [pytest.mark.gui, pytest.mark.skipif(sys.platform != 'linux', reason='Linux desktop launcher')]
REPO = Path(__file__).resolve().parent


@pytest.fixture
def bundle(tmp_path):
    destination = tmp_path / 'bundle'
    destination.mkdir()
    for name in ('maliphors_inator_logic.py', 'maliphors_inator_ui.py', 'user_assistance.py', 'USER_GUIDE.md', 'CHANGELOG.md', 'LICENSE', 'malaphors.json'):
        shutil.copyfile(REPO / name, destination / name)
    shutil.copyfile(REPO / 'scripts/daily_launcher.py', destination / 'daily_launcher.py')
    (destination / 'build.json').write_text(json.dumps({'build': 'test-snapshot'}))
    return destination


def launch(bundle, data):
    return subprocess.run([sys.executable, str(bundle / 'daily_launcher.py'), '--smoke-test'],
        env=dict(os.environ, MALIPHORS_INATOR_DAILY_DATA_DIR=str(data)), capture_output=True, text=True, timeout=20)


def test_launcher_seeds_preserves_and_backs_up_state(bundle, tmp_path):
    data = tmp_path / 'daily-data'
    first = launch(bundle, data)
    assert first.returncode == 0, first.stderr
    assert (data / 'malaphors.json').read_bytes() == (bundle / 'malaphors.json').read_bytes()
    favorites = {'favorites': ['Keep my daily favorite']}
    (data / 'favorites.json').write_text(json.dumps(favorites))
    library = {'proverbs': [
        {'original': 'Daily library phrase', 'beginning': 'Daily', 'ending': 'library phrase'}]}
    (data / 'malaphors.json').write_text(json.dumps(library))
    second = launch(bundle, data)
    assert second.returncode == 0, second.stderr
    assert json.loads((data / 'favorites.json').read_text()) == favorites
    assert json.loads((data / 'malaphors.json').read_text()) == library
    archives = list((data / 'backups').glob('*.zip'))
    assert len(archives) == 1
    with zipfile.ZipFile(archives[0]) as archive:
        assert json.loads(archive.read('favorites.json')) == favorites
    assert 'test-snapshot' in (data / 'daily-test.log').read_text()


def test_launcher_refuses_second_writer(bundle, tmp_path):
    import fcntl
    data = tmp_path / 'daily-data'
    data.mkdir()
    with (data / '.session.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        second = launch(bundle, data)
        assert second.returncode == 2, second.stderr
        assert not (data / 'malaphors.json').exists()


def test_launcher_backup_can_restore_daily_data(bundle, tmp_path):
    data = tmp_path / 'daily-data'
    assert launch(bundle, data).returncode == 0
    favorite = {'favorites': ['Recover this daily favorite']}
    (data / 'favorites.json').write_text(json.dumps(favorite))
    history = [{'malaphor': 'Restored blend', 'source1': 'One', 'source2': 'Two',
                'timestamp': '2026-10-01T12:00:00+00:00'}]
    (data / 'history.json').write_text(json.dumps(history))
    assert launch(bundle, data).returncode == 0
    archive_path = next((data / 'backups').glob('*.zip'))
    names = ['malaphors.json', 'favorites.json', 'history.json']
    with zipfile.ZipFile(archive_path) as archive:
        expected = {name: archive.read(name) for name in names}
    for name in names:
        (data / name).write_text('{damaged')
    # Restore only known JSON names into the closed application's data directory.
    for name, contents in expected.items():
        (data / name).write_bytes(contents)
    result = launch(bundle, data)
    assert result.returncode == 0, result.stderr
    assert json.loads((data / 'favorites.json').read_text()) == favorite
    assert json.loads((data / 'history.json').read_text()) == history
    assert (data / 'malaphors.json').read_bytes() == expected['malaphors.json']
