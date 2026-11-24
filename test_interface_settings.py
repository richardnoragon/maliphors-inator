"""Interface-only settings validation, geometry, fonts, table state and portability."""
from copy import deepcopy
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, font as tkfont
from unittest.mock import Mock

import pytest

from interface_settings import (DEFAULTS, validate_preferences, export_document,
                                parse_document, fitted_geometry, system_theme)
from app_storage import validate_state, create_backup, preview_restore
from maliphors_inator_ui import MaliphorsInatorApp


def descendants(parent):
    for child in parent.winfo_children():
        yield child
        yield from descendants(child)


def button(win, label):
    return next(w for w in descendants(win) if isinstance(w, ttk.Button) and str(w.cget('text')) == label)


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr('tkinter.messagebox.showinfo', lambda *a, **k: None)
    monkeypatch.setattr('tkinter.messagebox.showerror', lambda *a, **k: None)
    application = MaliphorsInatorApp()
    application.root.update()
    yield application
    application.close()
    application.root.destroy()


def test_portable_document_excludes_data_and_onboarding():
    preferences = {**deepcopy(DEFAULTS), 'onboarding_complete':True, 'private_setting':'do not export'}
    document = export_document(preferences)
    assert set(document['settings']) == set(DEFAULTS)
    assert 'onboarding_complete' not in document['settings']
    assert parse_document(document)['interface_language'] == 'en'


@pytest.mark.parametrize('update', [
    {'theme':'blue'}, {'font_size':True}, {'font_size':30}, {'interface_language':'de'},
    {'remember_window_size':'yes'}, {'windows':{'main':'not geometry'}},
    {'tables':{'unknown':{}}}, {'tables':{'import_review':{'visible':[]}}},
    {'tables':{'import_review':{'order':['status']}}},
    {'tables':{'import_review':{'widths':{'phrase':0}}}},
])
def test_reject_invalid_settings(update):
    with pytest.raises(ValueError):
        validate_preferences(update)


def test_import_rejects_other_projects_and_internal_state():
    with pytest.raises(ValueError):
        parse_document({'application':'Coreinator','format':1,'settings':{}})
    with pytest.raises(ValueError):
        parse_document({'application':'maliphors-inator','format':1,'settings':{'onboarding_complete':True}})


def test_fitted_geometry_clamps_offscreen_and_handles_size_only():
    assert fitted_geometry('1200x900+4000-100', 1024, 768) == '1024x768+0+0'
    assert fitted_geometry('800x600+2000+2000',1024,768) == '800x600+224+168'
    assert fitted_geometry('800x600',1024,768) == '800x600'


def test_system_theme_detects_desktop_and_falls_back(monkeypatch):
    monkeypatch.setattr('interface_settings.shutil.which', lambda name:'/usr/bin/gsettings')
    monkeypatch.setattr('interface_settings.subprocess.run', lambda *a, **k: Mock(stdout="'prefer-dark'"))
    assert system_theme() == 'dark'
    monkeypatch.setattr('interface_settings.shutil.which', lambda name:None)
    monkeypatch.setenv('GTK_THEME','Adwaita:dark')
    assert system_theme() == 'dark'
    monkeypatch.delenv('GTK_THEME')
    assert system_theme() == 'light'


@pytest.mark.gui
def test_main_submenu_and_dialog_fonts_share_family_and_size(app):
    app.interface.commit({'font_size':12})
    win = app.assistance.show_help()
    app.root.update()
    base = tkfont.nametofont('TkDefaultFont', root=app.root).actual()
    for name in ('TkMenuFont','TkTextFont','TkHeadingFont','TkSmallCaptionFont'):
        actual = tkfont.nametofont(name, root=app.root).actual()
        assert (actual['family'],actual['size']) == (base['family'],base['size'])
    assert str(app.assistance.tools_menu.cget('font')) == 'TkMenuFont'
    text = next(w for w in descendants(win) if isinstance(w, tk.Text))
    assert str(text.cget('font')) == 'TkTextFont'
    dialog = app.show_manage_phrases_dialog()
    app.root.update()
    for w in descendants(dialog):
        if isinstance(w, (tk.Label,tk.Button,tk.Entry,tk.Listbox)):
            assert str(w.cget('font')) in ('TkDefaultFont','AppHeadingFont')
    dialog.destroy()


