"""Storage, migration, restore, import, feedback and responsive UI contracts."""
import asyncio
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import zipfile

import pytest

from app_storage import (StoreSession, resolve_data_dir, initialize_data, create_backup,
                         preview_restore, restore_backup)
from library_workflows import (preview_import, import_additions, classify_rows,
                               plan_cleanup, OperationCancelled)
from maliphors_inator_logic import MalaphorGenerator
from maliphors_inator_ui import MaliphorsInatorApp

REPO = Path(__file__).resolve().parent


def phrases():
    return [{'original': f'Phrase {i}', 'beginning': f'Beginning {i}', 'ending': f'ending {i}', 'language': 'en', 'tags': ['test']} for i in range(4)]


@pytest.fixture
def generator(tmp_path):
    directory = tmp_path / 'data'
    directory.mkdir()
    (directory / 'malaphors.json').write_text(json.dumps({'proverbs': phrases()}))
    return MalaphorGenerator(data_dir=directory)


def test_default_migration_copies_once_and_keeps_source(tmp_path, monkeypatch):
    source = tmp_path / 'legacy'
    source.mkdir()
    (source / 'malaphors.json').write_text(json.dumps({'proverbs': phrases()}))
    (source / 'favorites.json').write_text('{"favorites":["keep"]}')
    before = (source / 'favorites.json').read_bytes()
    monkeypatch.delenv('MALIPHORS_INATOR_DATA_DIR')
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'xdg'))
    monkeypatch.chdir(source)
    target = resolve_data_dir()
    initialize_data(target, migrate=True)
    assert (target / 'favorites.json').read_bytes() == before
    assert json.loads((target / 'migration.json').read_text())['source'] == str(source)
    (source / 'favorites.json').write_text('{"favorites":[]}')
    initialize_data(target, migrate=True)
    assert (target / 'favorites.json').read_bytes() == before


def test_data_directory_survives_working_directory_change(generator, tmp_path, monkeypatch):
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    generator.generate_malaphor()
    asyncio.run(generator.add_new_proverb('Fixed directory', 'survives'))
    assert not (elsewhere / 'history.json').exists()
    restored = MalaphorGenerator(data_dir=generator.data_dir)
    assert len(restored.history) == 1
    assert len(restored.proverbs) == 5


def test_single_writer_lock_released_after_session(tmp_path):
    with StoreSession(tmp_path):
        with pytest.raises(OSError, match='another session'):
            with StoreSession(tmp_path):
                pass
    with StoreSession(tmp_path):
        pass


def test_backups_restore_reload_and_keep_safety_snapshot(generator):
    generator.generate_malaphor()
    generator.add_to_favorites('Kept favorite')
    archive = create_backup(generator.data_dir)
    assert {'malaphors.json', 'history.json', 'favorites.json'} <= preview_restore(archive).keys()
    before = json.loads(generator.data_path('malaphors.json').read_text())
    generator.data_path('malaphors.json').write_text('{damaged')
    report = restore_backup(generator.data_dir, archive)
    assert Path(report['safety_backup']).exists()
    assert json.loads(generator.data_path('malaphors.json').read_text()) == before
    assert MalaphorGenerator(data_dir=generator.data_dir).favorites == ['Kept favorite']


@pytest.mark.parametrize('entry', ['../escape.json', 'unknown.json', '/tmp/escape.json'])
def test_restore_rejects_unexpected_paths(tmp_path, entry):
    path = tmp_path / 'unsafe.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr(entry, '{}')
    with pytest.raises(ValueError, match='paths'):
        preview_restore(path)


def test_restore_rejects_changed_preview_and_checksum(generator):
    archive = create_backup(generator.data_dir)
    with pytest.raises(ValueError, match='changed'):
        restore_backup(generator.data_dir, archive, expected_digest='wrong')
    corrupt = generator.data_dir / 'corrupt.zip'
    with zipfile.ZipFile(archive) as old, zipfile.ZipFile(corrupt, 'w') as new:
        for name in old.namelist():
            new.writestr(name, b'{"proverbs":[]}' if name == 'malaphors.json' else old.read(name))
    with pytest.raises(ValueError, match='checksum'):
        preview_restore(corrupt)


def test_restore_rolls_back_bytes_on_second_write_failure(generator, monkeypatch):
    import maliphors_inator_logic as core
    generator.add_to_favorites('original')
    archive = create_backup(generator.data_dir)
    generator.data_path('malaphors.json').write_bytes(b'{malformed original')
    before = {name: (generator.data_dir / name).read_bytes() for name in preview_restore(archive)}
    original = core.atomic_write_json
    calls = [0]
    def fail(path, value):
        calls[0] += 1
        # First call makes the safety backup manifest? ZIP creation uses no JSON writer.
        if calls[0] == 2:
            raise OSError('replacement failed')
        return original(path, value)
    monkeypatch.setattr(core, 'atomic_write_json', fail)
    with pytest.raises(OSError, match='replacement failed'):
        restore_backup(generator.data_dir, archive)
    assert all((generator.data_dir / name).read_bytes() == content for name, content in before.items())


