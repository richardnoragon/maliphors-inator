"""Validated, portable desktop appearance and window/table preferences."""
from copy import deepcopy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, font as tkfont, filedialog, messagebox
import weakref

DEFAULTS = {
    'theme': 'light', 'interface_language': 'en', 'font_family': '', 'font_size': 11,
    'remember_window_size': True, 'remember_window_position': True,
    'opening_geometry': '960x700', 'windows': {}, 'tables': {},
}
IMPORT_COLUMNS = ('status', 'include', 'phrase', 'error')
IMPORT_COLUMN_WIDTHS = {'status':100, 'include':100, 'phrase':400, 'error':280}
TABLE_COLUMNS = {'import_review': IMPORT_COLUMNS}
GEOMETRY = re.compile(r'^(\d{2,5})x(\d{2,5})([+-]\d{1,6})([+-]\d{1,6})$')
SIZE = re.compile(r'^(\d{2,5})x(\d{2,5})$')


def validate_preferences(value):
    """Validate known settings while leaving unrelated internal preferences intact."""
    if not isinstance(value, dict):
        raise ValueError('Interface settings must be an object')
    result = deepcopy(DEFAULTS)
    result.update(deepcopy(value))
    if result['theme'] not in ('light', 'dark', 'system'):
        raise ValueError('Theme must be Light, Dark or System')
    if result['interface_language'] != 'en':
        raise ValueError('English is the only supported interface language')
    if not isinstance(result['font_family'], str) or len(result['font_family']) > 150:
        raise ValueError('Invalid font family')
    if type(result['font_size']) is not int or not 8 <= result['font_size'] <= 18:
        raise ValueError('Font size must be an integer from 8 to 18')
    for key in ('remember_window_size', 'remember_window_position'):
        if type(result[key]) is not bool:
            raise ValueError(f'{key} must be true or false')
    opening = result['opening_geometry']
    if not isinstance(opening, str) or not (SIZE.fullmatch(opening) or GEOMETRY.fullmatch(opening)):
        raise ValueError('Opening geometry must be WIDTHxHEIGHT or WIDTHxHEIGHT+X+Y')
    if not isinstance(result['windows'], dict) or len(result['windows']) > 100:
        raise ValueError('Invalid remembered windows')
    for name, geometry in result['windows'].items():
        if not isinstance(name, str) or len(name) > 200 or not isinstance(geometry, str) or not GEOMETRY.fullmatch(geometry):
            raise ValueError('Invalid remembered window geometry')
    if not isinstance(result['tables'], dict) or set(result['tables']) - set(TABLE_COLUMNS):
        raise ValueError('Unknown table settings')
    for name, settings in result['tables'].items():
        columns = TABLE_COLUMNS[name]
        if not isinstance(settings, dict) or set(settings) - {'order','visible','widths','sort','descending'}:
            raise ValueError('Invalid table settings')
        order = settings.get('order', list(columns))
        visible = settings.get('visible', list(columns))
        widths = settings.get('widths', {})
        if not isinstance(order, list) or any(not isinstance(c, str) for c in order) or len(order) != len(columns) or set(order) != set(columns):
            raise ValueError('Table order must contain each column once')
        if not isinstance(visible, list) or any(not isinstance(c, str) for c in visible) or not visible or len(visible) != len(set(visible)) or set(visible) - set(columns):
            raise ValueError('At least one valid table column must remain visible')
        if not isinstance(widths, dict) or set(widths) - set(columns) or any(type(n) is not int or not 40 <= n <= 1600 for n in widths.values()):
            raise ValueError('Column widths must be from 40 to 1600 pixels')
        if settings.get('sort', '') not in ('', *columns) or type(settings.get('descending', False)) is not bool:
            raise ValueError('Invalid table sorting')
    return result


def export_document(preferences):
    validated = validate_preferences(preferences)
    return {'application': 'maliphors-inator', 'format': 1,
            'settings': {key: validated[key] for key in DEFAULTS}}