@pytest.mark.gui
def test_system_theme_is_saved_and_accepted_by_backup_validation(app, monkeypatch):
    monkeypatch.setattr('interface_settings.system_theme', lambda:'dark')
    app.interface.commit({'theme':'system'})
    assert app.theme_mode == 'system'
    assert app._theme_palette()['bg'] == '#0f172a'
    data = json.loads(Path('ui_preferences.json').read_text())
    validate_state('ui_preferences.json', data)
    archive = create_backup(app.generator.data_dir)
    assert 'ui_preferences.json' in preview_restore(archive)


@pytest.mark.gui
def test_failed_setting_save_leaves_active_preferences_unchanged(app, monkeypatch):
    before = deepcopy(app.preferences)
    monkeypatch.setattr(app.generator, '_write_json', lambda *a:False)
    with pytest.raises(OSError):
        app.interface.commit({'theme':'dark','font_size':14})
    assert app.preferences == before
    assert app.theme_mode == 'light'


@pytest.mark.gui
def test_dialog_geometry_restores_and_can_be_disabled(app, monkeypatch):
    requests = []
    original = tk.Toplevel.geometry
    def record(win, value=None):
        if value is not None:
            requests.append(value)
        return original(win, value)
    monkeypatch.setattr(tk.Toplevel, 'geometry', record)
    app.preferences['windows']['Manage Phrases'] = '820x620+32+44'
    dialog = app.show_manage_phrases_dialog()
    app.root.update()
    expected = fitted_geometry('820x620+32+44', dialog.winfo_screenwidth(), dialog.winfo_screenheight())
    assert expected in requests
    assert (dialog.winfo_width(), dialog.winfo_height()) == (min(820,dialog.winfo_screenwidth()),min(620,dialog.winfo_screenheight()))
    dialog.geometry('850x630+40+60')
    app.root.update()
    remembered = app.preferences['windows']['Manage Phrases']
    dialog.destroy()
    requests.clear()
    reopened = app.show_manage_phrases_dialog()
    app.root.update()
    assert fitted_geometry(remembered, reopened.winfo_screenwidth(), reopened.winfo_screenheight()) in requests
    assert (reopened.winfo_width(), reopened.winfo_height()) == (min(850,reopened.winfo_screenwidth()),min(630,reopened.winfo_screenheight()))
    reopened.destroy()
    app.preferences.update(remember_window_size=False, remember_window_position=False)
    default = app.show_manage_phrases_dialog()
    app.root.update()
    assert default.winfo_width() == 800
    assert default.winfo_height() == 600
    default.destroy()


@pytest.mark.gui
def test_main_geometry_uses_default_when_remembering_is_disabled(app, monkeypatch):
    app.preferences.update(opening_geometry='900x650+20+30', remember_window_size=False,
                           remember_window_position=False, windows={'main':'1200x900+100+200'})
    requests = []
    original = app.root.geometry
    def record(value=None):
        if value is not None:
            requests.append(value)
        return original(value)
    monkeypatch.setattr(app.root, 'geometry', record)
    app.interface.register_window(app.root, 'main')
    app.root.update()
    assert fitted_geometry('900x650+20+30', app.root.winfo_screenwidth(), app.root.winfo_screenheight()) in requests
    assert (app.root.winfo_width(), app.root.winfo_height()) == (min(900,app.root.winfo_screenwidth()),min(650,app.root.winfo_screenheight()))


@pytest.mark.gui
def test_table_customization_sorting_and_row_identity(app):
    rows = [{'id':0,'phrase':{'original':'Zebra','beginning':'Ze','ending':'bra'}},
            {'id':1,'phrase':{'original':'Apple','beginning':'Ap','ending':'ple'}}]
    win = app.workflows.import_review(rows)
    app.root.update()
    tree = next(w for w in descendants(win) if isinstance(w, ttk.Treeview))
    app.interface.commit({'tables':{'import_review':{'order':['phrase','status','include','error'],
        'visible':['phrase','status'], 'widths':{'phrase':300},'sort':'phrase','descending':False}}})
    assert tuple(tree.cget('displaycolumns')) == ('phrase','status')
    assert tree.get_children() == ('1','0')
    assert tree.set('0','phrase') == 'Zebra'
    app.interface.sort_table(tree, 'phrase')
    assert tree.get_children() == ('0','1')
    assert app.preferences['tables']['import_review']['descending'] is True
    win.destroy()
    again = app.workflows.import_review(rows)
    app.root.update()
    new = next(w for w in descendants(again) if isinstance(w, ttk.Treeview))
    assert new.get_children() == ('0','1')
    assert tuple(new.cget('displaycolumns')) == ('phrase','status')
    app.preferences['tables']['import_review']['sort'] = ''
    app.interface.apply_table(new)
    assert new.get_children() == ('0','1')
    new.column('phrase', width=1600, stretch=False)
    app.root.update()
    new.xview_moveto(1)
    assert new.cget('xscrollcommand')
    assert new.xview()[0] > 0
    again.destroy()


