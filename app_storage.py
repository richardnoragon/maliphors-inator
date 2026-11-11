"""Shared Linux data location, migration, session locks and verified backups."""
from contextlib import AbstractContextManager, nullcontext
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile
from app_resources import resource_path

STATE_FILES = ('malaphors.json', 'history.json', 'favorites.json', 'ratings.json',
               'generation_templates.json', 'settings_profiles.json', 'ui_preferences.json',
               'generation_preferences.json')
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024


def resolve_data_dir(value=None):
    if value is not None:
        return Path(value).expanduser().resolve()
    override = os.environ.get('MALIPHORS_INATOR_DATA_DIR')
    if override:
        return Path(override).expanduser().resolve()
    return (Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'maliphors-inator' / 'data').resolve()


def initialize_data(directory, *, migrate=False):
    """Copy a legacy store once without moving files or overwriting a destination."""
    from maliphors_inator_logic import atomic_write_json
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    marker = directory / 'migration.json'
    if marker.exists() or (directory / 'malaphors.json').exists():
        return
    source = None
    if migrate:
        share = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share'))
        candidates = [share / 'maliphors-inator-daily/data', share / 'malaphors-inator-daily/data',
                      Path.cwd(), resource_path('malaphors.json').parent]
        source = next((p for p in candidates if p.resolve() != directory.resolve()
                       and (p / 'malaphors.json').is_file()), None)
    if source:
        copied = []
        try:
            bundled = resource_path('malaphors.json').parent.resolve()
            with (nullcontext() if source.resolve() == bundled else StoreSession(source)):
                for name in STATE_FILES:
                    original, destination = source / name, directory / name
                    if original.is_file() and not destination.exists():
                        copied.append(name)
                        with destination.open('xb') as stream:
                            stream.write(original.read_bytes())
                atomic_write_json(marker, {'source': str(source.resolve()), 'copied': copied,
                                           'date': datetime.now(timezone.utc).isoformat()})
        except Exception:
            for name in copied:
                (directory / name).unlink(missing_ok=True)
            raise


class StoreSession(AbstractContextManager):
    """One desktop/CLI writer per directory; release automatically on process exit."""
    def __init__(self, directory):
        self.directory = Path(directory)
        self.stream = None

    def __enter__(self):
        import fcntl
        self.directory.mkdir(parents=True, exist_ok=True)
        self.stream = (self.directory / '.session.lock').open('a')
        try:
            fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.stream.close()
            raise OSError(f'Data is already open in another session: {self.directory}') from None
        return self

    def __exit__(self, *args):
        if self.stream:
            self.stream.close()


def validate_state(name, value):
    """Validate complete restore payloads before any destination is changed."""
    from library_workflows import phrase_error
    if name == 'malaphors.json':
        if not isinstance(value, dict) or not isinstance(value.get('proverbs'), list):
            raise ValueError('Invalid phrase library')
        if any(phrase_error(p) for p in value['proverbs']):
            raise ValueError('Invalid phrase records')
    elif name == 'history.json':
        entries = value.get('history') if isinstance(value, dict) else value
        if not isinstance(entries, list) or any(not isinstance(p, dict) or any(
                not isinstance(p.get(k), str) or not p[k] for k in ('malaphor', 'source1', 'source2'))
                or ('timestamp' in p and not isinstance(p['timestamp'], str)) for p in entries):
            raise ValueError('Invalid history')
    elif name == 'favorites.json':
        if not isinstance(value, dict) or not isinstance(value.get('favorites'), list) or any(not isinstance(p, str) for p in value['favorites']):
            raise ValueError('Invalid favorites')
    elif name == 'ratings.json':
        if not isinstance(value, dict) or not isinstance(value.get('ratings'), dict) or any(
                not isinstance(r, list) or any(type(n) is not int or not 1 <= n <= 5 for n in r) for r in value['ratings'].values()):
            raise ValueError('Invalid ratings')
    elif name == 'generation_templates.json':
        if not isinstance(value, list) or any(not isinstance(p, dict) or any(not isinstance(p.get(k), str) for k in ('name', 'pattern')) for p in value):
            raise ValueError('Invalid templates')
    elif not isinstance(value, dict):
        raise ValueError(f'Expected an object in {name}')
    if name == 'settings_profiles.json' and any(not isinstance(p, dict) for p in value.values()):
        raise ValueError('Invalid settings profiles')
    if name == 'ui_preferences.json' and value.get('theme', 'light') not in ('light', 'dark'):
        raise ValueError('Invalid theme')
    if name == 'generation_preferences.json':
        if not isinstance(value.get('blocked', []), list) or any(not isinstance(pair, list) or len(pair) != 2 or any(not isinstance(s, str) for s in pair) for pair in value.get('blocked', [])):
            raise ValueError('Invalid blocked pairs')


