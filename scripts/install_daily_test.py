"""Install/update a local Linux daily-test snapshot without replacing saved data."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv


def desktop_quote(value):
    return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'


def preserve_daily_data(share, base):
    """Reuse the previous installation's data and lock without rewriting history."""
    legacy = share / 'malaphors-inator-daily' / 'data'
    destination = base / 'data'
    if legacy.is_dir() and not destination.exists() and not destination.is_symlink():
        destination.symlink_to(legacy, target_is_directory=True)


def main():
    if sys.platform != 'linux':
        raise SystemExit('This installer targets the current Linux laptop.')
    repo = Path(__file__).resolve().parents[1]
    share = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')).resolve()
    base = share / 'maliphors-inator-daily'
    base.mkdir(parents=True, exist_ok=True)
    preserve_daily_data(share, base)
    environment = base / 'venv'
    python = environment / 'bin/python'
    if not python.exists():
        venv.EnvBuilder(with_pip=False).create(environment)
    pip = shutil.which('pip') or shutil.which('pip3')
    if not pip:
        raise SystemExit('Install pip for your Python distribution, then rerun this installer.')
    subprocess.run([pip, '--python', str(python), 'install', '-r', str(repo / 'requirements.txt')], check=True)
    sys.path.insert(0, str(repo))
    from app_resources import SNAPSHOT_FILES
    files = SNAPSHOT_FILES
    digest = hashlib.sha256()
    for file in files + ['scripts/daily_launcher.py']:
        digest.update(file.encode())
        digest.update((repo / file).read_bytes())
    build = datetime.now(timezone.utc).strftime('%Y%m%d') + '-' + digest.hexdigest()[:10]
    bundle = base / 'builds' / build
    bundle.mkdir(parents=True, exist_ok=True)
    for file in files:
        shutil.copyfile(repo / file, bundle / file)
    shutil.copyfile(repo / 'scripts/daily_launcher.py', bundle / 'daily_launcher.py')
    (bundle / 'build.json').write_text(json.dumps({'build': build, 'source': str(repo)}, indent=2))
    # Swap the entry point only after the snapshot and dependencies are present.
    link = base / '.current-new'
    link.unlink(missing_ok=True)
    link.symlink_to(bundle, target_is_directory=True)
    link.replace(base / 'current')
    icon = base / 'daily-test.svg'
    icon.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" rx="26" fill="#254f67"/><text x="64" y="88" text-anchor="middle" font-family="sans-serif" font-size="86" font-weight="bold" fill="#fff">M</text><circle cx="105" cy="23" r="14" fill="#f5b94c"/></svg>')
    entry = '\n'.join(['[Desktop Entry]', 'Type=Application', 'Version=1.0',
        'Name=maliphors-inator Daily Test', 'Comment=Pre-alpha daily testing with separate saved data',
        f'Exec={desktop_quote(python)} {desktop_quote(base / "current/daily_launcher.py")}',
        f'Icon={icon}', 'Terminal=false', 'Categories=Utility;', 'StartupNotify=false', ''])
    applications = share / 'applications'
    applications.mkdir(parents=True, exist_ok=True)
    launcher = applications / 'maliphors-inator-daily.desktop'
    launcher.write_text(entry)
    launcher.chmod(0o755)
    desktop = subprocess.run(['xdg-user-dir', 'DESKTOP'], capture_output=True, text=True, check=True).stdout.strip()
    if desktop and Path(desktop).is_dir() and Path(desktop) != Path.home():
        shortcut = Path(desktop) / launcher.name
        shutil.copyfile(launcher, shortcut)
        shortcut.chmod(0o755)
        print(f'Desktop shortcut: {shortcut}')
    subprocess.run(['desktop-file-validate', str(launcher)], check=True)
    # Retire old entry points only after the new desktop entry validates.
    (applications / 'malaphors-inator-daily.desktop').unlink(missing_ok=True)
    if desktop and Path(desktop).is_dir() and Path(desktop) != Path.home():
        (Path(desktop) / 'malaphors-inator-daily.desktop').unlink(missing_ok=True)
    print(f'Installed build: {build}\nApplication menu: maliphors-inator Daily Test\nData: {base / "data"}\nLauncher: {launcher}')


if __name__ == '__main__':
    main()