def test_startup_backup_retention(generator):
    for _ in range(18):
        create_backup(generator.data_dir, reason='startup')
    assert len(list((generator.data_dir / 'backups').glob('*-startup.zip'))) == 14


def test_import_preview_correction_exclusion_and_revalidation(generator, tmp_path):
    new = {'original': 'New phrase', 'beginning': 'New', 'ending': 'phrase'}
    path = tmp_path / 'incoming.json'
    path.write_text(json.dumps({'proverbs': [phrases()[0], new, {'original': 'Broken'}]}))
    before = generator.data_path('malaphors.json').read_bytes()
    rows = preview_import(path, generator.proverbs)
    assert [row['status'] for row in rows] == ['duplicate', 'new', 'invalid']
    with pytest.raises(ValueError, match='Correct it'):
        generator.commit_import_rows(rows)
    assert generator.data_path('malaphors.json').read_bytes() == before
    rows[2]['phrase'] = {'original': 'Corrected', 'beginning': 'Corrected', 'ending': 'phrase'}
    assert generator.commit_import_rows(rows) == 2
    assert generator.commit_import_rows(rows) == 0
    assert generator.search('Corrected')
    assert list((generator.data_dir / 'backups').glob('*-before-import.zip'))


def test_import_excluded_invalid_row_is_not_written(generator):
    rows = [{'id': 0, 'phrase': None, 'include': False}, {'id': 1, 'phrase': {'original':'Unique', 'beginning':'Uni','ending':'que'}, 'include':True}]
    assert generator.commit_import_rows(rows) == 1
    assert len(generator.proverbs) == 5


@pytest.mark.parametrize('operation', ['import', 'cleanup'])
def test_cancelled_plans_and_commits_leave_data_unchanged(generator, operation):
    event = threading.Event()
    event.set()
    before = generator.data_path('malaphors.json').read_bytes()
    with pytest.raises(OperationCancelled):
        if operation == 'import':
            generator.commit_import_rows([], cancel=event)
        else:
            plan_cleanup(generator.proverbs, cancel=event)
    assert generator.data_path('malaphors.json').read_bytes() == before


def test_cleanup_commits_once_and_rejects_stale_plan(generator):
    generator.proverbs.append(deepcopy(generator.proverbs[0]))
    original = deepcopy(generator.proverbs)
    plan = plan_cleanup(original)
    assert len(plan['removed']) == 1
    assert generator.commit_cleanup(plan, original) == 1
    assert len(MalaphorGenerator(data_dir=generator.data_dir).proverbs) == 4
    with pytest.raises(ValueError, match='changed'):
        generator.commit_cleanup(plan, original)


def test_failed_import_save_keeps_memory_and_search(generator, monkeypatch):
    before = deepcopy(generator.proverbs)
    monkeypatch.setattr(generator, '_write_json', lambda *a: False)
    rows = [{'id':0, 'phrase':{'original':'Must not appear','beginning':'Must','ending':'not appear'}}]
    with pytest.raises(OSError):
        generator.commit_import_rows(rows)
    assert generator.proverbs == before
    assert not generator.search('Must not appear')


def test_feedback_is_persistent_and_random_generation_avoids_blocked(generator):
    result = generator.generate_malaphor()
    assert generator.rate_malaphor(result['source1'], result['source2'], 5)
    assert generator.avoid_combination(result['source1'], result['source2'])
    reloaded = MalaphorGenerator(data_dir=generator.data_dir)
    for _ in range(15):
        next_result = reloaded.generate_malaphor()
        assert (next_result['source1'], next_result['source2']) != (result['source1'], result['source2'])
    assert reloaded.avoid_combination(result['source1'], result['source2'], avoid=False)
    assert reloaded.get_pair_rating(result['source1'], result['source2']) == 5


def test_more_like_shares_source_and_suppresses_recent_outputs(generator):
    first = generator.generate_malaphor()
    second = generator.generate_more_like(first)
    assert {first['source1'], first['source2']} & {second['source1'], second['source2']}
    assert first['malaphor'] != second['malaphor']
    outputs = {first['malaphor'], second['malaphor']}
    for _ in range(8):
        item = generator.generate_malaphor()
        assert item['malaphor'] not in outputs
        outputs.add(item['malaphor'])


def test_failed_feedback_save_preserves_preferences(generator, monkeypatch):
    monkeypatch.setattr(generator, '_write_json', lambda *args: False)
    assert generator.avoid_combination('A', 'B') is False
    assert generator.rate_malaphor('A','B',5) is False
    assert generator.generation_preferences['blocked'] == []
    assert generator.phrase_pair_ratings == {}


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