def parse_document(value):
    if not isinstance(value, dict) or value.get('application') != 'maliphors-inator' or type(value.get('format')) is not int or value['format'] != 1:
        raise ValueError('Not a supported maliphors-inator interface settings file')
    settings = value.get('settings')
    if not isinstance(settings, dict) or set(settings) - set(DEFAULTS):
        raise ValueError('Unknown or non-interface settings in the file')
    return {key: item for key, item in validate_preferences(settings).items() if key in DEFAULTS}


def system_theme():
    """GNOME color-scheme preference, GTK fallback, then a deterministic light default."""
    if shutil.which('gsettings'):
        try:
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                                    capture_output=True, text=True, timeout=.4, check=True)
            if 'prefer-dark' in result.stdout:
                return 'dark'
            if 'prefer-light' in result.stdout or 'default' in result.stdout:
                return 'light'
        except (OSError, subprocess.SubprocessError):
            pass
    return 'dark' if 'dark' in os.environ.get('GTK_THEME', '').lower() else 'light'


def fitted_geometry(value, screen_width, screen_height, *, position=True):
    match = GEOMETRY.fullmatch(value) or SIZE.fullmatch(value)
    if not match:
        raise ValueError('Invalid geometry')
    width = max(100, min(int(match[1]), screen_width))
    height = max(100, min(int(match[2]), screen_height))
    if position and len(match.groups()) == 4:
        x = max(0, min(int(match[3]), screen_width - width))
        y = max(0, min(int(match[4]), screen_height - height))
        return f'{width}x{height}+{x}+{y}'
    return f'{width}x{height}'


