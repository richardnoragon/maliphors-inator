"""Launch the installed Linux pre-alpha snapshot with separate daily-test data."""
import argparse
import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import shutil
import sys
import tkinter as tk
from tkinter import messagebox
import zipfile
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke-test', action='store_true', help='Open the window briefly and exit')
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent
    base = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'maliphors-inator-daily'
    data = Path(os.environ.get('MALIPHORS_INATOR_DAILY_DATA_DIR',
        os.environ.get('MALAPHOR_DAILY_DATA_DIR', base / 'data'))).resolve()
    data.mkdir(parents=True, exist_ok=True)
    # Keep this descriptor open throughout the session to prevent two writers.
    with (data / '.session.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            if args.smoke_test:
                print("Daily Test already running", file=sys.stderr)
                return 2
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo('Daily Test already running', 'Use the existing maliphors-inator Daily Test window.', parent=root)
            root.destroy()
            return 0

        logger = logging.getLogger('maliphors_inator')
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(data / 'daily-test.log', maxBytes=1_000_000, backupCount=3)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        logger.addHandler(handler)
        try:
            existing = list(data.glob('*.json'))
            if existing:
                backups = data / 'backups'
                backups.mkdir(exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                with zipfile.ZipFile(backups / f'{stamp}.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
                    for file in existing:
                        archive.write(file, file.name)
                for old in sorted(backups.glob('*.zip'))[:-14]:
                    old.unlink()
            if not (data / 'malaphors.json').exists():
                shutil.copyfile(bundle / 'malaphors.json', data / 'malaphors.json')
            build = json.loads((bundle / 'build.json').read_text())['build']
            os.chdir(data)
            sys.path.insert(0, str(bundle))
            from maliphors_inator_ui import MaliphorsInatorApp
            app = MaliphorsInatorApp()
            app.root.title(f'maliphors-inator Daily Test — pre-alpha — {build}')
            def callback_error(exc_type, exc, traceback):
                logger.error('Desktop action failed', exc_info=(exc_type, exc, traceback))
                messagebox.showerror('Daily Test error', f'{exc}\n\nDetails: {data / "daily-test.log"}', parent=app.root)
            app.root.report_callback_exception = callback_error
            logger.info('Starting build %s with data in %s', build, data)
            try:
                if args.smoke_test:
                    app.root.after(300, app.root.quit)
                app.run()
            finally:
                try:
                    app.root.destroy()
                except tk.TclError:
                    pass
            logger.info('Daily Test closed')
            return 0
        except Exception as exc:
            logger.exception('Daily Test startup failed')
            if args.smoke_test:
                print(f'Daily Test startup failed: {exc}', file=sys.stderr)
                return 1
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror('Daily Test could not start', f'{exc}\n\nLog: {data / "daily-test.log"}', parent=root)
            root.destroy()
            return 1
        finally:
            logger.removeHandler(handler)
            handler.close()


if __name__ == '__main__':
    raise SystemExit(main())
