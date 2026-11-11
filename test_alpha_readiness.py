"""Data-integrity and recovery checks for the alpha handoff scope."""
import asyncio
from copy import deepcopy
import json
from pathlib import Path
import shutil
import threading

import pytest

from maliphors_inator_logic import MalaphorGenerator, atomic_write_json

REPO = Path(__file__).resolve().parent


@pytest.fixture
def generator():
    shutil.copyfile(REPO / 'malaphors.json', 'malaphors.json')
    return MalaphorGenerator()


@pytest.mark.parametrize('failure', ['serialize', 'fsync', 'replace'])
def test_interrupted_write_preserves_existing_json(monkeypatch, failure):
    path = Path('state.json')
    path.write_text('{"saved": true}')
    original = path.read_bytes()
    def fail(*args):
        raise OSError('simulated disk failure')
    if failure != 'serialize':
        monkeypatch.setattr(f'maliphors_inator_logic.os.{failure}', fail)
    with pytest.raises((TypeError, OSError)):
        atomic_write_json(path, {'new': object() if failure == 'serialize' else True})
    assert path.read_bytes() == original
    assert not list(Path('.').glob('.state.json.*.tmp'))


@pytest.mark.parametrize('method,args', [
    ('add_new_proverb', ('New sentinel', 'ending')),
    ('edit_proverb', (0, 'Changed sentinel', 'ending')),
    ('delete_proverb', (0,)),
])
def test_failed_phrase_change_preserves_disk_memory_and_search(generator, monkeypatch, method, args):
    before = deepcopy(generator.proverbs)
    disk = Path('malaphors.json').read_bytes()
    cached = generator.search(before[0]['original'])
    async def denied(*args):
        return False
    monkeypatch.setattr(generator, '_save_to_file', denied)
    assert asyncio.run(getattr(generator, method)(*args)) is False
    assert generator.proverbs == before
    assert generator.search(before[0]['original']) == cached
    assert not generator.search('sentinel')
    assert Path('malaphors.json').read_bytes() == disk
    assert not generator.undo_stack.can_undo()


def test_edit_preserves_metadata_and_refreshes_search(generator):
    generator.proverbs[0].update(language='en', tags=['test'], source='alpha fixture')
    assert asyncio.run(generator.edit_proverb(0, 'Alpha sentinel', 'ending'))
    result = generator.search('sentinel')[0]
    assert result['tags'] == ['test']
    assert result['source'] == 'alpha fixture'
    assert MalaphorGenerator().search('sentinel') == [result]


@pytest.mark.parametrize('collection', ['history', 'favorites'])
def test_failed_delete_keeps_saved_entry(generator, monkeypatch, collection):
    generator.generate_malaphor()
    generator.add_to_favorites('Saved favorite')
    before = deepcopy(getattr(generator, collection))
    disk = Path(f'{collection}.json').read_bytes()
    monkeypatch.setattr(generator, '_write_json', lambda *args: False)
    assert getattr(generator, f'delete_from_{collection}')(0) is False
    assert getattr(generator, collection) == before
    assert Path(f'{collection}.json').read_bytes() == disk
    assert not generator.undo_stack.can_undo()


@pytest.mark.parametrize('collection', ['proverbs', 'history', 'favorites'])
def test_delete_undo_redo_survives_reload(generator, collection):
    generator.generate_malaphor()
    generator.add_to_favorites('Saved favorite')
    original = deepcopy(getattr(generator, collection))
    if collection == 'proverbs':
        assert asyncio.run(generator.delete_proverb(0))
    else:
        assert getattr(generator, f'delete_from_{collection}')(0)
    deleted = deepcopy(getattr(generator, collection))
    assert len(deleted) == len(original) - 1
    assert generator.undo_last_action()
    assert getattr(MalaphorGenerator(), collection) == original
    assert generator.redo_last_action()
    assert getattr(MalaphorGenerator(), collection) == deleted
    if collection == 'proverbs':
        assert generator.search(original[0]['original']) == generator.search_index.lookup(original[0]['original'])


def test_failed_undo_keeps_stack_and_state(generator, monkeypatch):
    assert generator.add_to_favorites('Saved favorite')
    assert generator.delete_from_favorites(0)
    monkeypatch.setattr(generator, '_write_json', lambda *args: False)
    assert generator.undo_last_action() is False
    assert generator.favorites == []
    assert generator.undo_stack.can_undo()
    assert not generator.undo_stack.can_redo()
    assert MalaphorGenerator().favorites == []


@pytest.mark.parametrize('filename,payload', [
    ('history.json', '{broken'), ('history.json', '{"history": null}'),
    ('history.json', '[{"malaphor": 123}]'), ('history.json', '[{"malaphor":"x","source1":"a","source2":"b","timestamp":123}]'),
    ('ratings.json', 'null'), ('ratings.json', '{"ratings": {"one|two": ["bad"]}}'),
    ('favorites.json', '{broken'), ('favorites.json', '{"favorites": [123]}'),
    ('malaphors.json', '{broken'), ('malaphors.json', '{"proverbs": [null]}'),
    ('malaphors.json', json.dumps({'proverbs': [{'original': 'a b', 'beginning': 'a', 'ending': 'b', 'tags': None}]})),
])
def test_unreadable_data_is_not_overwritten_on_save(filename, payload):
    Path(filename).write_text(payload)
    generator = MalaphorGenerator()
    assert Path(filename).resolve() in generator.load_errors
    generator._run_auto_save()
    assert generator._write_json(filename, {}) is False
    assert Path(filename).read_text() == payload