class InterfaceSettings:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.closed = False
        self.windows = weakref.WeakKeyDictionary()
        self.tables = weakref.WeakKeyDictionary()
        self.pending = set()
        self.fit_new_windows = weakref.WeakSet()
        self.settings_window = None
        self.default_family = tkfont.nametofont('TkDefaultFont', root=self.root).actual('family')
        self.system_mode = system_theme() if app.theme_mode == 'system' else 'light'
        self.configure_fonts()
        self._font_family = app.preferences.get('font_family', '')
        self._font_size = app.preferences.get('font_size', 11)
        self.bindings = []
        for cls in ('Tk', 'Toplevel'):
            binding = self.root.bind_class(cls, '<Map>', self.on_map, add='+')
            self.bindings.append((cls, binding))
        self.timer = self.root.after(10000, self.poll_system)

    def configure_fonts(self):
        family = self.app.preferences.get('font_family') or self.default_family
        available = set(tkfont.families(self.root))
        if family not in available:
            family = self.default_family
        size = self.app.preferences.get('font_size', 11)
        for name in ('TkDefaultFont','TkTextFont','TkMenuFont','TkHeadingFont','TkCaptionFont','TkSmallCaptionFont','TkIconFont','TkTooltipFont','TkFixedFont'):
            try:
                tkfont.nametofont(name, root=self.root).configure(family=family, size=size)
            except tk.TclError:
                pass
        for name, offset, weight in [('AppHeadingFont', 1, 'bold'), ('AppTitleFont', 6, 'bold'), ('AppResultFont', 5, 'normal')]:
            if name in tkfont.names(self.root):
                font = tkfont.nametofont(name, root=self.root)
            else:
                self.root.tk.call('font', 'create', name)
                font = tkfont.nametofont(name, root=self.root)
            font.configure(family=family, size=size+offset, weight=weight)
            # Keep named font objects alive; otherwise Tk deletes them on GC.
            setattr(self, name, font)
        self.root.option_add('*Font', 'TkDefaultFont')
        self.root.option_add('*Menu.font', 'TkMenuFont')
        self.root.option_add('*Text.font', 'TkTextFont')
        self.root.option_add('*Listbox.font', 'TkDefaultFont')
        self.root.option_add('*TCombobox*Listbox.font', 'TkDefaultFont')
        style = self.app.style
        style.configure('.', font='TkDefaultFont')
        style.configure('Treeview', font='TkDefaultFont', rowheight=size*2+8)
        style.configure('Treeview.Heading', font='TkHeadingFont')
        for name in ('TButton','TLabel','TCheckbutton','TRadiobutton','TEntry','TCombobox','TNotebook.Tab','TLabelframe.Label'):
            style.configure(name, font='TkDefaultFont')

    def effective_theme(self):
        return self.system_mode if self.app.theme_mode == 'system' else self.app.theme_mode

    def poll_system(self):
        if self.closed:
            return
        if self.app.theme_mode == 'system':
            selected = system_theme()
            if selected != self.system_mode:
                self.system_mode = selected
                self.app._apply_theme(self.root)
        self.timer = self.root.after(10000, self.poll_system)

    def on_map(self, event):
        win = event.widget
        if not isinstance(win, (tk.Tk, tk.Toplevel)) or win.wm_overrideredirect() or win in self.pending:
            return
        self.pending.add(win)
        def decorate():
            self.pending.discard(win)
            if self.closed or not win.winfo_exists():
                return
            if win not in self.windows and not getattr(win, '_interface_transient', False):
                self.register_window(win, win.title())
            self.apply_fonts(win)
            self.app._apply_theme(win)
            if win in self.fit_new_windows:
                self.fit_new_windows.discard(win)
                self.fit_content(win)
        self.root.after_idle(decorate)

    def apply_fonts(self, parent):
        if not parent.winfo_exists():
            return
        if isinstance(parent, tk.Menu):
            parent.configure(font='TkMenuFont')
            last = parent.index('end')
            for index in range(0 if last is None else last+1):
                if parent.type(index) in ('command','cascade','checkbutton','radiobutton'):
                    parent.entryconfigure(index, font='TkMenuFont')
        elif not isinstance(parent, (ttk.Widget, tk.Toplevel, tk.Tk)):
            try:
                current = str(parent.cget('font'))
                if current not in ('AppTitleFont','AppHeadingFont','AppResultFont'):
                    parent.configure(font='TkTextFont' if isinstance(parent, tk.Text) else 'TkDefaultFont')
            except tk.TclError:
                pass
        for child in parent.winfo_children():
            self.apply_fonts(child)

    def register_window(self, win, key):
        self.windows[win] = key
        preferences = self.app.preferences
        saved = preferences.get('windows', {}).get(key)
        if not saved:
            self.fit_new_windows.add(win)
        base = preferences.get('opening_geometry', '960x700') if key == 'main' else win.geometry()
        base_match = GEOMETRY.fullmatch(base) or SIZE.fullmatch(base)
        saved_match = GEOMETRY.fullmatch(saved) if saved else None
        if base_match:
            size_match = saved_match if saved_match and preferences.get('remember_window_size', True) else base_match
            position_match = saved_match if saved_match and preferences.get('remember_window_position', True) else base_match
            value = f'{int(size_match[1])}x{int(size_match[2])}'
            if len(position_match.groups()) == 4:
                value += f'{int(position_match[3]):+}{int(position_match[4]):+}'
            win.geometry(fitted_geometry(value, win.winfo_screenwidth(), win.winfo_screenheight()))
        def remember(event):
            if event.widget is win and not self.closed:
                try:
                    if win.state() == 'normal':
                        self.app.preferences.setdefault('windows', {})[key] = win.geometry()
                except tk.TclError:
                    pass
        win.bind('<Configure>', remember, add='+')

    def fit_content(self, win):
        """Grow fresh windows or windows with changed fonts when screen space allows."""
        if not win.winfo_exists():
            return
        win.update_idletasks()
        width = min(win.winfo_screenwidth(), max(win.winfo_width(), win.winfo_reqwidth()))
        height = min(max(100, win.winfo_screenheight()-70), max(win.winfo_height(), win.winfo_reqheight()))
        if width != win.winfo_width() or height != win.winfo_height():
            win.geometry(f'{width}x{height}')

    def capture(self):
        for win, key in list(self.windows.items()):
            try:
                if win.winfo_exists() and win.state() == 'normal':
                    self.app.preferences.setdefault('windows', {})[key] = win.geometry()
            except tk.TclError:
                pass
        for tree in list(self.tables):
            self.capture_table(tree)

    def register_table(self, tree, name):
        if name not in TABLE_COLUMNS:
            raise ValueError('Unknown table')
        self.tables[tree] = name
        tree._interface_headings = {c: str(tree.heading(c, 'text')) for c in TABLE_COLUMNS[name]}
        for column in TABLE_COLUMNS[name]:
            tree.heading(column, command=lambda c=column: self.sort_table(tree, c))
        tree.bind('<ButtonRelease-1>', lambda event: self.capture_table(tree), add='+')
        self.apply_table(tree)

    def capture_table(self, tree):
        if not tree.winfo_exists():
            return
        name = self.tables[tree]
        settings = self.app.preferences.setdefault('tables', {}).setdefault(name, {})
        settings['widths'] = {c: max(40, min(1600, int(tree.column(c, 'width')))) for c in TABLE_COLUMNS[name]}

    def apply_table(self, tree):
        if not tree.winfo_exists():
            return
        name = self.tables[tree]
        settings = self.app.preferences.get('tables', {}).get(name, {})
        order = settings.get('order', list(TABLE_COLUMNS[name]))
        visible = settings.get('visible', list(TABLE_COLUMNS[name]))
        tree.configure(displaycolumns=[c for c in order if c in visible])
        for column, width in settings.get('widths', {}).items():
            tree.column(column, width=width)
        if settings.get('sort'):
            self.sort_table(tree, settings['sort'], settings.get('descending', False))
        else:
            for column, title in tree._interface_headings.items():
                tree.heading(column, text=title)
            for index, item in enumerate(sorted(tree.get_children(''), key=lambda item: int(item))):
                tree.move(item, '', index)

    def sort_table(self, tree, column, descending=None):
        name = self.tables[tree]
        settings = self.app.preferences.setdefault('tables', {}).setdefault(name, {})
        if descending is None:
            descending = not settings.get('descending', False) if settings.get('sort') == column else False
        settings.update(sort=column, descending=descending)
        for name, title in tree._interface_headings.items():
            tree.heading(name, text=title + (' ↓' if descending else ' ↑') if name == column else title)
        def key(item):
            value = str(tree.set(item, column))
            try:
                return (0, float(value))
            except ValueError:
                return (1, value.casefold())
        for index, item in enumerate(sorted(tree.get_children(''), key=key, reverse=descending)):
            tree.move(item, '', index)

    def commit(self, settings):
        candidate = deepcopy(self.app.preferences)
        candidate.update(settings)
        candidate = validate_preferences(candidate)
        family = candidate['font_family']
        if family and family not in set(tkfont.families(self.root)):
            raise ValueError(f'Font is not installed: {family}')
        if not self.app.generator._write_json(self.app.UI_PREFERENCES_FILE, candidate):
            raise OSError('Could not save interface settings; active settings were not changed')
        self.app.preferences = candidate
        self.app.theme_mode = candidate['theme']
        if candidate['theme'] == 'system':
            self.system_mode = system_theme()
        fonts_changed = (candidate['font_family'],candidate['font_size']) != (getattr(self, '_font_family', None),getattr(self, '_font_size', None))
        self.configure_fonts()
        self._font_family, self._font_size = candidate['font_family'], candidate['font_size']
        self.apply_fonts(self.root)
        self.app._apply_theme(self.root)
        for tree in list(self.tables):
            self.apply_table(tree)
        if fonts_changed:
            for win in list(self.windows):
                self.fit_content(win)
        return candidate

    def show(self):
        if self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return self.settings_window
        self.capture()
        win = tk.Toplevel(self.root)
        self.settings_window = win
        win.title('Interface Settings')
        win.geometry('820x650')
        win.minsize(760, 600)
        win.transient(self.root)
        win.bind('<F1>', lambda event: self.app.assistance.show_help('interface', parent=win))
        footer = ttk.Frame(win, padding=10)
        footer.pack(side='bottom', fill='x')
        tabs = ttk.Notebook(win)
        tabs.pack(fill='both', expand=True, padx=12, pady=12)
        def scrollable_tab(title):
            host = ttk.Frame(tabs)
            tabs.add(host, text=title)
            scroll = ttk.Scrollbar(host, orient='vertical')
            scroll.pack(side='right', fill='y')
            canvas = tk.Canvas(host, highlightthickness=0, yscrollcommand=scroll.set)
            canvas.pack(fill='both', expand=True)
            scroll.configure(command=canvas.yview)
            content = ttk.Frame(canvas, padding=16)
            item = canvas.create_window(0, 0, window=content, anchor='nw')
            canvas.bind('<Configure>', lambda event: canvas.itemconfigure(item, width=event.width))
            content.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.bind('<Button-4>', lambda event: canvas.yview_scroll(-1, 'units'))
            canvas.bind('<Button-5>', lambda event: canvas.yview_scroll(1, 'units'))
            return content
        appearance = scrollable_tab('Appearance')
        windows = scrollable_tab('Windows')
        table = scrollable_tab('Table Columns')
        theme = tk.StringVar()
        family = tk.StringVar()
        size = tk.IntVar()
        remember_size = tk.BooleanVar()
        remember_position = tk.BooleanVar()
        width, height, x, y = (tk.IntVar() for _ in range(4))
        ttk.Label(appearance, text='Appearance and interface fonts', font='AppHeadingFont').pack(anchor='w', pady=(0,16))
        def field(parent, label, widget):
            row = ttk.Frame(parent)
            row.pack(fill='x', pady=8)
            ttk.Label(row, text=label, width=24).pack(side='left')
            widget(row).pack(side='left', fill='x', expand=True)
        field(appearance, 'Theme', lambda row: ttk.Combobox(row, textvariable=theme, values=['Light','Dark','System'], state='readonly'))
        def language_field(row):
            widget = ttk.Combobox(row, values=['English'], state='readonly')
            widget.current(0)
            return widget
        field(appearance, 'Interface language', language_field)
        ttk.Label(appearance, text='English is currently supported. Phrase-generation language is selected separately.', wraplength=700).pack(anchor='w', pady=6)
        families = ['System default'] + sorted(set(tkfont.families(self.root)))
        field(appearance, 'Font family', lambda row: ttk.Combobox(row, textvariable=family, values=families, state='readonly'))
        field(appearance, 'Base font size (points)', lambda row: ttk.Spinbox(row, from_=8, to=18, textvariable=size, width=6))
        ttk.Label(appearance, text='Menus, submenus, controls and dialog text share this font. Titles retain a consistent heading size.', wraplength=700).pack(anchor='w', pady=14)
        ttk.Label(appearance, text='System theme follows the Linux desktop preference when available; otherwise Light is used.', wraplength=700).pack(anchor='w')
        ttk.Checkbutton(windows, text='Remember window sizes', variable=remember_size).pack(anchor='w', pady=8)
        ttk.Checkbutton(windows, text='Remember window locations', variable=remember_position).pack(anchor='w', pady=8)
        ttk.Label(windows, text='Default main-window opening geometry', font='AppHeadingFont').pack(anchor='w', pady=14)
        for label, variable in [('Width',width), ('Height',height), ('Left',x), ('Top',y)]:
            field(windows, label, lambda row, v=variable: ttk.Spinbox(row, from_=0, to=8192, textvariable=v, width=8))
        ttk.Label(windows, text='Saved windows are clamped to the current screen. Transient progress windows and tooltips do not retain a location.', wraplength=700).pack(anchor='w', pady=8)
        column_rows = []
        table_state = {}
        draft_windows = {}
        opening_draft = {}
        ttk.Label(table, text='Import review table', font='AppHeadingFont').pack(anchor='w')
        ttk.Label(table, text='Change order, visibility and width. Click a table heading to sort while reviewing an import.', wraplength=700).pack(anchor='w', pady=8)
        columns_frame = ttk.Frame(table)
        columns_frame.pack(fill='x', pady=5)
        sort_column = tk.StringVar()
        descending = tk.BooleanVar()
        def render_columns():
            for child in columns_frame.winfo_children():
                child.destroy()
            for index, row in enumerate(column_rows):
                line = ttk.Frame(columns_frame)
                line.pack(fill='x', pady=5)
                ttk.Checkbutton(line, text=row['name'].replace('_',' ').title(), variable=row['visible'], width=20).pack(side='left')
                ttk.Spinbox(line, from_=40, to=1600, textvariable=row['width'], width=6).pack(side='left', padx=6)
                def move(delta, i=index):
                    target = i+delta
                    if 0 <= target < len(column_rows):
                        column_rows[i], column_rows[target] = column_rows[target], column_rows[i]
                        render_columns()
                ttk.Button(line, text='Up', command=lambda m=move: m(-1), state='normal' if index else 'disabled').pack(side='left', padx=4)
                ttk.Button(line, text='Down', command=lambda m=move: m(1), state='normal' if index<len(column_rows)-1 else 'disabled').pack(side='left')
        field(table, 'Sort by', lambda row: ttk.Combobox(row, textvariable=sort_column, values=['Original order',*IMPORT_COLUMNS], state='readonly'))
        ttk.Checkbutton(table, text='Descending', variable=descending).pack(anchor='w', pady=8)
        def populate(settings):
            theme.set(settings['theme'].title())
            family.set(settings['font_family'] or 'System default')
            size.set(settings['font_size'])
            remember_size.set(settings['remember_window_size'])
            remember_position.set(settings['remember_window_position'])
            geometry = GEOMETRY.fullmatch(settings['opening_geometry']) or SIZE.fullmatch(settings['opening_geometry'])
            width.set(int(geometry[1])); height.set(int(geometry[2]))
            x.set(int(geometry[3]) if len(geometry.groups()) == 4 else 0)
            y.set(int(geometry[4]) if len(geometry.groups()) == 4 else 0)
            opening_draft.update(original=settings['opening_geometry'], values=(width.get(),height.get(),x.get(),y.get()))
            saved = settings.get('tables', {}).get('import_review', {})
            column_rows[:] = [{'name': c, 'visible':tk.BooleanVar(value=c in saved.get('visible',IMPORT_COLUMNS)),
                              'width':tk.IntVar(value=saved.get('widths',{}).get(c, IMPORT_COLUMN_WIDTHS[c]))}
                             for c in saved.get('order', IMPORT_COLUMNS)]
            sort_column.set(saved.get('sort') or 'Original order')
            descending.set(saved.get('descending',False))
            draft_windows.clear()
            draft_windows.update(deepcopy(settings.get('windows', {})))
            table_state.clear()
            table_state.update(deepcopy(settings.get('tables', {})))
            render_columns()
        def collect():
            values = (width.get(),height.get(),x.get(),y.get())
            geometry = opening_draft['original'] if values == opening_draft['values'] else f'{width.get()}x{height.get()}{x.get():+}{y.get():+}'
            if width.get()<760 or height.get()<580:
                raise ValueError('Main window needs at least 760 × 580 pixels')
            tables = deepcopy(table_state)
            tables['import_review'] = {'order':[r['name'] for r in column_rows],
                'visible':[r['name'] for r in column_rows if r['visible'].get()],
                'widths':{r['name']:r['width'].get() for r in column_rows},
                'sort':'' if sort_column.get() == 'Original order' else sort_column.get(), 'descending':descending.get()}
            candidate = {**deepcopy(self.app.preferences), 'theme':theme.get().lower(), 'font_family':'' if family.get()=='System default' else family.get(),
                         'font_size':size.get(), 'remember_window_size':remember_size.get(), 'remember_window_position':remember_position.get(),
                         'opening_geometry':geometry, 'tables':tables, 'windows':deepcopy(draft_windows)}
            return validate_preferences(candidate)
        def apply():
            try:
                candidate = collect()
                opening_changed = candidate['opening_geometry'] != self.app.preferences.get('opening_geometry', '960x700')
                imported_main = candidate.get('windows', {}).get('main') != self.app.preferences.get('windows', {}).get('main')
                if opening_changed:
                    candidate.setdefault('windows', {})['main'] = candidate['opening_geometry']
                self.commit(candidate)
                if opening_changed or imported_main:
                    geometry = candidate.get('windows', {}).get('main') or candidate['opening_geometry']
                    self.root.geometry(fitted_geometry(geometry, self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
                messagebox.showinfo('Interface settings saved', 'Your interface settings were saved and applied.', parent=win)
            except (ValueError, OSError, tk.TclError) as exc:
                messagebox.showerror('Interface settings', str(exc), parent=win)
        def use_current():
            geometry = GEOMETRY.fullmatch(self.root.geometry())
            if geometry:
                for variable, number in zip((width,height,x,y), geometry.groups()):
                    variable.set(int(number))
        def export():
            try:
                value = export_document(collect())
                path = filedialog.asksaveasfilename(parent=win, defaultextension='.json', initialfile='maliphors-interface.json', filetypes=[('Interface settings','*.json')])
                if path:
                    from maliphors_inator_logic import atomic_write_json
                    destination = Path(path).resolve()
                    from app_storage import STATE_FILES
                    if destination in {self.app.generator.data_path(name).resolve() for name in (*STATE_FILES,'migration.json','.session.lock')}:
                        raise ValueError('Choose an export file outside the active application state files')
                    atomic_write_json(destination, value)
                    messagebox.showinfo('Interface settings exported', str(destination), parent=win)
            except (ValueError, OSError, tk.TclError) as exc:
                messagebox.showerror('Export interface settings', str(exc), parent=win)
        def import_settings():
            path = filedialog.askopenfilename(parent=win, filetypes=[('Interface settings','*.json')])
            if not path:
                return
            try:
                if Path(path).stat().st_size > 1024*1024:
                    raise ValueError('Interface settings file exceeds 1 MB')
                settings = parse_document(json.loads(Path(path).read_text(encoding='utf-8')))
                chosen = settings['font_family']
                if chosen and chosen not in set(tkfont.families(self.root)):
                    settings['font_family'] = ''
                    messagebox.showinfo('Font unavailable', 'The exported font is not installed; System default will be used.', parent=win)
                populate(settings)
                messagebox.showinfo('Interface settings loaded', 'Review the imported options and click Apply to save them. No phrase data or internal onboarding state was imported.', parent=win)
            except (ValueError, OSError, TypeError) as exc:
                messagebox.showerror('Import interface settings', str(exc), parent=win)
        ttk.Button(windows, text='Use Current Main Window', command=use_current).pack(anchor='w', pady=5)
        ttk.Button(footer, text='Import Settings…', command=import_settings).pack(side='left', padx=4)
        ttk.Button(footer, text='Export Settings…', command=export).pack(side='left', padx=4)
        ttk.Button(footer, text='Close', command=win.destroy).pack(side='right', padx=4)
        ttk.Button(footer, text='Apply', command=apply).pack(side='right', padx=4)
        populate(validate_preferences(self.app.preferences))
        return win

    def close(self):
        if self.closed:
            return
        self.capture()
        self.app._save_ui_preferences()
        self.closed = True
        self.root.after_cancel(self.timer)
        for cls, binding in self.bindings:
            self.root._unbind(('bind', cls, '<Map>'), binding)


def apply_qt_fonts(window, directory=None):
    """Optional Qt utilities consume the same font preference without a Qt core dependency."""
    from app_storage import resolve_data_dir
    try:
        path = resolve_data_dir(directory) / 'ui_preferences.json'
        preferences = validate_preferences(json.loads(path.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError):
        preferences = validate_preferences({})
    chosen = window.font()
    if preferences['font_family']:
        chosen.setFamily(preferences['font_family'])
    chosen.setPointSize(preferences['font_size'])
    def apply(widget):
        if hasattr(widget, 'setFont'):
            widget.setFont(chosen)
        for child in widget.children():
            apply(child)
    apply(window)