def create_backup(directory, destination=None, *, reason='manual', retain=14):
    """Atomic ZIP snapshot of known state, including checksums (no extraction)."""
    directory = Path(directory)
    paths = [directory / name for name in STATE_FILES if (directory / name).is_file()]
    if not paths:
        return None
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination = Path(destination) if destination else directory / 'backups' / f'{stamp}-{reason}.zip'
    if destination.resolve() in [p.resolve() for p in paths]:
        raise ValueError('Backup destination must not replace a data file')
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=destination.parent, suffix='.zip.tmp')
    os.close(fd)
    try:
        checksums = {}
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                content = path.read_bytes()
                archive.writestr(path.name, content)
                checksums[path.name] = hashlib.sha256(content).hexdigest()
            archive.writestr('manifest.json', json.dumps({'format': 1, 'reason': reason, 'files': checksums}))
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    if destination.parent.resolve() == (directory / 'backups').resolve() and reason == 'startup':
        for old in sorted(destination.parent.glob('*-startup.zip'))[:-retain]:
            old.unlink()
    return destination


def preview_restore(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) - set(STATE_FILES) - {'manifest.json'}:
            raise ValueError('Backup contains duplicate or unexpected paths')
        if sum(info.file_size for info in infos) > MAX_ARCHIVE_BYTES:
            raise ValueError('Backup exceeds the 100 MB uncompressed limit')
        files = {}
        for name in names:
            if name == 'manifest.json':
                continue
            content = archive.read(name)
            value = json.loads(content)
            validate_state(name, value)
            files[name] = content
        if not files:
            raise ValueError('Backup contains no application data')
        if 'manifest.json' in names:
            manifest = json.loads(archive.read('manifest.json'))
            actual = {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}
            if not isinstance(manifest, dict) or manifest.get('format') != 1 or manifest.get('files') != actual:
                raise ValueError('Backup checksum mismatch')
        return files


def restore_backup(directory, archive_path, *, expected_digest=None):
    """Validate, make a safety backup, then replace with rollback on failure."""
    from maliphors_inator_logic import atomic_write_json
    directory = Path(directory)
    payload = Path(archive_path).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if expected_digest is not None and digest != expected_digest:
        raise ValueError('Backup changed since preview; preview it again')
    # Read the same bytes that were fingerprinted, avoiding a path swap race.
    from io import BytesIO
    files = preview_restore(BytesIO(payload))
    before = {name: (directory / name).read_bytes() if (directory / name).exists() else None for name in files}
    safety = create_backup(directory, reason='before-restore')
    written = []
    try:
        for name, content in files.items():
            atomic_write_json(directory / name, json.loads(content))
            written.append(name)
    except Exception as exc:
        rollback_errors = []
        for name in reversed(written):
            try:
                if before[name] is None:
                    (directory / name).unlink(missing_ok=True)
                else:
                    _replace_bytes(directory / name, before[name])
            except Exception as rollback:
                rollback_errors.append(f'{name}: {rollback}')
        if rollback_errors:
            raise OSError(f'Restore failed: {exc}; rollback needs recovery: {rollback_errors}. Safety backup: {safety}') from exc
        raise
    return {'files': list(files), 'safety_backup': str(safety) if safety else None}


def _replace_bytes(path, content):
    """Rollback must preserve even a malformed original byte for byte."""
    import stat
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else None
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.rollback-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if mode is not None:
            os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
