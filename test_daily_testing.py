"""Failure and cancellation checks for the pre-alpha daily workflow."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import shutil
import threading

import pytest

from maliphors_inator_logic import MalaphorGenerator
from maliphors_inator_ui import MaliphorsInatorApp


@pytest.fixture
def generator():
    shutil.copyfile(Path(__file__).parent / 'malaphors.json', 'malaphors.json')
    return MalaphorGenerator()


@pytest.mark.parametrize('payload', [None, [], {}, {'proverbs': None}, {'proverbs': {}},
    {'proverbs': [None]}, {'proverbs': [{'original': 'Broken'}]},
    {'proverbs': [{'original': 'Broken', 'beginning': 12, 'ending': 'end'}]},
    {'proverbs': [{'original': 'Broken', 'beginning': ' ', 'ending': 'end'}]},
    {'proverbs': [{'original': 'Broken', 'beginning': 'start', 'ending': 'end', 'tags': 'bad'}]}])
def test_malformed_import_preserves_library(generator, payload):
    before = deepcopy(generator.proverbs)
    saved = Path('malaphors.json').read_bytes()
    Path('incoming.json').write_text(json.dumps(payload))
    assert asyncio.run(generator.import_malaphors('incoming.json')) is False
    assert generator.proverbs == before
    assert Path('malaphors.json').read_bytes() == saved


def test_failed_import_save_preserves_memory_and_search(generator, monkeypatch):
    before = deepcopy(generator.proverbs)
    saved = Path('malaphors.json').read_bytes()
    assert generator.search('daily-sentinel') == []
    phrase = {'original': 'daily-sentinel phrase', 'beginning': 'daily-sentinel', 'ending': 'phrase'}
    Path('incoming.json').write_text(json.dumps({'proverbs': [phrase]}))
    async def denied(*args):
        return False
    monkeypatch.setattr(generator, '_save_to_file', denied)
    assert asyncio.run(generator.import_malaphors('incoming.json')) is False
    assert generator.proverbs == before
    assert generator.search('daily-sentinel') == []
    assert Path('malaphors.json').read_bytes() == saved


@pytest.mark.parametrize('method', ['export_malaphors', 'export_history', 'export_favorites',
    'export_malaphors_as_text', 'export_history_as_text', 'export_favorites_as_text'])
def test_export_to_directory_reports_failure(generator, method):
    Path('destination').mkdir()
    assert asyncio.run(getattr(generator, method)('destination')) is False


def test_batch_cancel_after_first_result(generator, monkeypatch):
    event = threading.Event()
    original = generator.generate_malaphor
    def generate(**kwargs):
        result = original(**kwargs)
        event.set()
        return result
    monkeypatch.setattr(generator, 'generate_malaphor', generate)
    result = asyncio.run(generator.generate_batch_async(count=10, cancel_event=event))
    assert len(result) == len(generator.history) == 1
    assert len(MalaphorGenerator().history) == 1


@pytest.fixture
def desktop(generator, monkeypatch):
    app = MaliphorsInatorApp()
    messages = []
    for name in ('showinfo', 'showerror', 'showwarning'):
        monkeypatch.setattr(f'tkinter.messagebox.{name}',
                            lambda *args, _name=name, **kwargs: messages.append((_name, args)))
    app.test_messages = messages
    yield app
    app.close()
    app.root.destroy()


@pytest.mark.gui
def test_cancel_file_dialogs_leave_state_unchanged(desktop, monkeypatch):
    before = {p.name: p.read_bytes() for p in Path('.').glob('*.json')}
    monkeypatch.setattr('tkinter.filedialog.askopenfilename', lambda **kw: '')
    monkeypatch.setattr('tkinter.filedialog.asksaveasfilename', lambda **kw: '')
    for name in ('import_malaphors_dialog', 'export_originals_dialog',
                 'export_generated_dialog', 'export_favorites_dialog'):
        getattr(desktop, name)()
    assert not desktop.test_messages
    assert {p.name: p.read_bytes() for p in Path('.').glob('*.json')} == before


@pytest.mark.gui
def test_bad_import_shows_error(desktop, monkeypatch):
    Path('broken.json').write_text('{bad json')
    monkeypatch.setattr('tkinter.filedialog.askopenfilename', lambda **kw: 'broken.json')
    desktop.import_malaphors_dialog()
    assert desktop.test_messages[-1][0] == 'showerror'


@pytest.mark.gui
@pytest.mark.parametrize('method', ['export_originals_dialog', 'export_generated_dialog', 'export_favorites_dialog'])
def test_failed_export_shows_error(desktop, monkeypatch, method):
    Path('blocked.json').mkdir()
    monkeypatch.setattr('tkinter.filedialog.asksaveasfilename', lambda **kw: 'blocked.json')
    getattr(desktop, method)()
    assert desktop.test_messages[-1][0] == 'showerror'


@pytest.mark.gui
def test_unavailable_language_shows_error_and_preserves_display(desktop):
    old_text = desktop.sentence_label.cget('text')
    desktop.language_var.set('missing-language')
    desktop.generate_malaphor()
    assert desktop.test_messages[-1][0] == 'showerror'
    assert desktop.sentence_label.cget('text') == old_text
    assert not desktop.generator.history


@pytest.mark.asyncio
async def test_async_batch_observes_scheduled_cancellation(generator, monkeypatch):
    event = asyncio.Event()
    original = generator.generate_malaphor
    def generate(**kwargs):
        result = original(**kwargs)
        asyncio.get_running_loop().call_soon(event.set)
        return result
    monkeypatch.setattr(generator, 'generate_malaphor', generate)
    results = await generator.generate_batch_async(count=10, cancel_event=event)
    assert len(results) == len(generator.history) == 1


def widgets(parent):
    for child in parent.winfo_children():
        yield child
        yield from widgets(child)


@pytest.mark.gui
def test_filtered_favorite_delete_and_cancel(desktop, monkeypatch):
    import tkinter as tk
    desktop.generator.favorites = ['Keep this favorite', 'Delete sentinel favorite']
    desktop.generator.save_favorites()
    dialog = desktop.show_favorites_dialog()
    try:
        entry = next(w for w in widgets(dialog) if isinstance(w, tk.Entry))
        listing = next(w for w in widgets(dialog) if isinstance(w, tk.Listbox))
        delete = next(w for w in widgets(dialog) if isinstance(w, tk.Button) and w.cget('text') == 'Delete Selected')
        assert any(isinstance(w, tk.Button) and w.cget('text') == 'Export Favorites' for w in widgets(dialog))
        entry.insert(0, 'sentinel')
        listing.selection_set(0)
        monkeypatch.setattr('tkinter.messagebox.askyesno', lambda *a, **kw: False)
        delete.invoke()
        assert len(desktop.generator.favorites) == 2
        monkeypatch.setattr('tkinter.messagebox.askyesno', lambda *a, **kw: True)
        delete.invoke()
        assert desktop.generator.favorites == ['Keep this favorite']
        assert MalaphorGenerator().favorites == ['Keep this favorite']
    finally:
        dialog.destroy()


def test_cli_generation_failure_is_readable(generator, capsys):
    import maliphors_inator_cli
    assert maliphors_inator_cli.main(['--generate', '--language', 'missing']) == 1
    captured = capsys.readouterr()
    assert 'Not enough proverbs' in captured.err
    assert 'Traceback' not in captured.err


@pytest.mark.parametrize('method', ['export_malaphors', 'export_history', 'export_favorites',
    'export_malaphors_as_text', 'export_history_as_text', 'export_favorites_as_text'])
def test_readonly_export_preserves_existing_file(generator, method):
    import os
    if os.name == 'nt' or (hasattr(os, 'geteuid') and os.geteuid() == 0):
        pytest.skip('Requires POSIX file permissions under a non-root user')
    path = Path('readonly-export')
    path.write_text('existing contents')
    path.chmod(0o444)
    try:
        assert asyncio.run(getattr(generator, method)(str(path))) is False
        assert path.read_text() == 'existing contents'
    finally:
        path.chmod(0o600)


def test_readonly_import_library_preserves_state(generator):
    import os
    if os.name == 'nt' or (hasattr(os, 'geteuid') and os.geteuid() == 0):
        pytest.skip('Requires POSIX file permissions under a non-root user')
    path = Path('malaphors.json')
    saved = path.read_bytes()
    before = deepcopy(generator.proverbs)
    Path('incoming.json').write_text(json.dumps({'proverbs': [
        {'original': 'Unwritable sentinel', 'beginning': 'Unwritable', 'ending': 'sentinel'}]}))
    path.chmod(0o444)
    try:
        assert asyncio.run(generator.import_malaphors('incoming.json')) is False
        assert generator.proverbs == before
        assert path.read_bytes() == saved
    finally:
        path.chmod(0o600)


@pytest.mark.gui
def test_favorite_save_failure_is_not_reported_as_success(desktop, monkeypatch):
    desktop.sentence_label.config(text='Unsaved favorite')
    monkeypatch.setattr(desktop.generator, '_save_favorites_sync', lambda: False)
    desktop.add_to_favorites()
    assert desktop.test_messages[-1][0] == 'showerror'
    assert 'Unsaved favorite' not in desktop.generator.favorites


@pytest.mark.gui
def test_history_save_failure_is_reported(desktop, monkeypatch):
    monkeypatch.setattr(desktop.generator, '_save_history_entry', lambda entry=None: False)
    desktop.generate_malaphor()
    assert desktop.test_messages[-1][0] == 'showerror'


@pytest.mark.parametrize('count', [1, 3])
def test_cli_history_write_failure_exits_nonzero(generator, capsys, count):
    import maliphors_inator_cli
    Path('history.json').mkdir()
    assert maliphors_inator_cli.main(['--generate', '--count', str(count)]) == 1
    assert 'Could not save history.json' in capsys.readouterr().err


@pytest.mark.asyncio
async def test_cancelled_async_task_does_not_generate(generator):
    task = asyncio.create_task(generator.generate_batch_async(count=10))
    asyncio.get_running_loop().call_soon(task.cancel)
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not generator.history
    assert not Path('history.json').exists()
