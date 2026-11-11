"""Release checks using real widgets, files, and CLI processes in disposable data directories."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tkinter as tk

import pytest

from maliphors_inator_logic import MalaphorGenerator
from maliphors_inator_ui import MaliphorsInatorApp

REPO = Path(__file__).resolve().parent


@pytest.fixture
def phrase_library():
    shutil.copyfile(REPO / 'malaphors.json', 'malaphors.json')


@pytest.mark.parametrize('entrypoint', ['main.py', 'maliphors_inator_cli.py'])
def test_documented_cli_flows(phrase_library, entrypoint):
    def cli(*args, code=0):
        result = subprocess.run([sys.executable, str(REPO / entrypoint), *args],
                                capture_output=True, text=True, timeout=20)
        assert result.returncode == code, result.stderr
        assert 'Traceback' not in result.stderr
        return result.stdout

    assert '--generate' in cli('--help')
    assert len(json.loads(cli('--generate', '--count', '3', '--output-format', 'json'))) == 3
    assert len(json.loads(cli('--generate', '--count', '5', '--smart', '--output-format', 'json'))) == 5
    assert cli('--search', 'bird')
    cli('--export', 'originals.json')
    cli('--export', 'originals.txt', '--export-format', 'text')
    assert json.loads(Path('originals.json').read_text())['proverbs']
    assert Path('originals.txt').read_text()
    incoming = {'original': 'Release sentinel phrase', 'beginning': 'Release', 'ending': 'sentinel phrase'}
    Path('incoming.json').write_text(json.dumps({'proverbs': [incoming]}))
    cli('--import-file', 'incoming.json')
    assert 'Release sentinel phrase' in cli('--search', 'sentinel')
    cli('--import-file', 'incoming.json', code=1)
    assert len(MalaphorGenerator().history) == 8


@pytest.mark.gui
def test_desktop_file_flows_and_shutdown(phrase_library, monkeypatch):
    app = MaliphorsInatorApp()
    monkeypatch.setattr('tkinter.messagebox.showinfo', lambda *a, **k: None)
    try:
        app.root.update()
        assert app.root.title() == 'maliphors-inator'
        # All action buttons must fit inside the main window.
        def check_buttons(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Button):
                    assert child.winfo_rootx() + child.winfo_width() <= app.root.winfo_rootx() + app.root.winfo_width()
                    assert child.winfo_rooty() + child.winfo_height() <= app.root.winfo_rooty() + app.root.winfo_height()
                check_buttons(child)
        check_buttons(app.root)
        app.generate_malaphor()
        assert app.generator.history[-1]['malaphor'] in app.sentence_label.cget('text')
        app.add_to_favorites()
        for method, stem, key in [(app.export_originals_dialog, 'originals', 'proverbs'),
                                  (app.export_generated_dialog, 'generated', 'history'),
                                  (app.export_favorites_dialog, 'favorites-export', 'favorites')]:
            for suffix in ('json', 'txt'):
                filename = f'{stem}.{suffix}'
                monkeypatch.setattr('tkinter.filedialog.asksaveasfilename', lambda **kw: filename)
                method()
                content = Path(filename).read_text()
                assert content
                if suffix == 'json':
                    assert json.loads(content)[key]
        assert app.generator.search('sentinel') == []
        incoming = {'original': 'Release sentinel phrase', 'beginning': 'Release', 'ending': 'sentinel phrase'}
        Path('incoming.json').write_text(json.dumps({'proverbs': [incoming, incoming]}))
        monkeypatch.setattr('tkinter.filedialog.askopenfilename', lambda **kw: 'incoming.json')
        app.import_malaphors_dialog()
        assert app.generator.search('sentinel') == [incoming]
        # Exercise the actual event loop and its final save/cleanup.
        app.root.after(20, app.root.quit)
        app.run()
        assert not app.generator._auto_save_thread.is_alive()
        restored = MalaphorGenerator()
        assert restored.favorites == app.generator.favorites
        assert restored.history[0]['malaphor'] == app.generator.history[0]['malaphor']
    finally:
        app.close()
        app.root.destroy()


def test_main_desktop_entrypoint(phrase_library):
    # Run main.py itself and close its real Tk window after startup.
    script = '''
import runpy
import tkinter as tk
original = tk.Tk.mainloop
def smoke_loop(root, *args, **kwargs):
    root.after(100, root.quit)
    return original(root, *args, **kwargs)
tk.Tk.mainloop = smoke_loop
runpy.run_path(%r, run_name="__main__")
''' % str(REPO / 'main.py')
    env = dict(os.environ, PYTHONPATH=str(REPO))
    result = subprocess.run([sys.executable, '-c', script], env=env,
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert 'Traceback' not in result.stderr
