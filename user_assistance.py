"""Offline user assistance for the Tk desktop, with no independent data writer."""
from pathlib import Path
import re
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from app_resources import resource_path

ROOT = Path(__file__).resolve().parent
CONTACT = 'richardnoragon@mac.com'

# Topic id -> (title, keywords, description/body, related topic ids).
TOPICS = {'start': ('Getting Started',
           'welcome first launch onboarding create new begin',
           'Use Generate for results, Library for source phrases, and Favorites/History for saved output. '
           'First launch copies existing data to the shared store without moving originals. The data path '
           'appears in the footer.\n'
           '\n'
           '1. Choose all languages and click Generate (at least two matching sources).\n'
           '2. Copy or Add to Favorites.\n'
           '3. Rate it, ask for More Like This, or Avoid This Combination.\n'
           '4. Find saved results in Favorites or History.\n'
           '5. Press F1 for the current view or Help for tours and guided tasks.\n'
           '\n'
           'Create New Phrase and Import Existing Data use your active store. Try Demo opens a separate '
           'temporary store. Skip onboarding and replay it later from Help.',
           ('concepts', 'generate', 'import')),
 'concepts': ('Core Concepts',
              'library libraries phrase phrases item items tags categories source metadata learning center '
              'why',
              'The library is the proverbs list in malaphors.json. Each phrase has original text, a '
              'beginning and an ending. Generation combines two phrases. Language and tags optionally '
              'restrict the ingredients. Tags/categories need at least two matching phrases.\n'
              '\n'
              'History records results and their sources. Favorites are saved displayed strings. Editing a '
              'source does not rename all historical results. Undo/redo covers supported deletions in the '
              'current session; it is not a backup.',
              ('generate', 'advanced', 'backup')),
 'generate': ('Generate and Save a Favorite',
              'generate generation random smart favorites favorite save first task',
              'Generate combines two different matching source phrases. Random choices use saved ratings, '
              'skip avoided ordered pairs and prefer outputs not among the latest 20 saved results. If fresh '
              'combinations run out, an unblocked result may repeat.\n'
              '\n'
              'More Like This prefers combinations sharing a source with the displayed result. Avoid This '
              'Combination persists that ordered pair; undo it with Advanced → Manage Avoided Combinations. '
              'Rate 1–5, then Save Rating. These are local heuristics.\n'
              '\n'
              'Copy shares the displayed text; Add to Favorites keeps it. Favorites and History have '
              'separate tabs and filters. Manual Combine and Batch Generation are under Advanced.',
              ('concepts', 'search', 'backup')),
 'search': ('Search and Manage Content',
            'find search searching edit delete phrases history favorites empty',
            'Library searches original source phrase text. Manage Phrases edits/deletes source records. '
            'Favorites and History filter saved results in their own tabs and offer management/export '
            'dialogs. Advanced → Manual Combine provides separate source selectors.\n'
            '\n'
            'Ctrl+F focuses Library search. If nothing matches, clear the filter or try a shorter term. '
            'Search Help searches documentation, not your personal data. Ctrl+Shift+P finds actions across '
            'tabs and Advanced.',
            ('generate', 'import', 'trouble')),
 'import': ('Import Source Phrases',
            'import importing json merge add create proverb phrase',
            'Library → Import Malaphors reads JSON into a review table before saving. Rows are new, '
            'duplicate or invalid. Select a row, edit its JSON object, Save Row Correction, or toggle '
            'Include / Exclude Selected. Included invalid rows block import; excluded rows are ignored; '
            'exact-original duplicates are skipped. Apply Reviewed Import revalidates, backs up, saves once, '
            'then refreshes search.\n'
            '\n'
            'JSON requires {"proverbs": [{"original": "A stitch in time saves nine", "beginning": "A stitch '
            'in time", "ending": "saves nine"}]}. Optional language/source are text and tags is a text list. '
            'The preview accepts files up to 25 MB. History/favorites/text exports are not phrase import '
            'formats. Cancel before commit leaves data unchanged.',
            ('backup', 'export', 'trouble')),
 'export': ('Export and Share',
            'export exporting image png svg share format file formats',
            'Export Originals saves the phrase library; Export Generated saves history. Manage Favorites '
            'offers Export Favorites. Choose JSON for structured data or text for reading. Only '
            'phrase-library JSON is a phrase import format. Copy copies the displayed result. Image export '
            'supports PNG (Pillow) and SVG.\n'
            '\n'
            'An export of phrases alone is not a complete backup. Check the chosen path before replacing a '
            'file.',
            ('import', 'backup', 'advanced')),
 'backup': ('Backups and Recovery',
            'backup backups restore recovery corrupt corrupted missing files storage paths migration '
            'synchronization',
            'The desktop footer shows the explicit shared data directory. Normal desktop and CLI default to '
            'the XDG store and support --data-dir or MALIPHORS_INATOR_DATA_DIR. First default launch copies '
            'legacy data without deleting originals. Normal entry points hold a single-writer session lock.\n'
            '\n'
            'Backups / Restore lists snapshots and creates portable ZIPs. Startup retains the latest 14 '
            'startup snapshots; reviewed imports and cleanup keep pre-change backups. Restore preview lists '
            'replacements, validates known filenames/schemas/checksums and asks approval. Missing archive '
            'files remain unchanged. A safety backup precedes replacement; failures roll back replaced files '
            'and report recovery needs.\n'
            '\n'
            'For manual copies/restores close all writers first. The old Daily Test is still a separate '
            'sandbox. Keep external backups. See USER_GUIDE.md and the upgrade guide for migration '
            'precedence and the 100 MB restore limit.',
            ('trouble', 'advanced', 'export')),
 'advanced': ('Advanced Concepts and Tools',
              'power user profiles ratings weighted templates tags statistics theme architecture learning '
              'center automation',
              'Advanced contains Manual Combine, Batch Generation, tags/categories, '
              'ratings/templates/profiles, statistics, gallery, image export and cleanup. Core Concepts '
              'explains source phrases, generated history and favorites.\n'
              '\n'
              'Import, cleanup, backup and batch workflows use background workers with '
              'progress/cancellation. Cancel is checked between records or before save; an atomic commit '
              'already underway finishes safely. Batch cancellation keeps completed results. Some legacy '
              'advanced single-result actions remain synchronous.\n'
              '\n'
              'The app uses local JSON, no network service or external AI. Session locks prevent another '
              'normal desktop/CLI writer, but there is no cross-computer synchronization or power-loss '
              'transaction spanning all state files.',
              ('concepts', 'backup', 'shortcuts')),
 'trouble': ('Troubleshooting',
             'error failure failed cannot no data empty permissions display tkinter missing performance',
             'No result? Choose all languages and ensure two different matching source phrases. If pairs are '
             'blocked, use Advanced → Manage Avoided Combinations.\n'
             '\n'
             'Wrong library? Check the footer or CLI --data-path. Desktop/CLI resolve --data-dir, then '
             'MALIPHORS_INATOR_DATA_DIR, then the XDG store. The old Daily Test remains separate.\n'
             '\n'
             'Another session error? Close the other desktop/CLI writer for that directory.\n'
             '\n'
             'Import blocked? Correct included invalid rows or exclude them in the review table; check the '
             '25 MB file limit. Save failed? Check paths, permissions and space, retaining backups.\n'
             '\n'
             'Unreadable saved data? Use Backups / Restore to inspect and restore a known-good snapshot. '
             'Preserve originals. If rollback reports a failure, inspect its safety backup.\n'
             '\n'
             'Long operation? The upgraded workflows show progress and Cancel; a commit underway finishes '
             'safely. Some legacy advanced actions still run synchronously. Diagnostics below are read-only.',
             ('backup', 'import', 'report')),
 'shortcuts': ('Keyboard Shortcuts',
               'keyboard shortcuts keys hotkeys reference navigation',
               'F1: context help for the active screen\n'
               'Ctrl+Shift+P: search actions\n'
               'Ctrl+G: generate\n'
               'Ctrl+C: copy displayed result (normal text copy remains available inside text fields)\n'
               'Ctrl+H: manage history\n'
               'Ctrl+F: focus source search in Library\n'
               'Ctrl+S: add displayed result to favorites\n'
               'Ctrl+Z: undo a supported deletion\n'
               'Ctrl+Y or Ctrl+Shift+Z: redo\n'
               '\n'
               'In help: Tab moves focus, Enter opens the selected topic/action, Escape closes the window. '
               'Tour and guided-task buttons work with Tab and Space.',
               ('search', 'generate')),
 'report': ('Report Problem',
            'bug issue contact security vulnerability conduct feedback',
            'Ordinary bugs: https://github.com/richardnoragon/maliphors-inator/issues\n'
            '\n'
            'Include revision/build, OS/Python, steps, expected/actual behavior and whether it reproduces '
            'with disposable data. Remove private phrases, paths and credentials before sharing logs.\n'
            '\n'
            'Security vulnerabilities and confidential conduct reports: richardnoragon@mac.com. Do not '
            'publish sensitive details in an issue. Nothing is sent automatically from this help window.',
            ('trouble',)),
 'about': ('About maliphors-inator',
           'about license version release pre alpha',
           'maliphors-inator combines idioms and proverbs in a local Python/Tk desktop app and CLI. '
           'Previously malaphors-rs / Malaphors-inator.\n'
           '\n'
           'Stage: pre-alpha. Historical technical alpha checks passed; human usability review and '
           'independent developer handoff remain open. Package metadata and historical changelog versions do '
           'not declare alpha readiness.\n'
           '\n'
           'Proprietary license: see LICENSE. Contact: richardnoragon@mac.com. Offline help does not send '
           'telemetry or personal data.',
           ('start', 'report'))}

