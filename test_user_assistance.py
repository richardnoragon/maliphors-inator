"""Offline assistance behavior using real Tk controls and disposable files."""
import json
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk

import pytest

from maliphors_inator_ui import MaliphorsInatorApp
from user_assistance import TOPICS, context_topic, search_topics


def children(widget):
    for child in widget.winfo_children():
        yield child
        yield from children(child)


def button(window, text):
    return next(w for w in children(window)
                if isinstance(w, (tk.Button, ttk.Button)) and w.cget('text') == text)


@pytest.fixture
def app(monkeypatch):
    Path('malaphors.json').write_text(json.dumps({'proverbs': [
        {'original': 'A stitch in time saves nine', 'beginning': 'A stitch in time', 'ending': 'saves nine'},
        {'original': 'The early bird catches the worm', 'beginning': 'The early bird', 'ending': 'catches the worm'}]}))
    monkeypatch.setattr('tkinter.messagebox.showinfo', lambda *a, **k: None)
    application = MaliphorsInatorApp()
    application.root.update()
    yield application
    application.close()
    application.root.destroy()


def test_help_search_and_related_topics():
    assert 'import' in search_topics('IMPORT JSON')
    assert 'backup' in search_topics('restore')
    assert 'import' in search_topics('add phrase')
    assert not search_topics('notawordzzzz')
    for _, _, _, related in TOPICS.values():
        assert all(key in TOPICS for key in related)
    assert context_topic('Manage History') == 'search'
    assert context_topic('Manage Favorites') == 'generate'
    assert context_topic('Add New Proverb') == 'import'


@pytest.mark.gui
def test_welcome_persists_completion_and_preserves_preferences(app):
    app.preferences['custom_setting'] = 'keep'
    welcome = app.assistance.welcome()
    button(welcome, 'Done / Skip for now').invoke()
    saved = json.loads(Path('ui_preferences.json').read_text())
    assert saved['onboarding_complete'] is True
    assert saved['custom_setting'] == 'keep'
    app.theme_mode = 'dark'
    app._save_ui_preferences()
    assert json.loads(Path('ui_preferences.json').read_text())['onboarding_complete'] is True
    assert not welcome.winfo_exists()


@pytest.mark.gui
def test_failed_onboarding_save_is_retryable(app, monkeypatch):
    errors = []
    monkeypatch.setattr('tkinter.messagebox.showerror', lambda *a, **k: errors.append(a))
    monkeypatch.setattr(app, '_save_ui_preferences', lambda: False)
    welcome = app.assistance.welcome()
    button(welcome, 'Done / Skip for now').invoke()
    assert welcome.winfo_exists()
    assert not app.preferences.get('onboarding_complete')
    assert errors


@pytest.mark.gui
def test_guided_first_result_validates_real_saved_changes(app):
    guide = app.assistance.guided_task('first')
    button(guide, 'Validate / Next').invoke()
    assert not app.generator.history
    button(guide, 'Perform Step').invoke()
    assert app.generator.history
    button(guide, 'Validate / Next').invoke()
    button(guide, 'Perform Step').invoke()
    assert app.generator.favorites
    assert json.loads(Path('favorites.json').read_text())['favorites']
    button(guide, 'Validate / Next').invoke()
    confirm = next(w for w in children(guide) if isinstance(w, ttk.Checkbutton))
    confirm.invoke()
    button(guide, 'Validate / Next').invoke()
    assert str(button(guide, 'Perform Step').cget('state')) == 'disabled'


@pytest.mark.gui
def test_search_no_results_and_action_palette(app):
    help_window = app.assistance.show_help('import')
    entry = next(w for w in children(help_window) if isinstance(w, ttk.Entry))
    entry.insert(0, 'notawordzzzz')
    body = next(w for w in children(help_window) if isinstance(w, tk.Text))
    assert 'No matching help' in body.get('1.0', 'end')
    entry.delete(0, 'end')
    entry.insert(0, 'restore')
    assert 'Backups and Recovery' in body.get('1.0', 'end')
    palette = app.assistance.palette()
    entry = next(w for w in children(palette) if isinstance(w, ttk.Entry))
    entry.insert(0, 'generate')
    button(palette, 'Run Selected').invoke()
    assert app.generator.history
    assert not palette.winfo_exists()


