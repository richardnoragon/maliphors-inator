"""Tk worker coordination and reviewable library/backup operations."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import queue
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from app_storage import create_backup, preview_restore, restore_backup, STATE_FILES
from library_workflows import (OperationCancelled, preview_import, classify_rows,
                               plan_cleanup, checkpoint)


class DesktopWorkflows:
    """Only the Tk thread reads widgets; workers report through a queue."""
    def __init__(self, app):
        self.app = app
        self.active = None
        self.cancel = None
        self.poll_id = None
        self.closed = False

    def start(self, title, work, complete):
        if self.active is not None:
            messagebox.showinfo('Operation running', 'Finish or cancel the current operation first.', parent=self.app.root)
            return
        events = queue.Queue()
        self.cancel = threading.Event()
        win = tk.Toplevel(self.app.root)
        win.title(title)
        win.geometry('500x180')
        win.transient(self.app.root)
        win.grab_set()  # No simultaneous edits while a worker owns the generator.
        label = ttk.Label(win, text='Preparing…', padding=14, wraplength=450)
        label.pack(fill='x')
        bar = ttk.Progressbar(win, mode='indeterminate')
        bar.pack(fill='x', padx=14, pady=8)
        bar.start()
        def request_cancel():
            self.cancel.set()
            label.config(text='Cancelling… A save already committing will finish safely.')
        ttk.Button(win, text='Cancel', command=request_cancel).pack(pady=8)
        win.protocol('WM_DELETE_WINDOW', request_cancel)
        def progress(done, total):
            # Throttle large files so progress cannot exhaust the event queue.
            if done == total or done % max(1, total // 100) == 0:
                events.put(('progress', (done, total)))
        def run():
            try:
                value = work(self.cancel, progress)
                events.put(('done', value))
            except Exception as exc:
                events.put(('error', exc))
        self.active = threading.Thread(target=run, daemon=True)
        self.active.start()
        def poll():
            if self.closed:
                return
            try:
                while True:
                    kind, payload = events.get_nowait()
                    if kind == 'progress':
                        done, total = payload
                        bar.stop()
                        bar.config(mode='determinate', maximum=max(1, total), value=done)
                        label.config(text=f'{done} / {total}')
                    else:
                        win.destroy()
                        self.active.join()
                        self.active = None
                        if kind == 'done':
                            complete(payload)
                        elif isinstance(payload, OperationCancelled):
                            messagebox.showinfo('Cancelled', str(payload), parent=self.app.root)
                        else:
                            messagebox.showerror(title, str(payload), parent=self.app.root)
                        return
            except queue.Empty:
                self.poll_id = self.app.root.after(30, poll)
        self.poll_id = self.app.root.after(30, poll)
        return win

    def import_file(self):
        path = filedialog.askopenfilename(parent=self.app.root, filetypes=[('Phrase JSON', '*.json')])
        if not path:
            return
        existing = deepcopy(self.app.generator.proverbs)
        return self.start('Read Import Preview', lambda cancel, progress: preview_import(path, existing, cancel, progress), self.import_review)

    def import_review(self, rows):
        win = tk.Toplevel(self.app.root)
        win.title('Review Import — correct or exclude rows before saving')
        win.geometry('920x650')
        win.transient(self.app.root)
        win.grab_set()
        win.bind('<F1>', self.app.assistance.context_help)
        summary = ttk.Label(win, padding=8)
        summary.pack(fill='x')
        footer = ttk.Frame(win)
        footer.pack(side='bottom', fill='x', padx=10, pady=10)
        tree = ttk.Treeview(win, columns=('status', 'include', 'phrase', 'error'), show='headings', height=12)
        for key, title, width in [('status','Status',85), ('include','Import?',65), ('phrase','Original phrase',420), ('error','Issue',250)]:
            tree.heading(key, text=title)
            tree.column(key, width=width, stretch=key in ('phrase', 'error'))
        scroll = ttk.Scrollbar(win, orient='vertical', command=tree.yview)
        scroll.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(fill='both', expand=True, padx=10)
        editor = ttk.LabelFrame(win, text='Selected row: edit the JSON object (including optional metadata)')
        editor.pack(fill='x', padx=10, pady=5)
        text = tk.Text(editor, height=7, wrap='word')
        text.pack(fill='x', padx=5, pady=5)
        current = list(rows)
        selected = [None]
        def refresh():
            current[:] = classify_rows(current, self.app.generator.proverbs)
            tree.delete(*tree.get_children())
            counts = {k: sum(r['status'] == k and r.get('include', True) for r in current) for k in ('new','duplicate','invalid')}
            summary.config(text=f"{counts['new']} new · {counts['duplicate']} duplicate · {counts['invalid']} invalid included. Duplicates are skipped. Invalid included rows block import.")
            for row in current:
                p = row['phrase']
                tree.insert('', 'end', iid=str(row['id']), values=(row['status'], 'yes' if row.get('include', True) else 'no', p.get('original', '') if isinstance(p, dict) else repr(p), row['error'] or ''))
        def select(event=None):
            if tree.selection():
                selected[0] = int(tree.selection()[0])
                row = next(r for r in current if r['id'] == selected[0])
                text.delete('1.0', 'end')
                text.insert('1.0', json.dumps(row['phrase'], indent=2, ensure_ascii=False))
        def edit():
            if selected[0] is None:
                return
            try:
                value = json.loads(text.get('1.0', 'end'))
            except ValueError as exc:
                messagebox.showerror('Invalid JSON', str(exc), parent=win)
                return
            next(r for r in current if r['id'] == selected[0])['phrase'] = value
            refresh()
        def exclude():
            ids = set(tree.selection())
            for row in current:
                if str(row['id']) in ids:
                    row['include'] = not row.get('include', True)
            refresh()
        def apply():
            payload = deepcopy(current)
            # Keep the review window on failures/cancellation so corrections are retained.
            def done(count):
                win.destroy()
                self.app.update_history()
                messagebox.showinfo('Import complete', f'{count} new phrases saved. A pre-import backup was kept.', parent=self.app.root)
            win.grab_release()
            self.start('Apply Import', lambda cancel, progress: self.app.generator.commit_import_rows(payload, cancel, progress), done)
        tree.bind('<<TreeviewSelect>>', select)
        ttk.Button(footer, text='Save Row Correction', command=edit).pack(side='left', padx=4)
        ttk.Button(footer, text='Include / Exclude Selected', command=exclude).pack(side='left', padx=4)
        ttk.Button(footer, text='Apply Reviewed Import', command=apply).pack(side='right', padx=4)
        ttk.Button(footer, text='Cancel', command=win.destroy).pack(side='right', padx=4)
        refresh()
        return win

    def cleanup(self):
        original = deepcopy(self.app.generator.proverbs)
        def review(plan):
            if not plan['removed']:
                messagebox.showinfo('Cleanup preview', 'No invalid or exact duplicate phrases found.', parent=self.app.root)
                return
            if messagebox.askyesno('Cleanup preview', f"Remove {len(plan['removed'])} invalid/duplicate phrases? A backup will be made before saving.", parent=self.app.root):
                self.start('Apply Cleanup', lambda cancel, progress: self.app.generator.commit_cleanup(plan, original, cancel),
                           lambda count: (self.app.update_history(), messagebox.showinfo('Cleanup complete', f'{count} phrases removed.', parent=self.app.root)))
        return self.start('Preview Cleanup', lambda cancel, progress: plan_cleanup(original, cancel=cancel, progress=progress), review)

    def batch(self):
        win = tk.Toplevel(self.app.root)
        win.title('Batch Generation')
        win.geometry('460x190')
        ttk.Label(win, text='How many results? Completed results are saved; cancellation keeps them.', wraplength=420, padding=12).pack()
        count = tk.IntVar(value=10)
        ttk.Spinbox(win, from_=1, to=1000, textvariable=count).pack()
        def run():
            try:
                number = count.get()
                if not 1 <= number <= 1000:
                    raise ValueError('Choose 1 to 1000 results')
            except (ValueError, tk.TclError) as exc:
                messagebox.showerror('Batch size', str(exc), parent=win)
                return
            language = self.app.language_var.get()
            language = None if language == 'all' else language
            win.destroy()
            def work(cancel, progress):
                results = []
                for index in range(number):
                    if cancel.is_set():
                        break
                    results.append(self.app.generator.generate_malaphor(language=language))
                    progress(index+1, number)
                return results
            def done(results):
                if results:
                    self.app.display_result(results[-1])
                self.app.update_history()
                messagebox.showinfo('Batch finished', f'{len(results)} of {number} results saved.', parent=self.app.root)
            self.start('Batch Generation', work, done)
        ttk.Button(win, text='Generate Batch', command=run).pack(pady=10)
        return win

    def backups(self):
        win = tk.Toplevel(self.app.root)
        win.title('Backups and Restore')
        win.geometry('700x420')
        ttk.Label(win, text=f'Data directory: {self.app.generator.data_dir}', wraplength=650, padding=10).pack(fill='x')
        listing = tk.Listbox(win)
        listing.pack(fill='both', expand=True, padx=10, pady=5)
        paths = []
        def refresh():
            paths[:] = sorted((self.app.generator.data_dir / 'backups').glob('*.zip'), reverse=True)
            listing.delete(0, 'end')
            for path in paths:
                listing.insert('end', path.name)
        def backup():
            path = filedialog.asksaveasfilename(parent=win, defaultextension='.zip', filetypes=[('Backup ZIP', '*.zip')])
            if path:
                def work(cancel, progress):
                    with self.app.generator._persistence_lock:
                        checkpoint(cancel)
                        if not self.app.generator._run_auto_save():
                            raise OSError('Could not flush state before backup')
                        return create_backup(self.app.generator.data_dir, path)
                self.start('Create Backup', work, lambda path: (refresh(), messagebox.showinfo('Backup saved', str(path), parent=win)))
        def restore():
            path = paths[listing.curselection()[0]] if listing.curselection() else filedialog.askopenfilename(parent=win, filetypes=[('Backup ZIP', '*.zip')])
            if not path:
                return
            def inspect(cancel, progress):
                checkpoint(cancel)
                payload = Path(path).read_bytes()
                from io import BytesIO
                return preview_restore(BytesIO(payload)), hashlib.sha256(payload).hexdigest()
            def review(result):
                files, digest = result
                details = '\n'.join(f'{name}: {len(content)} bytes' for name, content in files.items())
                omitted = set(STATE_FILES) - set(files)
                details += '\n\nFiles not in this backup will remain unchanged.' if omitted else ''
                if not messagebox.askyesno('Restore preview', f'{details}\n\nReplace these files and reload? A safety backup will be saved first.', parent=win):
                    return
                def work(cancel, progress):
                    with self.app.generator._persistence_lock:
                        checkpoint(cancel)
                        return restore_backup(self.app.generator.data_dir, path, expected_digest=digest)
                def done(report):
                    g = self.app.generator
                    g.load_errors.clear()
                    g._load_data()
                    g.history = g._load_history_from_file()
                    g._load_ratings()
                    g.generation_templates = g._load_generation_templates()
                    g.generation_preferences = g._load_generation_preferences()
                    g._build_search_index()
                    g.search.cache_clear()
                    g.undo_stack.undo_stack.clear()
                    g.undo_stack.redo_stack.clear()
                    self.app.preferences = self.app._load_ui_preferences()
                    self.app.theme_mode = self.app.preferences.get('theme', 'light')
                    self.app._apply_theme(self.app.root)
                    self.app.current_result = None
                    self.app.sentence_label.config(text="Click 'Generate' to create a malaphor")
                    self.app.update_history()
                    refresh()
                    messagebox.showinfo('Restore complete', f"Restored {len(report['files'])} files. Safety backup: {report['safety_backup']}", parent=win)
                self.start('Restore Backup', work, done)
            self.start('Inspect Backup', inspect, review)
        ttk.Button(win, text='Create Backup…', command=backup).pack(side='left', padx=10, pady=10)
        ttk.Button(win, text='Preview / Restore Selected or ZIP…', command=restore).pack(side='right', padx=10, pady=10)
        refresh()
        return win

    def close(self):
        if self.active and self.active.is_alive():
            self.cancel.set()
            # The UI close action waits through polling; shutdown never saves stale state.
            return False
        self.closed = True
        if self.poll_id:
            self.app.root.after_cancel(self.poll_id)
        return True