def search_topics(query):
    """AND-match normalized query words across title, keywords and article text."""
    terms = re.findall(r'\w+', query.casefold())
    return [key for key, (title, keywords, body, _) in TOPICS.items()
            if all(term in f'{title} {keywords} {body}'.casefold() for term in terms)]


def context_topic(title):
    title = title.casefold()
    for words, topic in [(('favorite',), 'generate'), (('history', 'phrase', 'combine'), 'search'),
                         (('import', 'proverb'), 'import'), (('export',), 'export'),
                         (('tag', 'categor', 'power', 'profile', 'statistic', 'gallery'), 'advanced')]:
        if any(word in title for word in words):
            return topic
    return 'start'


class UserAssistance:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.windows = []
        self.overlays = []
        self.tour_window = None
        self.demo_process = None
        self.demo_directory = None
        menu = tk.Menu(self.root)
        advanced = tk.Menu(menu, tearoff=False)
        for label, command in app.action_commands.items():
            advanced.add_command(label=label, command=command)
        menu.add_cascade(label='Advanced', menu=advanced)
        help_menu = tk.Menu(menu, tearoff=False)
        for label, command in [
            ('Getting Started', self.welcome), ('Feature Tour', self.tour),
            ('Guided Tasks', self.guided_tasks), ('User Guide', self.user_guide),
            ('Search Help', self.show_help), ('Troubleshooting', self.troubleshoot),
            ('Keyboard Shortcuts', lambda: self.show_help('shortcuts')),
            ('Release Notes', self.release_notes), ('Report Problem', lambda: self.show_help('report')),
            ('About', lambda: self.show_help('about')),
        ]:
            help_menu.add_command(label=label, command=command)
        menu.add_cascade(label='Help', menu=help_menu)
        self.root.config(menu=menu)
        self.root.bind('<F1>', self.context_help)
        self.root.bind('<Control-Shift-P>', lambda event: self.palette())
        self.root.bind('<Control-Shift-p>', lambda event: self.palette())

    def window(self, title, geometry='760x560', parent=None):
        win = tk.Toplevel(parent or self.root)
        win.title(title)
        win.geometry(geometry)
        win.transient(parent or self.root)
        win.bind('<Escape>', lambda event: win.destroy())
        self.windows.append(win)
        def forget(event):
            if event.widget is win and win in self.windows:
                self.windows.remove(win)
        win.bind('<Destroy>', forget, add='+')
        return win

    @staticmethod
    def text(parent, content):
        frame = ttk.Frame(parent)
        frame.pack(fill='both', expand=True, padx=12, pady=8)
        bar = ttk.Scrollbar(frame)
        bar.pack(side='right', fill='y')
        text = tk.Text(frame, wrap='word', height=10, font='TkDefaultFont', padx=12, pady=12, yscrollcommand=bar.set)
        text.pack(fill='both', expand=True)
        bar.config(command=text.yview)
        text.insert('1.0', content)
        text.config(state='disabled')
        return text

    def context_help(self, event=None):
        widget = event.widget if event else self.root.focus_get()
        parent = widget.winfo_toplevel() if widget else self.root
        topic = context_topic(parent.title())
        if parent is self.root:
            name = self.app.notebook.tab(self.app.notebook.select(), 'text')
            topic = {'Generate': 'generate', 'Library': 'search', 'Favorites': 'generate', 'History': 'search'}[name]
        self.show_help(topic, parent=parent)
        return 'break'

    def show_help(self, topic='start', parent=None):
        win = self.window('Search Help — maliphors-inator', parent=parent)
        query = tk.StringVar()
        ttk.Label(win, text='Search local help (for example: add phrase, backups, import)').pack(anchor='w', padx=12, pady=6)
        entry = ttk.Entry(win, textvariable=query)
        entry.pack(fill='x', padx=12)
        results = tk.Listbox(win, height=5, exportselection=False)
        results.pack(fill='x', padx=12, pady=6)
        body = self.text(win, '')
        related = ttk.Frame(win)
        related.pack(fill='x', padx=12)
        keys = []

        def display(key):
            title, _, content, links = TOPICS[key]
            body.config(state='normal')
            body.delete('1.0', 'end')
            body.insert('1.0', f'{title}\n\n{content}')
            body.config(state='disabled')
            for child in related.winfo_children():
                child.destroy()
            for target in links:
                ttk.Button(related, text=TOPICS[target][0], command=lambda t=target: display(t)).pack(side='left', padx=2)

        def refresh(*args):
            keys[:] = search_topics(query.get())
            results.delete(0, 'end')
            for key in keys:
                results.insert('end', TOPICS[key][0])
            if keys:
                results.selection_set(0)
                display(keys[0])
            else:
                body.config(state='normal')
                body.delete('1.0', 'end')
                body.insert('1.0', 'No matching help. Try a shorter term, such as import or backup, or clear the search.')
                body.config(state='disabled')
                for child in related.winfo_children():
                    child.destroy()

        def select(event=None):
            if results.curselection():
                display(keys[results.curselection()[0]])
        query.trace_add('write', refresh)
        results.bind('<<ListboxSelect>>', select)
        results.bind('<Return>', select)
        entry.bind('<Return>', select)
        refresh()
        display(topic if topic in TOPICS else 'start')
        ttk.Button(win, text='Close', command=win.destroy).pack(pady=8)
        entry.focus_set()
        return win

    def document(self, name, title):
        try:
            content = resource_path(name).read_text(encoding='utf-8')
        except OSError:
            content = f'{name} is unavailable in this installation. Use Search Help for offline guidance.'
        win = self.window(title)
        self.text(win, content)
        ttk.Button(win, text='Close', command=win.destroy).pack(pady=8)
        return win

    def user_guide(self):
        return self.document('USER_GUIDE.md', 'User Guide')

    def release_notes(self):
        return self.document('CHANGELOG.md', 'Release Notes')

    def welcome(self):
        win = self.window('Getting Started — maliphors-inator', '680x540')
        self.text(win, TOPICS['start'][2] + '\n\nChoose your first action below. Demo changes are discarded when its window closes. You can skip onboarding and replay it from Help.')
        actions = ttk.Frame(win)
        actions.pack(fill='x', padx=12)
        ttk.Button(actions, text='Create New Phrase', command=self.app.show_add_proverb_dialog).pack(side='left', padx=3)
        ttk.Button(actions, text='Import Existing Data', command=self.app.workflows.import_file).pack(side='left', padx=3)
        ttk.Button(actions, text='Try Demo', command=self.demo).pack(side='left', padx=3)
        ttk.Button(win, text='Feature Tour', command=self.tour).pack(pady=4)
        ttk.Button(win, text='Guide My First Result', command=lambda: self.guided_task('first')).pack(pady=4)
        def finish():
            if not self.app.preferences.get('onboarding_complete'):
                self.app.preferences['onboarding_complete'] = True
                if not self.app._save_ui_preferences():
                    self.app.preferences.pop('onboarding_complete', None)
                    messagebox.showerror('Could not save preference', 'Getting Started will appear again next launch.', parent=win)
                    return
            win.destroy()
        ttk.Button(win, text='Done / Skip for now', command=finish).pack(pady=8)
        win.protocol('WM_DELETE_WINDOW', finish)
        win.bind('<Escape>', lambda event: finish())
        return win

    def demo(self):
        """Run the app in a separate process and temporary working directory."""
        import json
        import subprocess
        import sys
        import tempfile
        if self.demo_process and self.demo_process.poll() is None:
            return self.demo_process
        directory = tempfile.TemporaryDirectory(prefix='maliphors-demo-')
        data = Path(directory.name)
        examples = [{'original': 'A stitch in time saves nine', 'beginning': 'A stitch in time', 'ending': 'saves nine'},
                    {'original': 'The early bird catches the worm', 'beginning': 'The early bird', 'ending': 'catches the worm'}]
        (data / 'malaphors.json').write_text(json.dumps({'proverbs': examples}), encoding='utf-8')
        script = ('import sys; sys.path.insert(0, sys.argv[1]); '
                  'from maliphors_inator_ui import MaliphorsInatorApp; '
                  'app = MaliphorsInatorApp(); '
                  'app.root.title("maliphors-inator — Temporary Demo"); app.run()')
        try:
            process = subprocess.Popen([sys.executable, '-c', script, str(ROOT)], cwd=data, env={**os.environ, 'MALIPHORS_INATOR_DATA_DIR': str(data)})
        except OSError as exc:
            directory.cleanup()
            messagebox.showerror('Demo could not start', str(exc), parent=self.root)
            return None
        self.demo_process, self.demo_directory = process, directory
        def check():
            if self.demo_process is not process:
                return
            if process.poll() is None:
                self.root.after(300, check)
            else:
                directory.cleanup()
                self.demo_process = self.demo_directory = None
        self.root.after(300, check)
        return process

    def buttons(self):
        def walk(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Toplevel):
                    continue
                if isinstance(child, tk.Button):
                    yield child
                yield from walk(child)
        return list(walk(self.root))

    def clear_highlight(self):
        for overlay in self.overlays:
            overlay.destroy()
        self.overlays.clear()

    def tour(self):
        if self.tour_window and self.tour_window.winfo_exists():
            self.tour_window.destroy()
        self.clear_highlight()
        win = self.window('Feature Tour', '560x250')
        self.tour_window = win
        steps = [('Manage Phrases', 'Your ingredients: inspect and edit source phrases.'),
                 ('Generate', 'Create a result using at least two different matching phrases.'),
                 ('Add to Favorites', 'Keep a generated result for later.'),
                 ('More Like This', 'Keep a source you liked while finding fresh combinations; use Advanced for manual combinations.'),
                 ('Import Malaphors', 'Merge phrase JSON after making a backup.'),
                 ('Export Originals', 'Export phrases. History and favorites have separate exports.'),
                 ('Manage History', 'Find generated results. F1 opens context help on each screen.')]
        position = [0]
        label = ttk.Label(win, wraplength=510, padding=18)
        label.pack(fill='both', expand=True)
        controls = ttk.Frame(win)
        controls.pack(pady=10)
        def render():
            self.clear_highlight()
            name, explanation = steps[position[0]]
            label.config(text=f'{position[0]+1} / {len(steps)} — {name}\n\n{explanation}\n\nThe highlighted control is in the main window. The tour does not click it for you.')
            tab = {'Manage Phrases': 'Library', 'Import Malaphors': 'Library', 'Export Originals': 'Library', 'Manage History': 'History'}.get(name, 'Generate')
            self.app.notebook.select(self.app.views[tab])
            self.root.update_idletasks()
            target = next((b for b in self.buttons() if b.cget('text') == name), None)
            if target:
                x = target.winfo_rootx() - self.root.winfo_rootx()
                y = target.winfo_rooty() - self.root.winfo_rooty()
                w, h = target.winfo_width(), target.winfo_height()
                rw, rh = self.root.winfo_width(), self.root.winfo_height()
                for left, top, width, height in [(0, 0, rw, y), (0, y, x, h), (x+w, y, rw-x-w, h), (0, y+h, rw, rh-y-h)]:
                    if width > 0 and height > 0:
                        frame = tk.Frame(self.root, bg='#263238')
                        frame.place(x=left, y=top, width=width, height=height)
                        self.overlays.append(frame)
            back.config(state='normal' if position[0] else 'disabled')
            next_button.config(text='Finish' if position[0] == len(steps)-1 else 'Next')
        def move(delta):
            position[0] += delta
            if position[0] == len(steps):
                win.destroy()
            else:
                render()
        back = ttk.Button(controls, text='Back', command=lambda: move(-1))
        back.pack(side='left', padx=6)
        next_button = ttk.Button(controls, text='Next', command=lambda: move(1))
        next_button.pack(side='left', padx=6)
        ttk.Button(controls, text='Cancel', command=win.destroy).pack(side='left', padx=6)
        win.bind('<Destroy>', lambda event: self.clear_highlight() if event.widget is win else None, add='+')
        # Reposition the mask when the main window resizes or moves.
        binding = self.root.bind('<Configure>', lambda event: render() if event.widget is self.root and win.winfo_exists() else None, add='+')
        win.bind('<Destroy>', lambda event: self.root.unbind('<Configure>', binding) if event.widget is win else None, add='+')
        render()
        next_button.focus_set()
        return win

    def guided_tasks(self):
        win = self.window('Guided Tasks', '560x300')
        ttk.Label(win, text='Choose a task. Actions use your current data; Cancel stops the guide.', wraplength=510, padding=12).pack()
        for key, title in [('first', 'Generate, favorite and find a result'), ('import', 'Import source phrases'), ('backup', 'Back up and restore safely')]:
            ttk.Button(win, text=title, command=lambda k=key: self.guided_task(k)).pack(pady=8)
        return win

    def guided_task(self, kind):
        history = len(self.app.generator.history)
        favorites = len(self.app.generator.favorites)
        phrases = len(self.app.generator.proverbs)
        if kind == 'first':
            steps = [
                ('Generate', 'Requirements: at least two matching source phrases. Click Perform Step to generate. Validation checks for a new saved history result.', self.app.generate_malaphor, lambda: len(self.app.generator.history) > history),
                ('Save a Favorite', 'Review your result, then Perform Step to add it to favorites. Validation checks that favorites grew. If it was already saved, generate a different result.', self.app.add_to_favorites, lambda: len(self.app.generator.favorites) > favorites),
                ('Find It Again', 'Open Manage Favorites, find your result and close the dialog. Confirm below when you have found it.', self.app.show_favorites_dialog, None)]
        elif kind == 'import':
            steps = [
                ('Prepare', 'Requirements: close other writers and make a backup before import. Review the format, then confirm preparation below.', lambda: self.show_help('import'), None),
                ('Import', 'Select phrase-library JSON. Cancel or duplicate-only import will not complete this step. Validation checks that the library grew.', self.app.workflows.import_file, lambda: len(self.app.generator.proverbs) > phrases),
                ('Find Imported Phrases', 'Open Manual Combine, search for an imported phrase, then close the dialog. Confirm that you found it.', self.app.show_manual_combine_dialog, None)]
        else:
            steps = [
                ('Prepare Backup', 'Read the complete instructions. Close the app and all CLI writers before copying the JSON files. This guide does not copy or replace files.', lambda: self.show_help('backup'), None),
                ('Copy and Inspect', 'After closing the app, copy all data JSON files into a separate directory. Inspect the copy and retain the original files. Reopen this guide from Help when ready.', lambda: self.show_help('backup'), None),
                ('Restore and Validate', 'Preserve current files. With the app closed, copy known-good files back, reopen and verify phrases/history/favorites. Confirm here only after checking the reopened app.', lambda: self.show_help('backup'), None)]
        win = self.window('Guided Task', '620x400')
        position = [0]
        label = ttk.Label(win, wraplength=560, padding=18)
        label.pack(fill='both', expand=True)
        confirmed = tk.BooleanVar(value=False)
        confirm = ttk.Checkbutton(win, text='I completed and checked this step', variable=confirmed)
        confirm.pack(pady=6)
        status = ttk.Label(win, wraplength=560)
        status.pack(pady=6)
        def render():
            title, description, _, validate = steps[position[0]]
            label.config(text=f'{position[0]+1} / {len(steps)} — {title}\n\n{description}')
            confirmed.set(False)
            confirm.config(state='disabled' if validate else 'normal')
            status.config(text='')
        def advance():
            _, _, _, validate = steps[position[0]]
            if not (validate() if validate else confirmed.get()):
                status.config(text='This step is not complete yet. Perform the action or confirm the manual check.')
                return
            position[0] += 1
            if position[0] == len(steps):
                label.config(text='Task complete. You have checked each step. Related help is available below.')
                perform.config(state='disabled')
                next_button.config(state='disabled')
                confirm.config(state='disabled')
                status.config(text='')
            else:
                render()
        perform = ttk.Button(win, text='Perform Step', command=lambda: steps[position[0]][2]())
        perform.pack(pady=4)
        next_button = ttk.Button(win, text='Validate / Next', command=advance)
        next_button.pack(pady=4)
        ttk.Button(win, text='Related Help', command=lambda: self.show_help('backup' if kind == 'backup' else 'import' if kind == 'import' else 'generate')).pack(pady=4)
        ttk.Button(win, text='Cancel / Close', command=win.destroy).pack(pady=6)
        render()
        return win

    def troubleshoot(self):
        win = self.window('Troubleshooting', '720x540')
        g = self.app.generator
        diagnostics = f'Data directory: {g.data_dir}\nSource phrases: {len(g.proverbs)} | History: {len(g.history)} | Favorites: {len(g.favorites)}\nProtected unreadable files: {", ".join(p.name for p in g.load_errors) or "none"}\n\nThese checks only read session state. They never repair or overwrite files automatically.'
        self.text(win, diagnostics)
        symptom = tk.StringVar(value='No generated result')
        choices = {'No generated result': 'generate', 'Missing library / wrong data': 'backup', 'Import or save failed': 'import', 'No search results': 'search', 'Slow or unresponsive operation': 'trouble'}
        ttk.Combobox(win, textvariable=symptom, values=list(choices), state='readonly').pack(fill='x', padx=12, pady=8)
        ttk.Button(win, text='Show Causes and Next Steps', command=lambda: self.show_help(choices[symptom.get()], parent=win)).pack(pady=6)
        ttk.Button(win, text='Report Problem', command=lambda: self.show_help('report', parent=win)).pack(pady=6)
        return win

    def palette(self):
        win = self.window('Search Actions', '580x460')
        query = tk.StringVar()
        entry = ttk.Entry(win, textvariable=query)
        entry.pack(fill='x', padx=12, pady=10)
        actions = {button.cget('text'): button.invoke for button in self.buttons()}
        actions.update(self.app.action_commands)
        actions.update({'Search Help': self.show_help, 'Getting Started': self.welcome,
                        'Feature Tour': self.tour, 'Guided Tasks': self.guided_tasks,
                        'Troubleshooting': self.troubleshoot, 'Advanced Concepts': lambda: self.show_help('advanced')})
        results = tk.Listbox(win, exportselection=False)
        results.pack(fill='both', expand=True, padx=12)
        matches = []
        def refresh(*args):
            matches[:] = [name for name in actions if all(term in name.casefold() for term in query.get().casefold().split())]
            results.delete(0, 'end')
            for name in matches:
                results.insert('end', name)
            if matches:
                results.selection_set(0)
        def run(event=None):
            if results.curselection():
                action = actions[matches[results.curselection()[0]]]
                win.destroy()
                action()
        query.trace_add('write', refresh)
        entry.bind('<Return>', run)
        results.bind('<Return>', run)
        results.bind('<Double-Button-1>', run)
        ttk.Button(win, text='Run Selected', command=run).pack(pady=8)
        refresh()
        entry.focus_set()
        return win

    def close(self):
        self.clear_highlight()
        if self.demo_process:
            if self.demo_process.poll() is None:
                self.demo_process.terminate()
                try:
                    self.demo_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.demo_process.kill()
                    self.demo_process.wait(timeout=2)
            self.demo_directory.cleanup()
            self.demo_process = self.demo_directory = None
        for win in list(self.windows):
            if win.winfo_exists():
                win.destroy()
        self.windows.clear()