@pytest.mark.gui
def test_tour_highlights_real_controls_and_cleans_up(app):
    tour = app.assistance.tour()
    app.root.update()
    assert len(app.assistance.overlays) >= 2
    assert str(button(tour, 'Back').cget('state')) == 'disabled'
    app.root.geometry('1000x800')
    app.root.update()
    for _ in range(6):
        button(tour, 'Next').invoke()
    button(tour, 'Finish').invoke()
    assert not tour.winfo_exists()
    assert not app.assistance.overlays
    tour = app.assistance.tour()
    button(tour, 'Cancel').invoke()
    assert not app.assistance.overlays


@pytest.mark.gui
def test_context_help_and_diagnostics_do_not_change_data(app):
    before = Path('malaphors.json').read_bytes()
    dialog = app.show_favorites_dialog()
    dialog.update()
    # A real F1 event must reach the dialog bindtag, including from its entry.
    entry = next(w for w in children(dialog) if isinstance(w, tk.Entry))
    entry.focus_force()
    entry.event_generate('<F1>')
    app.root.update()
    help_window = app.assistance.windows[-1]
    assert 'Search Help' in help_window.title()
    assert any('Generate and Save a Favorite' in w.get('1.0', 'end')
               for w in children(help_window) if isinstance(w, tk.Text))
    diagnostic = app.assistance.troubleshoot()
    assert any(str(Path.cwd()) in w.get('1.0', 'end') for w in children(diagnostic) if isinstance(w, tk.Text))
    assert Path('malaphors.json').read_bytes() == before
    dialog.destroy()


@pytest.mark.gui
@pytest.mark.skipif(sys.platform != 'linux', reason='inspect child cwd through procfs')
def test_demo_isolated_and_removed_on_close(app):
    before = Path('malaphors.json').read_bytes()
    process = app.assistance.demo()
    directory = Path(app.assistance.demo_directory.name)
    assert Path(f'/proc/{process.pid}/cwd').resolve() == directory
    assert directory != Path.cwd()
    assert len(json.loads((directory / 'malaphors.json').read_text())['proverbs']) == 2
    assert app.assistance.demo() is process
    app.assistance.close()
    assert process.poll() is not None
    assert not directory.exists()
    assert Path('malaphors.json').read_bytes() == before


@pytest.mark.gui
def test_first_run_opens_onboarding_and_completion_suppresses_it(app):
    observed = []
    def inspect():
        observed.append(any('Getting Started' in win.title() for win in app.assistance.windows))
        app.root.quit()
    app.root.after(180, inspect)
    app.run()
    assert observed == [True]
    app.preferences['onboarding_complete'] = True
    app.root.after(180, inspect)
    app.run()
    assert observed == [True, False]


@pytest.mark.gui
def test_help_controls_fit_and_all_related_buttons_are_visible(app):
    for window in (app.assistance.show_help(), app.assistance.welcome(),
                   app.assistance.user_guide(), app.assistance.guided_task('first')):
        window.update()
        for widget in children(window):
            if isinstance(widget, (tk.Button, ttk.Button)):
                assert widget.winfo_ismapped()
                assert widget.winfo_rooty() + widget.winfo_height() <= window.winfo_rooty() + window.winfo_height()
                assert widget.winfo_rootx() + widget.winfo_width() <= window.winfo_rootx() + window.winfo_width()


@pytest.mark.gui
def test_cancelled_import_does_not_complete_guided_step(app, monkeypatch):
    guide = app.assistance.guided_task('import')
    confirm = next(w for w in children(guide) if isinstance(w, ttk.Checkbutton))
    confirm.invoke()
    button(guide, 'Validate / Next').invoke()
    before = Path('malaphors.json').read_bytes()
    monkeypatch.setattr('tkinter.filedialog.askopenfilename', lambda **kwargs: '')
    button(guide, 'Perform Step').invoke()
    button(guide, 'Validate / Next').invoke()
    assert Path('malaphors.json').read_bytes() == before
    assert any('2 / 3 — Import' in str(w.cget('text')) for w in children(guide) if isinstance(w, ttk.Label))