@pytest.mark.gui
def test_four_views_and_worker_keeps_event_loop_responsive(generator, monkeypatch):
    app = MaliphorsInatorApp(data_dir=generator.data_dir)
    messages = []
    monkeypatch.setattr('tkinter.messagebox.showinfo', lambda *a, **k: messages.append(a))
    try:
        assert [app.notebook.tab(tab, 'text') for tab in app.notebook.tabs()] == ['Generate','Library','Favorites','History']
        app.root.update()
        assert app.data_location.winfo_ismapped()
        assert app.empty_state.winfo_ismapped()
        assert app.empty_state.winfo_rooty() + app.empty_state.winfo_height() <= app.root.winfo_rooty() + app.root.winfo_height()
        assert app.data_location.winfo_rooty() + app.data_location.winfo_height() <= app.root.winfo_rooty() + app.root.winfo_height()
        beats = []
        done = []
        def work(cancel, progress):
            for n in range(20):
                if cancel.is_set():
                    return n
                time.sleep(.01)
                progress(n,20)
            return 20
        app.workflows.start('Test work', work, done.append)
        app.root.after(20, lambda: beats.append('responsive'))
        limit = time.monotonic()+3
        while not done and time.monotonic() < limit:
            app.root.update()
            time.sleep(.01)
        assert beats == ['responsive']
        assert done == [20]
        app.focus_search_box()
        assert app.notebook.tab(app.notebook.select(), 'text') == 'Library'
    finally:
        app.close()
        app.root.destroy()


@pytest.mark.gui
def test_import_review_corrects_and_applies_real_rows(generator, monkeypatch):
    messages = []
    monkeypatch.setattr('tkinter.messagebox.showinfo', lambda *a, **k: messages.append(a))
    app = MaliphorsInatorApp(data_dir=generator.data_dir)
    try:
        rows = [{'id':0,'phrase':{'original':'Incomplete'},'include':True}]
        review = app.workflows.import_review(rows)
        tree = next(w for w in descendants(review) if isinstance(w, ttk.Treeview))
        tree.selection_set('0')
        tree.event_generate('<<TreeviewSelect>>')
        app.root.update()
        editor = next(w for w in descendants(review) if isinstance(w, tk.Text))
        editor.delete('1.0','end')
        editor.insert('1.0', '{"original":"Corrected row","beginning":"Corrected","ending":"row"}')
        def click(text):
            next(w for w in descendants(review) if isinstance(w, ttk.Button) and w.cget('text') == text).invoke()
        click('Save Row Correction')
        assert tree.item('0')['values'][0] == 'new'
        click('Apply Reviewed Import')
        limit = time.monotonic()+3
        while not messages and time.monotonic() < limit:
            app.root.update()
            time.sleep(.01)
        assert app.generator.search('Corrected row')
        assert len(MalaphorGenerator(data_dir=generator.data_dir).proverbs) == 5
    finally:
        app.close()
        app.root.destroy()


def test_cli_backup_preview_restore_and_directory_override(generator, tmp_path):
    def cli(*args, expected=0):
        result = subprocess.run([sys.executable, str(REPO / 'maliphors_inator_cli.py'),
                                 '--data-dir', str(generator.data_dir), *args],
                                capture_output=True, text=True, timeout=20)
        assert result.returncode == expected, result.stderr
        assert 'Traceback' not in result.stderr
        return result
    assert cli('--data-path').stdout.strip() == str(generator.data_dir)
    cli('--generate')
    archive = tmp_path / 'saved.zip'
    cli('--backup', str(archive))
    assert 'history.json' in json.loads(cli('--restore-preview', str(archive)).stdout)
    generator.data_path('history.json').write_text('[]')
    cli('--restore', str(archive), expected=1)
    cli('--restore', str(archive), '--confirm-restore')
    assert len(MalaphorGenerator(data_dir=generator.data_dir).history) == 1
    damaged = tmp_path / 'bad.zip'
    damaged.write_bytes(b'not a zip')
    cli('--restore-preview', str(damaged), expected=1)


def test_migration_failure_removes_partial_destination_and_keeps_source(tmp_path, monkeypatch):
    import maliphors_inator_logic as core
    source = tmp_path / 'legacy'
    source.mkdir()
    (source / 'malaphors.json').write_text(json.dumps({'proverbs': phrases()}))
    monkeypatch.chdir(source)
    monkeypatch.setenv('XDG_DATA_HOME', str(tmp_path / 'xdg'))
    monkeypatch.setattr(core, 'atomic_write_json', lambda *args: (_ for _ in ()).throw(OSError('marker denied')))
    target = tmp_path / 'destination'
    with pytest.raises(OSError, match='marker denied'):
        initialize_data(target, migrate=True)
    assert not (target / 'malaphors.json').exists()
    assert (source / 'malaphors.json').exists()


def test_delete_and_undo_use_explicit_data_directory(generator, tmp_path, monkeypatch):
    generator.generate_malaphor()
    generator.add_to_favorites('Keep or undo')
    elsewhere = tmp_path / 'elsewhere'
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert generator.delete_from_favorites(0)
    assert MalaphorGenerator(data_dir=generator.data_dir).favorites == []
    assert generator.undo_last_action()
    assert MalaphorGenerator(data_dir=generator.data_dir).favorites == ['Keep or undo']
    assert not (elsewhere / 'favorites.json').exists()
