"""Drive real Linux/Tk dialogs against temporary data; run from a graphical session.

Usage: python scripts/desktop_walkthrough.py
The script invokes real buttons and dialogs through Tcl, without replacing file
pickers or message boxes. It prints the temporary evidence directory on success.
"""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import tkinter as tk

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from maliphors_inator_ui import MaliphorsInatorApp


def descendants(root, widget='.'):
    for child in root.tk.splitlist(root.tk.call('winfo', 'children', widget)):
        yield str(child)
        yield from descendants(root, child)


def click(root, label, scope='.'):
    for widget in descendants(root, scope):
        if root.tk.call('winfo', 'class', widget) in ('Button', 'TButton'):
            if root.tk.call(widget, 'cget', '-text') == label:
                root.tk.call(widget, 'invoke')
                root.update()
                return
    raise AssertionError(f'Button not found: {label}')


def main():
    if sys.platform != 'linux':
        raise SystemExit('This walkthrough uses Linux/Tk file-dialog widget names.')
    data = Path(tempfile.mkdtemp(prefix='maliphors-inator-walkthrough-'))
    shutil.copyfile(REPO / 'malaphors.json', data / 'malaphors.json')
    old_cwd = Path.cwd()
    os.chdir(data)
    app = None
    failures = []
    try:
        phrase = {'original': 'Daily walkthrough sentinel', 'beginning': 'Daily', 'ending': 'walkthrough sentinel'}
        Path('incoming.json').write_text(json.dumps({'proverbs': [phrase]}))
        app = MaliphorsInatorApp()
        app.root.report_callback_exception = lambda *exc: (failures.append(str(exc[1])), app.root.quit())
        app.root.update()

        def later(callback):
            def guarded():
                try:
                    callback()
                except Exception as exc:
                    # Exit rather than leave a failed dialog automation hanging.
                    print(f'Walkthrough failed: {exc}', file=sys.stderr, flush=True)
                    os._exit(1)
            app.root.after(250, guarded)

        def acknowledge():
            click(app.root, 'OK')

        def choose_file(filename, cancel=False):
            def choose():
                base = '.__tk_filedialog.contents.f2'
                assert app.root.tk.call('winfo', 'exists', base + '.ent')
                if cancel:
                    app.root.tk.call(base + '.cancel', 'invoke')
                    return
                app.root.tk.call(base + '.ent', 'delete', 0, 'end')
                app.root.tk.call(base + '.ent', 'insert', 0, str(data / filename))
                later(acknowledge)
                app.root.tk.call(base + '.ok', 'invoke')
            later(choose)

        click(app.root, 'Generate')
        later(acknowledge)
        click(app.root, 'Add to Favorites')
        assert len(app.generator.history) == len(app.generator.favorites) == 1
        choose_file('incoming.json')
        click(app.root, 'Import Malaphors')
        assert app.generator.search('sentinel') == [phrase]
        choose_file('', cancel=True)
        click(app.root, 'Import Malaphors')
        for label, stem, key in [('Export Originals', 'originals', 'proverbs'),
                                 ('Export Generated', 'generated', 'history')]:
            for suffix in ('json', 'txt'):
                choose_file(f'{stem}.{suffix}')
                click(app.root, label)
                content = Path(f'{stem}.{suffix}').read_text()
                assert json.loads(content)[key] if suffix == 'json' else content
        click(app.root, 'Manage Favorites')
        dialog = next(w for w in app.root.winfo_children() if isinstance(w, tk.Toplevel))
        for suffix in ('json', 'txt'):
            choose_file(f'favorites-export.{suffix}')
            click(app.root, 'Export Favorites', str(dialog))
            assert Path(f'favorites-export.{suffix}').read_text()
        click(app.root, 'Close', str(dialog))
        app.root.update()
        from PIL import ImageGrab
        x, y = app.root.winfo_rootx(), app.root.winfo_rooty()
        try:
            ImageGrab.grab(bbox=(x, y, x + app.root.winfo_width(), y + app.root.winfo_height()), xdisplay=app.root.winfo_screen()).save(data / 'desktop.png')
        except Exception as exc:
            print(f'Screenshot unavailable on this display: {exc}', flush=True)
        saved = app.generator.favorites[:]
        later(acknowledge)
        app.root.after(20, lambda: click(app.root, 'Exit'))
        app.run()
        assert not app.generator._auto_save_thread.is_alive()
        app.root.destroy()
        app = MaliphorsInatorApp()
        app.root.update()
        assert app.generator.favorites == saved
        assert len(app.generator.history) == 1
        assert app.generator.search('sentinel') == [phrase]
        assert not failures, failures
        print(f'PASS: real buttons, file dialogs, cancellation, six exports, exit and reopen. Evidence: {data}')
    finally:
        if app is not None:
            app.close()
            app.root.destroy()
        os.chdir(old_cwd)


if __name__ == '__main__':
    main()