@pytest.mark.gui
@pytest.mark.parametrize('protected_name', ['ui_preferences.json', '.session.lock'])
def test_settings_export_import_draft_and_state_file_guard(app, monkeypatch, tmp_path, protected_name):
    win = app.interface.show()
    app.root.update()
    app.preferences['onboarding_complete'] = True
    exported = tmp_path / 'interface-export.json'
    monkeypatch.setattr('interface_settings.filedialog.asksaveasfilename', lambda **k:str(exported))
    button(win,'Export Settings…').invoke()
    document = json.loads(exported.read_text())
    assert 'onboarding_complete' not in document['settings']
    document['settings'].update(theme='dark', font_size=12)
    document['settings']['windows']['Manage Phrases'] = '820x620+30+40'
    exported.write_text(json.dumps(document))
    before = deepcopy(app.preferences)
    monkeypatch.setattr('interface_settings.filedialog.askopenfilename', lambda **k:str(exported))
    button(win,'Import Settings…').invoke()
    assert app.preferences == before
    button(win,'Apply').invoke()
    assert app.preferences['theme'] == 'dark'
    assert app.preferences['onboarding_complete'] is True
    assert app.preferences['windows']['Manage Phrases'] == '820x620+30+40'
    active = app.generator.data_path(protected_name)
    if not active.exists():
        active.write_bytes(b'active session lock')
    saved = active.read_bytes()
    monkeypatch.setattr('interface_settings.filedialog.asksaveasfilename', lambda **k:str(active))
    errors = []
    monkeypatch.setattr('interface_settings.messagebox.showerror', lambda *a, **k: errors.append(a))
    button(win,'Export Settings…').invoke()
    assert active.read_bytes() == saved
    assert errors


@pytest.mark.gui
def test_settings_window_and_buttons_fit_default_size(app):
    win = app.interface.show()
    app.root.update()
    for w in descendants(win):
        if isinstance(w, ttk.Button) and w.winfo_ismapped():
            assert w.winfo_rooty()+w.winfo_height() <= win.winfo_rooty()+win.winfo_height()
            assert w.winfo_rootx()+w.winfo_width() <= win.winfo_rootx()+win.winfo_width()
    language = next(w for w in descendants(win) if isinstance(w, ttk.Combobox) and tuple(w.cget('values')) == ('English',))
    assert language.get() == 'English'
    tools = app.assistance.tools_menu
    assert tools.entrycget(0, 'label') == 'Interface…'


@pytest.mark.gui
def test_optional_qt_utility_uses_the_saved_base_font(app, qapp):
    from log_manager import LogManager
    app.interface.commit({'font_size':13})
    window = LogManager()
    try:
        assert window.font().pointSize() == 13
        assert window.logTextEdit.font().pointSize() == 13
        assert window.clearButton.font().pointSize() == 13
    finally:
        window.close()
        window.deleteLater()


@pytest.mark.gui
def test_unavailable_imported_font_falls_back_to_system_default(app, monkeypatch, tmp_path):
    document = export_document(DEFAULTS)
    document['settings']['font_family'] = 'Not installed - interface portability test'
    path = tmp_path / 'portable.json'
    path.write_text(json.dumps(document))
    notices = []
    monkeypatch.setattr('interface_settings.messagebox.showinfo', lambda *a, **k:notices.append(a))
    monkeypatch.setattr('interface_settings.filedialog.askopenfilename', lambda **k:str(path))
    win = app.interface.show()
    app.root.update()
    button(win, 'Import Settings…').invoke()
    assert any(args[0] == 'Font unavailable' for args in notices)
    button(win, 'Apply').invoke()
    assert app.preferences['font_family'] == ''


@pytest.mark.gui
def test_appearance_only_apply_does_not_move_main_window(app, monkeypatch):
    win = app.interface.show()
    app.root.update()
    theme = next(w for w in descendants(win) if isinstance(w, ttk.Combobox) and tuple(w.cget('values')) == ('Light','Dark','System'))
    theme.set('Dark')
    requested = []
    original = app.root.geometry
    def record(value=None):
        if value is not None:
            requested.append(value)
        return original(value)
    monkeypatch.setattr(app.root, 'geometry', record)
    button(win, 'Apply').invoke()
    assert app.theme_mode == 'dark'
    assert requested == []