@pytest.mark.parametrize('method,args', [
    ('generate_malaphor', ()), ('generate_with_category', ()),
    ('generate_with_constraints', ()), ('generate_rhyming_random', ()),
    ('generate_from_template', ('Classic Mix',)),
])
def test_generation_failure_does_not_append_history(generator, monkeypatch, method, args):
    if method == 'generate_from_template':
        args = (generator.get_generation_templates()[0]['name'],)
    monkeypatch.setattr(generator, '_write_json', lambda *args: False)
    with pytest.raises(OSError, match='history.json'):
        getattr(generator, method)(*args)
    assert generator.history == []


@pytest.mark.parametrize('method', ['generate_malaphor', 'generate_with_category'])
def test_duplicate_only_library_returns_error(generator, method):
    generator.proverbs = [generator.proverbs[0]] * 2
    with pytest.raises(ValueError, match='distinct'):
        getattr(generator, method)()


def test_backup_restore_recovers_library_history_and_favorites(generator, tmp_path):
    assert asyncio.run(generator.add_new_proverb('Recovery sentinel', 'survives'))
    generator.generate_malaphor()
    assert generator.add_to_favorites('Recovery favorite')
    names = ['malaphors.json', 'history.json', 'favorites.json']
    backup = tmp_path / 'backup'
    backup.mkdir()
    expected = {name: Path(name).read_bytes() for name in names}
    for name in names:
        shutil.copyfile(name, backup / name)
        Path(name).write_text('{damaged')
    damaged = MalaphorGenerator()
    assert len(damaged.load_errors) == 3
    assert damaged._run_auto_save() is False
    for name in names:
        shutil.copyfile(backup / name, name)
    restored = MalaphorGenerator()
    assert not restored.load_errors
    assert restored.search('Recovery sentinel')
    assert restored.history == generator.history
    assert restored.favorites == generator.favorites
    assert all(Path(name).read_bytes() == expected[name] for name in names)


def test_autosave_and_generation_keep_every_history_entry(generator):
    errors = []
    def autosave():
        try:
            for _ in range(30):
                assert generator._run_auto_save()
        except BaseException as exc:
            errors.append(exc)
    thread = threading.Thread(target=autosave)
    thread.start()
    try:
        for _ in range(30):
            generator.generate_malaphor()
    finally:
        thread.join(timeout=10)
    assert not thread.is_alive()
    assert not errors
    assert len(generator.history) == 30
    assert MalaphorGenerator().history == generator.history


def test_failed_reorder_preserves_library_and_search(generator, monkeypatch):
    before = deepcopy(generator.proverbs)
    monkeypatch.setattr(generator, '_write_json', lambda *args: False)
    assert generator.move_proverb(0, 2) is False
    assert generator.proverbs == before
    assert generator.search_index.phrases == before


@pytest.mark.gui
def test_tooltips_support_buttons_and_listboxes(generator):
    import tkinter as tk
    from maliphors_inator_ui import MaliphorsInatorApp
    app = MaliphorsInatorApp()
    try:
        app.root.update()
        for widget_type in (tk.Button, tk.Listbox):
            widget = widget_type(app.root)
            widget.pack()
            app._create_tooltip(widget, 'Alpha review tooltip')
            _, tooltip, enter, leave = app.tooltips[-1]
            enter(None)
            app.root.update_idletasks()
            assert tooltip.winfo_viewable()
            leave(None)
    finally:
        app.close()
        app.root.destroy()


@pytest.mark.gui
@pytest.mark.parametrize('collection', ['history', 'favorites'])
def test_desktop_reports_failed_deletion(generator, monkeypatch, collection):
    import tkinter as tk
    from maliphors_inator_ui import MaliphorsInatorApp
    from test_daily_testing import widgets
    app = MaliphorsInatorApp()
    messages = []
    monkeypatch.setattr('tkinter.messagebox.askyesno', lambda *a, **k: True)
    monkeypatch.setattr('tkinter.messagebox.showerror', lambda *a, **k: messages.append(a))
    try:
        app.generator.generate_malaphor()
        app.generator.add_to_favorites('Keep this favorite')
        original = deepcopy(getattr(app.generator, collection))
        monkeypatch.setattr(app.generator, '_write_json', lambda *a: False)
        dialog = getattr(app, f'show_{collection}_dialog')()
        listing = next(w for w in widgets(dialog) if isinstance(w, tk.Listbox))
        listing.selection_set(0)
        button = next(w for w in widgets(dialog) if isinstance(w, tk.Button) and w.cget('text') == 'Delete Selected')
        button.invoke()
        assert messages and 'Could not save' in messages[-1][1]
        assert getattr(app.generator, collection) == original
        assert listing.size() == 1
    finally:
        app.close()
        app.root.destroy()
