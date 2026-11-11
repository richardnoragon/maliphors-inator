"""GUI module for maliphors-inator."""
import asyncio
import json
from pathlib import Path

import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.ttk as ttk

from maliphors_inator_logic import MalaphorGenerator
from user_assistance import UserAssistance


class MaliphorsInatorApp:
    """GUI application for maliphors-inator."""

    MAX_HISTORY_LINES = 1000  # Maximum number of lines to keep in history
    HISTORY_CLEANUP_TRIGGER = 1200  # When to trigger cleanup
    UI_PREFERENCES_FILE = Path("ui_preferences.json")

    def __init__(self, root=None):
        """Initialize the GUI application."""
        self.generator = MalaphorGenerator()
        self.root = root or tk.Tk()
        if not root:
            self.root.title("maliphors-inator")
        self.tooltips = []  # Store tooltip references
        self.dialogs = {}  # Cache dialog references
        self.style = ttk.Style(self.root)
        self.preferences = self._load_ui_preferences()
        self.theme_mode = self.preferences.get("theme", "light")
        self.generator.start_auto_save(interval_seconds=300.0)
        self.setup_gui()
        self.assistance = UserAssistance(self)
        self.update_history()
        self._apply_theme(self.root)
        if self.generator.load_errors:
            names = ", ".join(path.name for path in self.generator.load_errors)
            self.root.after_idle(lambda: tkinter.messagebox.showwarning(
                "Saved data needs recovery",
                f"Could not fully load: {names}. These files will not be overwritten. "
                "Close the app, restore a backup, and restart. See USER_GUIDE.md: Files and backups.",
                parent=self.root))

    def setup_gui(self):
        """Set up the GUI components."""
        # Configure window
        self.root.geometry("900x860")
        self.root.configure(padx=20, pady=20)

        self.language_var = tk.StringVar(value="all")

        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill='both')

        # Create three button frames
        button_frame_top = tk.Frame(main_frame)
        button_frame_top.pack(pady=5)

        button_frame_middle = tk.Frame(main_frame)
        button_frame_middle.pack(pady=5)

        button_frame_bottom = tk.Frame(main_frame)
        button_frame_bottom.pack(pady=5)

        # Add buttons to top row with increased width
        manage_phrases_button = tk.Button(
            button_frame_top,
            text="Manage Phrases",
            command=self.show_manage_phrases_dialog,
            width=15
        )
        manage_phrases_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(manage_phrases_button, "View and edit the collection of proverbs")

        manual_combine_button = tk.Button(
            button_frame_top,
            text="Manual Combine",
            command=self.show_manual_combine_dialog,
            width=15
        )
        manual_combine_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(manual_combine_button, "Manually select two phrases to combine into a malaphor")

        add_proverb_button = tk.Button(
            button_frame_top,
            text="Add New Proverb",
            command=self.show_add_proverb_dialog,
            width=15
        )
        add_proverb_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(add_proverb_button, "Add a new proverb to the collection")

        generate_button = tk.Button(
            button_frame_top,
            text="Generate",
            command=self.generate_malaphor,
            width=15
        )
        generate_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(generate_button, "Generate a new random malaphor")

        copy_button = tk.Button(
            button_frame_top,
            text="Copy Malaphor",
            command=self.copy_to_clipboard,
            width=15
        )
        copy_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(copy_button, "Copy the current malaphor to clipboard")

        language_label = tk.Label(button_frame_top, text="Language:")
        language_label.pack(side=tk.LEFT, padx=(12, 4))
        self._create_tooltip(language_label, "Limit generation to a specific language when available")
        language_combo = ttk.Combobox(
            button_frame_top,
            textvariable=self.language_var,
            values=["all", "en", "es", "fr", "de"],
            state="readonly",
            width=10,
        )
        language_combo.pack(side=tk.LEFT, padx=5)

        # Add import/export buttons to middle row
        import_button = tk.Button(
            button_frame_middle,
            text="Import Malaphors",
            command=self.import_malaphors_dialog,
            width=15
        )
        import_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(import_button, "Import malaphors from a JSON file")

        export_originals_button = tk.Button(
            button_frame_middle,
            text="Export Originals",
            command=self.export_originals_dialog,
            width=15
        )
        export_originals_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(export_originals_button, "Export original proverbs to a file")

        export_generated_button = tk.Button(
            button_frame_middle,
            text="Export Generated",
            command=self.export_generated_dialog,
            width=15
        )
        export_generated_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(export_generated_button, "Export generated malaphors to a file")

        # Add buttons to bottom row
        favorite_button = tk.Button(
            button_frame_bottom,
            text="Add to Favorites",
            command=self.add_to_favorites,
            width=15
        )
        favorite_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(favorite_button, "Add current malaphor to favorites")

        save_favorites_button = tk.Button(
            button_frame_bottom,
            text="Save Favorites",
            command=self.generator.save_favorites,
            width=15
        )
        save_favorites_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(save_favorites_button, "Save favorites to file")

        undo_button = tk.Button(
            button_frame_bottom,
            text="Undo",
            command=self.undo_last_action,
            width=12
        )
        undo_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(undo_button, "Undo the last destructive action")

        redo_button = tk.Button(
            button_frame_bottom,
            text="Redo",
            command=self.redo_last_action,
            width=12
        )
        redo_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(redo_button, "Redo the last undone action")

        export_image_button = tk.Button(
            button_frame_bottom,
            text="Export Image",
            command=self.export_current_malaphor_image,
            width=15
        )
        export_image_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(export_image_button, "Export the current malaphor as PNG or SVG")

        self.copy_stats_button = tk.Button(
            button_frame_bottom,
            text="Copy Stats",
            command=self.copy_generation_stats,
            width=15,
        )
        self.copy_stats_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(self.copy_stats_button, "Copy the current malaphor with its source metadata in a formatted output")

        self.recent_searches_button = tk.Button(
            button_frame_bottom,
            text="Recent Searches",
            command=self.show_recent_searches,
            width=15,
        )
        self.recent_searches_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(self.recent_searches_button, "Review and rerun recent search queries")

        exit_button = tk.Button(
            button_frame_bottom,
            text="Exit",
            command=self.exit_program,
            width=15
        )
        exit_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(exit_button, "Exit the application")

        view_history_button = tk.Button(
            button_frame_bottom,
            text="Manage History",
            command=self.show_history_dialog,
            width=15
        )
        view_history_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(view_history_button, "View and manage generated malaphor history")

        view_favorites_button = tk.Button(
            button_frame_bottom,
            text="Manage Favorites",
            command=self.show_favorites_dialog,
            width=15
        )
        view_favorites_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(view_favorites_button, "View and manage favorite malaphors")

        # Create new frame for advanced features (Group 2+)
        button_frame_advanced = tk.Frame(main_frame)
        button_frame_advanced.pack(pady=5)

        tag_management_button = tk.Button(
            button_frame_advanced,
            text="Tag Management",
            command=self.show_tag_management_dialog,
            width=15
        )
        tag_management_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(tag_management_button, "View and manage phrase tags (FEAT-4)")

        generate_by_category_button = tk.Button(
            button_frame_advanced,
            text="Generate by Category",
            command=self.show_generate_by_category_dialog,
            width=15
        )
        generate_by_category_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(generate_by_category_button, "Generate malaphors within a specific tag/category")

        statistics_button = tk.Button(
            button_frame_advanced,
            text="Statistics Dashboard",
            command=self.show_statistics_dashboard,
            width=15
        )
        statistics_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(statistics_button, "View statistics and analytics (FEAT-11)")

        gallery_button = tk.Button(
            button_frame_advanced,
            text="Gallery",
            command=self.show_gallery_dialog,
            width=15
        )
        gallery_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(gallery_button, "Browse generated malaphors in a visual gallery (FEAT-16)")

        theme_button = tk.Button(
            button_frame_advanced,
            text="Toggle Theme",
            command=self.toggle_theme,
            width=15
        )
        theme_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(theme_button, "Switch between light and dark themes (UX-6)")

        power_user_button = tk.Button(
            button_frame_advanced,
            text="Power User Tools",
            command=self.show_power_user_tools_dialog,
            width=18
        )
        power_user_button.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(power_user_button, "Advanced generation, sharing, and profile tools")

        # Wrap controls so every action fits in the startup window.
        for frame in (button_frame_top, button_frame_middle, button_frame_bottom, button_frame_advanced):
            for widget in frame.winfo_children():
                widget.pack_forget()
            for index, widget in enumerate(frame.winfo_children()):
                widget.grid(row=index // 4, column=index % 4, padx=5, pady=3)

        # Visible entry point for desktops that export the native menu globally.
        help_row = tk.Frame(main_frame)
        help_row.pack(fill='x')
        tk.Button(help_row, text='Help (F1)', command=lambda: self.assistance.show_help()).pack(side='right')

        # Create labels
        self.sentence_label = tk.Label(
            main_frame,
            text="Click 'Generate' to create a malaphor",
            wraplength=400,
            height=5
        )
        self.sentence_label.pack(pady=20)

        # Create history display
        history_frame = tk.LabelFrame(
            main_frame,
            text="History",
            padx=10,
            pady=10
        )
        history_frame.pack(fill='both', expand=True)

        self.history_text = tk.Text(history_frame, height=10, width=50)
        self.history_text.pack(side=tk.LEFT, fill='both', expand=True)
        self._create_tooltip(self.history_text, "Recently generated malaphors")

        # Add scrollbar to history
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        # Configure scrollbar
        self.history_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_text.yview)
        # Keep first-use guidance visible without filling lists with fake records.
        self.empty_state = tk.Label(main_frame, wraplength=820, justify='left')
        self.empty_state.pack(fill='x', pady=4, before=history_frame)
        self._apply_theme(self.root)

    def _create_tooltip(self, widget, text):
        """Create a tooltip for a given widget."""
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry("+0+0")
        label = tk.Label(
            tooltip,
            text=text,
            background="yellow",
            relief="solid",
            borderwidth=1
        )
        label.pack()
        tooltip.withdraw()

        def enter(event):
            # Buttons and listboxes have no text insertion cursor.
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + widget.winfo_height() + 5
            tooltip.wm_geometry(f"+{x}+{y}")
            tooltip.deiconify()

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

        # Store reference to prevent garbage collection
        self.tooltips.append((widget, tooltip, enter, leave))
        return tooltip

    def _load_ui_preferences(self):
        """Load preferences without letting a malformed file prevent startup."""
        try:
            data = json.loads(self.UI_PREFERENCES_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("theme", "light") not in ("light", "dark"):
                raise ValueError("Expected a light or dark theme preference")
            return data
        except FileNotFoundError:
            pass
        except (OSError, ValueError, TypeError) as exc:
            self.generator._protect_unreadable_file(self.UI_PREFERENCES_FILE, exc)
        return {"theme": "light"}

    def _save_ui_preferences(self):
        self.preferences['theme'] = self.theme_mode
        return self.generator._write_json(self.UI_PREFERENCES_FILE, self.preferences)

    def _theme_palette(self):
        """Return palette values for the active theme."""
        if self.theme_mode == "dark":
            return {
                "bg": "#0f172a",
                "panel": "#111827",
                "fg": "#e5e7eb",
                "muted": "#94a3b8",
                "input_bg": "#1f2937",
                "input_fg": "#f9fafb",
                "button_bg": "#2563eb",
                "button_fg": "#ffffff",
                "accent": "#38bdf8",
                "select_bg": "#1d4ed8",
                "select_fg": "#ffffff",
            }

        return {
            "bg": "#f5f7fb",
            "panel": "#ffffff",
            "fg": "#1f2937",
            "muted": "#4b5563",
            "input_bg": "#ffffff",
            "input_fg": "#111827",
            "button_bg": "#e5e7eb",
            "button_fg": "#111827",
            "accent": "#2563eb",
            "select_bg": "#bfdbfe",
            "select_fg": "#111827",
        }

    def _configure_ttk_style(self):
        """Configure ttk styles for the current theme."""
        palette = self._theme_palette()
        try:
            self.style.theme_use("clam")
            self.style.configure("TNotebook", background=palette["bg"], borderwidth=0)
            self.style.configure("TNotebook.Tab", background=palette["panel"], foreground=palette["fg"], padding=(12, 6))
            self.style.map("TNotebook.Tab", background=[("selected", palette["accent"])], foreground=[("selected", palette["select_fg"])])
            self.style.configure("TCombobox", fieldbackground=palette["input_bg"], foreground=palette["input_fg"], background=palette["panel"])
        except tk.TclError:
            pass

    def _apply_theme(self, widget):
        """Apply the current theme recursively to a widget tree."""
        palette = self._theme_palette()
        self._configure_ttk_style()

        if isinstance(widget, (tk.Tk, tk.Toplevel, tk.Frame, tk.LabelFrame, tk.Canvas)):
            try:
                widget.configure(bg=palette["bg"])
            except tk.TclError:
                pass

        if isinstance(widget, tk.Label):
            try:
                widget.configure(bg=palette["bg"], fg=palette["fg"])
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Button):
            try:
                widget.configure(
                    bg=palette["button_bg"],
                    fg=palette["button_fg"],
                    activebackground=palette["accent"],
                    activeforeground=palette["select_fg"],
                )
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Entry):
            try:
                widget.configure(bg=palette["input_bg"], fg=palette["input_fg"], insertbackground=palette["input_fg"])
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Text):
            try:
                widget.configure(
                    bg=palette["input_bg"],
                    fg=palette["input_fg"],
                    insertbackground=palette["input_fg"],
                    selectbackground=palette["select_bg"],
                    selectforeground=palette["select_fg"],
                )
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Listbox):
            try:
                widget.configure(
                    bg=palette["input_bg"],
                    fg=palette["input_fg"],
                    selectbackground=palette["select_bg"],
                    selectforeground=palette["select_fg"],
                )
            except tk.TclError:
                pass
        elif isinstance(widget, tk.Checkbutton):
            try:
                widget.configure(bg=palette["bg"], fg=palette["fg"], selectcolor=palette["panel"])
            except tk.TclError:
                pass

        for child in widget.winfo_children():
            self._apply_theme(child)

    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self._save_ui_preferences()
        self._apply_theme(self.root)

    def _format_gallery_card_text(self, entry):
        rating = entry.get("rating", 0.0)
        stars = "★" * int(round(rating))
        favorite_mark = "Favorite" if entry.get("is_favorite") else ""
        return (
            f"{entry.get('malaphor', '')}\n\n"
            f"From: {entry.get('source1', '')}\n"
            f"      {entry.get('source2', '')}\n"
            f"Rating: {stars or '—'}\n"
            f"{favorite_mark}\n"
            f"{entry.get('timestamp', '')}"
        )

    def _load_gallery_entry(self, entry, dialog=None):
        """Load a gallery entry into the main display."""
        self.sentence_label.config(
            text=(f"{entry.get('malaphor', '')}\n\n"
                  f"Created from:\n"
                  f"1. {entry.get('source1', '')}\n"
                  f"2. {entry.get('source2', '')}")
        )
        if dialog is not None:
            dialog.lift()

    def show_gallery_dialog(self):
        """Show a visual gallery of generated malaphors (FEAT-16)."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Malaphor Gallery")
        dialog.geometry("960x720")
        dialog.transient(self.root)
        dialog.grab_set()

        controls = tk.Frame(dialog)
        controls.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(controls, text="Sort by:").pack(side=tk.LEFT, padx=(0, 4))
        sort_var = tk.StringVar(value="Recent")
        sort_combo = ttk.Combobox(controls, textvariable=sort_var, values=["Recent", "Rating", "Alphabetical"], state="readonly", width=14)
        sort_combo.pack(side=tk.LEFT, padx=4)

        favorites_only_var = tk.BooleanVar(value=False)
        favorites_only = tk.Checkbutton(controls, text="Favorites only", variable=favorites_only_var)
        favorites_only.pack(side=tk.LEFT, padx=10)

        refresh_button = tk.Button(controls, text="Refresh")
        refresh_button.pack(side=tk.LEFT, padx=4)

        canvas_frame = tk.Frame(dialog)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        gallery_frame = tk.Frame(canvas)
        window_id = canvas.create_window((0, 0), window=gallery_frame, anchor="nw")

        def resize_canvas(event):
            canvas.itemconfigure(window_id, width=event.width)

        canvas.bind("<Configure>", resize_canvas)

        def load_entry(entry):
            self._load_gallery_entry(entry, dialog)

        def render_gallery(*_args):
            for child in gallery_frame.winfo_children():
                child.destroy()

            sort_value = sort_var.get().lower()
            if sort_value == "alphabetical":
                sort_key = "alpha"
            elif sort_value == "rating":
                sort_key = "rating"
            else:
                sort_key = "recent"

            entries = self.generator.get_gallery_entries(
                source="history",
                sort_by=sort_key,
                favorites_only=favorites_only_var.get(),
                limit=60,
            )

            if not entries:
                tk.Label(gallery_frame, text="No malaphors to show yet.").grid(row=0, column=0, padx=20, pady=20)
                return

            for index, entry in enumerate(entries):
                row = index // 2
                column = index % 2
                card = tk.Frame(gallery_frame, bd=1, relief=tk.RIDGE, padx=12, pady=10)
                card.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
                gallery_frame.grid_columnconfigure(column, weight=1)

                tk.Label(card, text=entry.get("malaphor", ""), wraplength=380, justify=tk.LEFT, font=("Arial", 11, "bold")).pack(anchor=tk.W)
                tk.Label(card, text=f"Source 1: {entry.get('source1', '')}", wraplength=380, justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 0))
                tk.Label(card, text=f"Source 2: {entry.get('source2', '')}", wraplength=380, justify=tk.LEFT).pack(anchor=tk.W)
                rating_value = entry.get("rating", 0.0)
                tk.Label(card, text=f"Rating: {'★' * int(round(rating_value)) or '—'}  {'Favorite' if entry.get('is_favorite') else ''}").pack(anchor=tk.W, pady=(6, 0))
                tk.Label(card, text=entry.get("timestamp", ""), fg=self._theme_palette()["muted"]).pack(anchor=tk.W, pady=(2, 8))

                actions = tk.Frame(card)
                actions.pack(anchor=tk.E, fill=tk.X)
                tk.Button(actions, text="Load", command=lambda item=entry: load_entry(item)).pack(side=tk.LEFT, padx=(0, 4))
                tk.Button(
                    actions,
                    text="Copy",
                    command=lambda item=entry: (self.root.clipboard_clear(), self.root.clipboard_append(self._format_gallery_card_text(item)), self.root.update()),
                ).pack(side=tk.LEFT)

        refresh_button.configure(command=render_gallery)
        sort_combo.bind("<<ComboboxSelected>>", render_gallery)
        favorites_only.configure(command=render_gallery)

        render_gallery()
        self._apply_theme(dialog)

    def show_power_user_tools_dialog(self):
        """Show advanced controls for generation templates, constraints, and metadata."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Power User Tools")
        dialog.geometry("920x720")
        dialog.transient(self.root)
        dialog.grab_set()

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        preview_frame = tk.LabelFrame(dialog, text="Preview / Output", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        preview_text = tk.Text(preview_frame, height=10, wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True)

        def set_preview(text):
            preview_text.config(state=tk.NORMAL)
            preview_text.delete("1.0", tk.END)
            preview_text.insert(tk.END, text)
            preview_text.config(state=tk.DISABLED)

        def current_entry():
            return self.generator.history[-1] if self.generator.history else None

        # Generation tab
        generate_frame = tk.Frame(notebook)
        notebook.add(generate_frame, text="Generate")

        constraint_grid = tk.LabelFrame(generate_frame, text="Constraints", padx=10, pady=10)
        constraint_grid.pack(fill=tk.X, padx=5, pady=5)

        fields = ["Min Words", "Max Words", "Min Syllables", "Max Syllables", "Category"]
        entries = {}
        for row, label_text in enumerate(fields):
            tk.Label(constraint_grid, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=4)
            entry = tk.Entry(constraint_grid, width=18)
            entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=4)
            entries[label_text] = entry

        template_options = [template.get("name", "") for template in self.generator.get_generation_templates()]
        tk.Label(constraint_grid, text="Template").grid(row=5, column=0, sticky=tk.W, padx=5, pady=4)
        template_var = tk.StringVar(value=template_options[0] if template_options else "")
        template_combo = ttk.Combobox(constraint_grid, textvariable=template_var, values=template_options, state="readonly", width=26)
        template_combo.grid(row=5, column=1, sticky=tk.W, padx=5, pady=4)

        def parse_int(entry_widget):
            value = entry_widget.get().strip()
            return int(value) if value else None

        def generate_constrained():
            try:
                result = self.generator.generate_with_constraints(
                    min_words=parse_int(entries["Min Words"]),
                    max_words=parse_int(entries["Max Words"]),
                    min_syllables=parse_int(entries["Min Syllables"]),
                    max_syllables=parse_int(entries["Max Syllables"]),
                    category=entries["Category"].get().strip() or None,
                    template_name=template_var.get().strip() or None,
                )
                self.sentence_label.config(
                    text=(f"{result['malaphor']}\n\n"
                          f"Created from:\n"
                          f"1. {result['source1']}\n"
                          f"2. {result['source2']}")
                )
                self.update_history()
                set_preview(self.generator.format_malaphor_with_metadata(
                    result["malaphor"],
                    result["source1"],
                    result["source2"],
                    rating=self.generator.get_pair_rating(result["source1"], result["source2"]),
                    timestamp=result.get("timestamp"),
                    format_type="markdown",
                ))
            except Exception as exc:
                tkinter.messagebox.showerror("Generation Error", str(exc))

        def generate_rhyme():
            try:
                result = self.generator.generate_rhyming_random()
                self.sentence_label.config(
                    text=(f"{result['malaphor']}\n\n"
                          f"Created from:\n"
                          f"1. {result['source1']}\n"
                          f"2. {result['source2']}")
                )
                self.update_history()
                set_preview(self.generator.format_malaphor_with_metadata(
                    result["malaphor"],
                    result["source1"],
                    result["source2"],
                    timestamp=result.get("timestamp"),
                    format_type="plain",
                ))
            except Exception as exc:
                tkinter.messagebox.showerror("Rhyme Error", str(exc))

        action_row = tk.Frame(generate_frame)
        action_row.pack(fill=tk.X, padx=5, pady=10)
        tk.Button(action_row, text="Generate Constrained", command=generate_constrained).pack(side=tk.LEFT, padx=5)
        tk.Button(action_row, text="Generate Rhyming", command=generate_rhyme).pack(side=tk.LEFT, padx=5)

        # Template tab
        template_frame = tk.Frame(notebook)
        notebook.add(template_frame, text="Templates")

        tk.Label(template_frame, text="Name").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        template_name_entry = tk.Entry(template_frame, width=30)
        template_name_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

        tk.Label(template_frame, text="Pattern").grid(row=1, column=0, sticky=tk.W, padx=5, pady=4)
        template_pattern_entry = tk.Entry(template_frame, width=60)
        template_pattern_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=4)
        template_pattern_entry.insert(0, "{source1_beginning} {source2_ending}")

        tk.Label(template_frame, text="Description").grid(row=2, column=0, sticky=tk.W, padx=5, pady=4)
        template_description_entry = tk.Entry(template_frame, width=60)
        template_description_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=4)

        def refresh_templates():
            template_options = [template.get("name", "") for template in self.generator.get_generation_templates()]
            template_combo.configure(values=template_options)
            if template_options:
                template_var.set(template_options[0])

        def save_template():
            if self.generator.save_generation_template(
                template_name_entry.get().strip(),
                template_pattern_entry.get().strip(),
                template_description_entry.get().strip(),
            ):
                refresh_templates()
                set_preview(f"Saved template: {template_name_entry.get().strip()}")
            else:
                tkinter.messagebox.showwarning("Template", "Provide both a template name and pattern.")

        def delete_template():
            name = template_name_entry.get().strip() or template_var.get().strip()
            if self.generator.delete_generation_template(name):
                refresh_templates()
                set_preview(f"Deleted template: {name}")
            else:
                tkinter.messagebox.showwarning("Template", "Template not found.")

        def apply_template():
            name = template_var.get().strip()
            if not name:
                return
            try:
                result = self.generator.generate_from_template(name)
                self.sentence_label.config(
                    text=(f"{result['malaphor']}\n\n"
                          f"Created from:\n"
                          f"1. {result['source1']}\n"
                          f"2. {result['source2']}")
                )
                self.update_history()
                set_preview(self.generator.format_malaphor_with_metadata(
                    result["malaphor"],
                    result["source1"],
                    result["source2"],
                    timestamp=result.get("timestamp"),
                    format_type="json",
                ))
            except Exception as exc:
                tkinter.messagebox.showerror("Template Error", str(exc))

        template_button_row = tk.Frame(template_frame)
        template_button_row.grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        tk.Button(template_button_row, text="Save Template", command=save_template).pack(side=tk.LEFT, padx=5)
        tk.Button(template_button_row, text="Delete Template", command=delete_template).pack(side=tk.LEFT, padx=5)
        tk.Button(template_button_row, text="Generate From Selected", command=apply_template).pack(side=tk.LEFT, padx=5)

        # Share / Compare / Profiles tab
        meta_frame = tk.Frame(notebook)
        notebook.add(meta_frame, text="Share / Profiles")

        format_var = tk.StringVar(value="plain")
        tk.Label(meta_frame, text="Share format").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        format_combo = ttk.Combobox(meta_frame, textvariable=format_var, values=["plain", "markdown", "json", "csv"], state="readonly", width=14)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=4)

        def share_current():
            entry = current_entry()
            if not entry:
                tkinter.messagebox.showwarning("Share", "Generate a malaphor first.")
                return
            text = self.generator.format_malaphor_with_metadata(
                entry.get("malaphor", ""),
                entry.get("source1", ""),
                entry.get("source2", ""),
                rating=self.generator.get_pair_rating(entry.get("source1", ""), entry.get("source2", "")),
                timestamp=entry.get("timestamp"),
                format_type=format_var.get(),
            )
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            set_preview(text)

        def compare_last_two():
            if len(self.generator.history) < 2:
                tkinter.messagebox.showwarning("Compare", "Generate at least two malaphors first.")
                return
            comparison = self.generator.compare_malaphors(self.generator.history[-2:])
            set_preview(json.dumps(comparison, indent=2, ensure_ascii=False))

        tk.Button(meta_frame, text="Copy Current Metadata", command=share_current).grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        tk.Button(meta_frame, text="Compare Last Two", command=compare_last_two).grid(row=1, column=1, sticky=tk.W, padx=5, pady=8)

        tk.Label(meta_frame, text="Profile name").grid(row=2, column=0, sticky=tk.W, padx=5, pady=4)
        profile_name_entry = tk.Entry(meta_frame, width=30)
        profile_name_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=4)

        profile_var = tk.StringVar()
        profile_combo = ttk.Combobox(meta_frame, textvariable=profile_var, values=self.generator.list_settings_profiles(), state="readonly", width=26)
        profile_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=4)
        tk.Label(meta_frame, text="Saved profiles").grid(row=3, column=0, sticky=tk.W, padx=5, pady=4)

        def refresh_profiles():
            profile_combo.configure(values=self.generator.list_settings_profiles())

        def save_profile():
            name = profile_name_entry.get().strip()
            profile = {
                "theme": self.theme_mode,
                "geometry": dialog.geometry(),
                "history_page_size": 25,
            }
            if self.generator.save_settings_profile(name, profile):
                refresh_profiles()
                set_preview(f"Saved profile: {name}")
            else:
                tkinter.messagebox.showwarning("Profiles", "Enter a profile name.")

        def load_profile():
            name = profile_var.get().strip()
            profile = self.generator.load_settings_profile(name)
            if not profile:
                tkinter.messagebox.showwarning("Profiles", "Select a saved profile.")
                return
            self.theme_mode = profile.get("theme", self.theme_mode)
            self._save_ui_preferences()
            self._apply_theme(self.root)
            geometry = profile.get("geometry")
            if geometry:
                dialog.geometry(geometry)
            set_preview(f"Loaded profile: {name}")

        def delete_profile():
            name = profile_var.get().strip()
            if self.generator.delete_settings_profile(name):
                refresh_profiles()
                set_preview(f"Deleted profile: {name}")
            else:
                tkinter.messagebox.showwarning("Profiles", "Select a saved profile.")

        profile_row = tk.Frame(meta_frame)
        profile_row.grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        tk.Button(profile_row, text="Save Profile", command=save_profile).pack(side=tk.LEFT, padx=5)
        tk.Button(profile_row, text="Load Profile", command=load_profile).pack(side=tk.LEFT, padx=5)
        tk.Button(profile_row, text="Delete Profile", command=delete_profile).pack(side=tk.LEFT, padx=5)

        refresh_templates()
        refresh_profiles()
        self._apply_theme(dialog)

    def _cleanup_tooltips(self):
        """Clean up tooltip bindings and references."""
        for widget, tooltip, enter, leave in self.tooltips:
            try:
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")
                tooltip.destroy()
            except tk.TclError:
                pass  # Widget already destroyed
        self.tooltips.clear()

    def show_add_proverb_dialog(self):
        """Show dialog for adding a new proverb."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Add New Proverb")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create and pack widgets
        beginning_label = tk.Label(dialog, text="Enter the beginning of the proverb:")
        beginning_label.pack(pady=5)
        self._create_tooltip(beginning_label, "Enter the first part of the proverb (e.g., 'A bird in the hand')")

        beginning_entry = tk.Entry(dialog, width=40)
        beginning_entry.pack(pady=5)
        self._create_tooltip(beginning_entry, "Enter the first part of the proverb here")

        ending_label = tk.Label(dialog, text="Enter the ending of the proverb:")
        ending_label.pack(pady=5)
        self._create_tooltip(ending_label, "Enter the second part of the proverb (e.g., 'is worth two in the bush')")

        ending_entry = tk.Entry(dialog, width=40)
        ending_entry.pack(pady=5)
        self._create_tooltip(ending_entry, "Enter the second part of the proverb here")

        def save_proverb():
            beginning = beginning_entry.get().strip()
            ending = ending_entry.get().strip()

            if not beginning or not ending:
                tkinter.messagebox.showwarning(
                    "Input Error",
                    "Both beginning and ending must be filled out!"
                )
                return

            if asyncio.run(self.generator.add_new_proverb(beginning, ending)):
                tkinter.messagebox.showinfo(
                    "Success",
                    "New proverb added successfully!"
                )
                self._refresh_assistance_hint()
                dialog.destroy()
            else:
                tkinter.messagebox.showerror("Save failed", "Could not save malaphors.json; the phrase was not added.")

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Save",
            command=save_proverb
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

        return dialog

    def generate_malaphor(self):
        """Generate and display a new malaphor."""
        selected_language = self.language_var.get().strip().lower()
        language = None if selected_language in {"", "all", "any"} else selected_language
        try:
            result = self.generator.generate_malaphor(language=language)
        except (ValueError, OSError) as exc:
            tkinter.messagebox.showerror("Generation failed", str(exc), parent=self.root)
            return
        sentence = result["malaphor"]
        self.sentence_label.config(
            text=(f"{sentence}\n\n"
                  f"Created from:\n"
                  f"1. {result['source1']}\n"
                  f"2. {result['source2']}")
        )
        self.update_history()

    def copy_to_clipboard(self):
        """Copy the current malaphor to clipboard."""
        sentence = self.sentence_label.cget("text")
        self.root.clipboard_clear()
        self.root.clipboard_append(sentence)
        self.root.update()
        tkinter.messagebox.showinfo(
            "Copy Malaphor",
            "The malaphor has been copied to the clipboard."
        )

    def add_to_favorites(self):
        """Add the current malaphor to favorites."""
        current_malaphor = self.sentence_label.cget("text")
        default_text = "Click 'Generate' to create a malaphor"
        if (current_malaphor and current_malaphor != default_text):
            if self.generator.add_to_favorites(current_malaphor) is False:
                tkinter.messagebox.showerror("Save failed", "Could not save favorites.json. Check the destination and permissions.", parent=self.root)
            else:
                self._refresh_assistance_hint()
                tkinter.messagebox.showinfo("Success", "Added to favorites!")

    def _refresh_assistance_hint(self):
        """Keep first-use recommendations aligned with the active collections."""
        if not self.generator.proverbs:
            hint = 'No source phrases yet. Use Add New Proverb or Import Malaphors; Help → Getting Started offers a temporary demo.'
        elif not self.generator.history:
            hint = 'Ready for your first result: choose all languages and click Generate. Help → Guided Tasks walks you through saving it.'
        elif not self.generator.favorites:
            hint = 'Keep a result with Add to Favorites. Find it later in Manage Favorites. Press F1 for help.'
        else:
            hint = 'Tip: Ctrl+Shift+P searches actions. Help → Feature Tour can be replayed at any time.'
        self.empty_state.config(text=hint)

    def update_history(self):
        """Update the history display with malaphors and their sources."""
        self._refresh_assistance_hint()
        # Check if cleanup is needed
        if self.history_text.index('end-1c').split('.')[0] > str(self.HISTORY_CLEANUP_TRIGGER):
            # Keep only the last MAX_HISTORY_LINES lines
            self.history_text.delete('1.0', f'end-{self.MAX_HISTORY_LINES}l')

        # Add new history entry
        self.history_text.delete(1.0, tk.END)
        for item in reversed(self.generator.history[-10:]):
            self.history_text.insert(tk.END, f"Malaphor: {item['malaphor']}\n")
            self.history_text.insert(tk.END, "From combining:\n")
            self.history_text.insert(tk.END, f"1. {item['source1']}\n")
            self.history_text.insert(tk.END, f"2. {item['source2']}\n\n")

    def exit_program(self):
        """Exit the program after confirming with the user."""
        if tkinter.messagebox.askokcancel(
            "Exit",
            "Do you want to exit the program?"
        ):
            self.root.quit()

    def import_malaphors_dialog(self):
        """Show dialog for importing malaphors from a JSON file."""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filepath:
            imported = asyncio.run(self.generator.import_malaphors(filepath))
            error = getattr(self.generator, "last_import_error", None)
            if imported:
                self._refresh_assistance_hint()
                tkinter.messagebox.showinfo("Import complete", "New phrases imported.", parent=self.root)
            elif error:
                tkinter.messagebox.showerror("Import failed", error, parent=self.root)
            else:
                tkinter.messagebox.showinfo("Import complete", "No new phrases to import.", parent=self.root)

    def _export_file(self, operation, filepath):
        """Report the result of a desktop export."""
        if asyncio.run(operation):
            tkinter.messagebox.showinfo("Export complete", f"Saved to {filepath}", parent=self.root)
        else:
            tkinter.messagebox.showerror(
                "Export failed", f"Could not write {filepath}. Check the destination and permissions.",
                parent=self.root,
            )

    def export_originals_dialog(self):
        """Show dialog for exporting original malaphors."""
        from tkinter import filedialog

        filetypes = [
            ("JSON files", "*.json"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=filetypes,
            initialfile="original_malaphors"
        )

        if filepath:
            if filepath.endswith('.txt'):
                self._export_file(self.generator.export_malaphors_as_text(filepath), filepath)
            else:
                self._export_file(self.generator.export_malaphors(filepath), filepath)

    def export_generated_dialog(self):
        """Show dialog for exporting generated malaphors."""
        from tkinter import filedialog

        filetypes = [
            ("JSON files", "*.json"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=filetypes,
            initialfile="generated_malaphors"
        )

        if filepath:
            if filepath.endswith('.txt'):
                self._export_file(self.generator.export_history_as_text(filepath), filepath)
            else:
                self._export_file(self.generator.export_history(filepath), filepath)

    def export_favorites_dialog(self):
        """Show dialog for exporting favorites."""
        from tkinter import filedialog

        filetypes = [
            ("JSON files", "*.json"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=filetypes,
            initialfile="favorite_malaphors"
        )

        if filepath:
            if filepath.endswith('.txt'):
                self._export_file(self.generator.export_favorites_as_text(filepath), filepath)
            else:
                self._export_file(self.generator.export_favorites(filepath), filepath)

    def show_manage_phrases_dialog(self):
        """Show dialog for managing (viewing/editing/deleting) phrases."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Manage Phrases")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create frames
        list_frame = tk.Frame(dialog)
        list_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)

        edit_frame = tk.Frame(dialog)
        edit_frame.pack(side=tk.RIGHT, fill='y', padx=10, pady=10)

        # Create listbox with scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        phrases_listbox = tk.Listbox(list_frame, width=60, height=20, yscrollcommand=scrollbar.set)
        phrases_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=phrases_listbox.yview)
        self._create_tooltip(phrases_listbox, "List of all available proverbs. Click one to edit.")

        # Populate listbox
        proverbs = self.generator.get_all_proverbs()
        def refresh_phrase_listbox(selected_index=None):
            phrases_listbox.delete(0, tk.END)
            for proverb in proverbs:
                phrases_listbox.insert(tk.END, proverb["original"])
            if selected_index is not None and 0 <= selected_index < phrases_listbox.size():
                phrases_listbox.selection_clear(0, tk.END)
                phrases_listbox.selection_set(selected_index)

        refresh_phrase_listbox()

        drag_state = {"index": None}

        def on_drag_start(event):
            drag_state["index"] = phrases_listbox.nearest(event.y)

        def on_drag_motion(event):
            start_index = drag_state["index"]
            if start_index is None:
                return
            target_index = phrases_listbox.nearest(event.y)
            if target_index == start_index:
                return
            if self.generator.move_proverb(start_index, target_index):
                proverbs[:] = self.generator.get_all_proverbs()
                refresh_phrase_listbox(target_index)
                drag_state["index"] = target_index

        phrases_listbox.bind("<ButtonPress-1>", on_drag_start)
        phrases_listbox.bind("<B1-Motion>", on_drag_motion)

        # Create edit fields
        beginning_label = tk.Label(edit_frame, text="Beginning:")
        beginning_label.pack(pady=5)
        self._create_tooltip(beginning_label, "Edit the first part of the selected proverb")

        beginning_entry = tk.Entry(edit_frame, width=40)
        beginning_entry.pack(pady=5)
        self._create_tooltip(beginning_entry, "Enter the first part of the proverb here")

        ending_label = tk.Label(edit_frame, text="Ending:")
        ending_label.pack(pady=5)
        self._create_tooltip(ending_label, "Edit the second part of the selected proverb")

        ending_entry = tk.Entry(edit_frame, width=40)
        ending_entry.pack(pady=5)
        self._create_tooltip(ending_entry, "Enter the second part of the proverb here")

        def on_select(event):
            try:
                index = phrases_listbox.curselection()[0]
                proverb = proverbs[index]
                beginning_entry.delete(0, tk.END)
                beginning_entry.insert(0, proverb["beginning"])
                ending_entry.delete(0, tk.END)
                ending_entry.insert(0, proverb["ending"])
            except IndexError:
                pass

        phrases_listbox.bind('<<ListboxSelect>>', on_select)

        def save_changes():
            try:
                index = phrases_listbox.curselection()[0]
                beginning = beginning_entry.get().strip()
                ending = ending_entry.get().strip()

                if not beginning or not ending:
                    tkinter.messagebox.showwarning(
                        "Input Error",
                        "Both beginning and ending must be filled out!"
                    )
                    return

                if asyncio.run(self.generator.edit_proverb(index, beginning, ending)):
                    # Update listbox
                    phrases_listbox.delete(index)
                    phrases_listbox.insert(index, f"{beginning} {ending}")
                    tkinter.messagebox.showinfo(
                        "Success",
                        "Phrase updated successfully!"
                    )
                    proverbs[:] = self.generator.proverbs
                else:
                    tkinter.messagebox.showerror("Save failed", "Could not save malaphors.json; the phrase was kept.")
            except IndexError:
                tkinter.messagebox.showwarning(
                    "Selection Error",
                    "Please select a phrase to edit!"
                )

        def delete_phrase():
            try:
                index = phrases_listbox.curselection()[0]
                if tkinter.messagebox.askyesno(
                    "Confirm Delete",
                    "Are you sure you want to delete this phrase?"
                ):
                    if asyncio.run(self.generator.delete_proverb(index)):
                        phrases_listbox.delete(index)
                        beginning_entry.delete(0, tk.END)
                        ending_entry.delete(0, tk.END)
                        tkinter.messagebox.showinfo(
                            "Success",
                            "Phrase deleted successfully!"
                        )
                        proverbs[:] = self.generator.proverbs
                    else:
                        tkinter.messagebox.showerror("Save failed", "Could not save malaphors.json; the phrase was kept.")
            except IndexError:
                tkinter.messagebox.showwarning(
                    "Selection Error",
                    "Please select a phrase to delete!"
                )

        # Add buttons
        button_frame = tk.Frame(edit_frame)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Delete",
            command=delete_phrase
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

        return dialog

    def show_manual_combine_dialog(self):
        """Show dialog for manually selecting phrases to combine."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Manual Phrase Combination")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create frames for the two listboxes
        left_frame = tk.LabelFrame(dialog, text="First Phrase")
        left_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)

        right_frame = tk.LabelFrame(dialog, text="Second Phrase")
        right_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)

        # Create search entries
        left_search = tk.Entry(left_frame, textvariable=tk.StringVar())
        left_search.pack(fill='x', padx=5, pady=5)
        self._create_tooltip(left_search, "Search for phrases in the left list")

        right_search = tk.Entry(right_frame, textvariable=tk.StringVar())
        right_search.pack(fill='x', padx=5, pady=5)
        self._create_tooltip(right_search, "Search for phrases in the right list")

        # Create listboxes with scrollbars
        left_scrollbar = tk.Scrollbar(left_frame)
        left_scrollbar.pack(side=tk.RIGHT, fill='y')
        left_listbox = tk.Listbox(left_frame, yscrollcommand=left_scrollbar.set)
        left_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        left_scrollbar.config(command=left_listbox.yview)
        self._create_tooltip(left_listbox, "Select the first phrase to combine")

        right_scrollbar = tk.Scrollbar(right_frame)
        right_scrollbar.pack(side=tk.RIGHT, fill='y')
        right_listbox = tk.Listbox(right_frame, yscrollcommand=right_scrollbar.set)
        right_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        right_scrollbar.config(command=right_listbox.yview)
        self._create_tooltip(right_listbox, "Select the second phrase to combine")

        # Populate listboxes
        proverbs = self.generator.get_all_proverbs()
        for i, proverb in enumerate(proverbs):
            left_listbox.insert(tk.END, proverb["original"])
            right_listbox.insert(tk.END, proverb["original"])

        def update_listbox(listbox, search_var, event=None):
            """Filter listbox based on search text."""
            search_text = search_var.get().lower()
            listbox.delete(0, tk.END)
            for proverb in proverbs:
                if search_text in proverb["original"].lower():
                    listbox.insert(tk.END, proverb["original"])

        # Bind search entries to update function
        left_search_var = tk.StringVar()
        left_search_var.trace('w', lambda *args: update_listbox(left_listbox, left_search_var))
        right_search_var = tk.StringVar()
        right_search_var.trace('w', lambda *args: update_listbox(right_listbox, right_search_var))

        def combine_selected():
            """Generate malaphor from selected phrases."""
            try:
                left_sel = left_listbox.curselection()[0]
                right_sel = right_listbox.curselection()[0]

                # Convert listbox indices to proverb indices
                left_text = left_listbox.get(left_sel)
                right_text = right_listbox.get(right_sel)

                left_index = next(i for i, p in enumerate(proverbs) if p["original"] == left_text)
                right_index = next(i for i, p in enumerate(proverbs) if p["original"] == right_text)

                result = self.generator.generate_malaphor(left_index, right_index)
                self.sentence_label.config(
                    text=(f"{result['malaphor']}\n\n"
                          f"Created from:\n"
                          f"1. {result['source1']}\n"
                          f"2. {result['source2']}")
                )
                self.update_history()
                dialog.destroy()

            except IndexError:
                tkinter.messagebox.showwarning(
                    "Selection Error",
                    "Please select both a first and second phrase!"
                )

        # Add combine button
        button_frame = tk.Frame(dialog)
        button_frame.pack(side=tk.BOTTOM, fill='x', pady=10)

        tk.Button(
            button_frame,
            text="Combine Selected",
            command=combine_selected
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

    def show_history_dialog(self):
        """Show dialog for managing history entries."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Manage History")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create search frame
        search_frame = tk.Frame(dialog)
        search_frame.pack(fill='x', padx=10, pady=5)

        search_label = tk.Label(search_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(search_label, "Search through your generated malaphors")

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(search_entry, "Type to filter malaphors")

        page_state = {"page": 1}
        page_size = 25
        current_items = []

        # Create listbox with scrollbar
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        history_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=history_listbox.yview)
        self._create_tooltip(history_listbox, "List of generated malaphors. Click one to manage.")

        page_label = tk.Label(dialog, text="Page 1")
        page_label.pack(pady=(0, 5))

        def paged_items(search_text=''):
            if search_text:
                items = self.generator.search_history(search_text)
            else:
                items = list(enumerate(self.generator.history))

            total_pages = max(1, (len(items) + page_size - 1) // page_size)
            page_state["page"] = min(page_state["page"], total_pages)
            start_index = (page_state["page"] - 1) * page_size
            end_index = start_index + page_size
            return items[start_index:end_index], total_pages

        empty_hint = tk.Label(dialog, wraplength=740)
        empty_hint.pack(pady=4)
        tk.Button(dialog, text='Help with History', command=lambda: self.assistance.show_help('search', parent=dialog)).pack(pady=2)

        def update_history_list(search_text=''):
            nonlocal current_items
            history_listbox.delete(0, tk.END)
            current_items, total_pages = paged_items(search_text)
            page_label.config(text=f"Page {page_state['page']} of {total_pages}")
            empty_hint.config(text='' if current_items else 'No matching history. Clear the search, or close this window and click Generate to create your first result.')

            for _, item in current_items:
                timestamp = item.get('timestamp', '')[:10]
                history_listbox.insert(
                    tk.END,
                    f"{item['malaphor']} | {item['source1']} + {item['source2']} | {timestamp}"
                )

        def on_search(*args):
            page_state["page"] = 1
            update_history_list(search_var.get())

        search_var.trace('w', on_search)

        def delete_selected():
            try:
                sel = history_listbox.curselection()
                if sel:
                    index = current_items[sel[0]][0]
                    if tkinter.messagebox.askyesno(
                        "Confirm Delete",
                        "Are you sure you want to delete this entry?"
                    ):
                        if not self.generator.delete_from_history(index):
                            raise OSError("Could not save history.json; the entry was kept.")
                        update_history_list(search_var.get())
            except Exception as e:
                tkinter.messagebox.showerror(
                    "Error",
                    f"Could not delete entry: {str(e)}"
                )

        def previous_page():
            if page_state["page"] > 1:
                page_state["page"] -= 1
                update_history_list(search_var.get())

        def next_page():
            _, total_pages = paged_items(search_var.get())
            if page_state["page"] < total_pages:
                page_state["page"] += 1
                update_history_list(search_var.get())

        # Add buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Previous",
            command=previous_page
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Next",
            command=next_page
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Delete Selected",
            command=delete_selected
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

        # Initial population
        update_history_list()

        return dialog

    def show_favorites_dialog(self):
        """Show dialog for managing favorite entries."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Manage Favorites")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create search frame
        search_frame = tk.Frame(dialog)
        search_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        self._create_tooltip(search_entry, "Type to filter favorites")

        # Create listbox with scrollbar
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')

        favorites_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        favorites_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=favorites_listbox.yview)
        self._create_tooltip(favorites_listbox, "List of favorite malaphors. Click one to manage.")

        visible_indices = []

        empty_hint = tk.Label(dialog, wraplength=740)
        empty_hint.pack(pady=4)
        tk.Button(dialog, text='Help with Favorites', command=lambda: self.assistance.show_help('generate', parent=dialog)).pack(pady=2)

        def update_favorites_list(search_text=''):
            empty_hint.config(text='' if self.generator.favorites else 'No favorites yet. Close this window, generate a result and click Add to Favorites.')
            favorites_listbox.delete(0, tk.END)
            visible_indices.clear()
            if search_text:
                items = self.generator.search_favorites(search_text)
                for i, item in items:
                    visible_indices.append(i)
                    favorites_listbox.insert(tk.END, item)
            else:
                for i, item in enumerate(self.generator.favorites):
                    visible_indices.append(i)
                    favorites_listbox.insert(tk.END, item)
            if search_text and not visible_indices:
                empty_hint.config(text='No matching favorites. Clear the search or try a shorter term.')

        def on_search(*args):
            update_favorites_list(search_var.get())

        search_var.trace('w', on_search)

        def delete_selected():
            try:
                sel = favorites_listbox.curselection()
                if sel:
                    index = visible_indices[sel[0]]
                    if tkinter.messagebox.askyesno(
                        "Confirm Delete",
                        "Are you sure you want to delete this favorite?"
                    ):
                        if not self.generator.delete_from_favorites(index):
                            raise OSError("Could not save favorites.json; the favorite was kept.")
                        update_favorites_list(search_var.get())
            except Exception as e:
                tkinter.messagebox.showerror(
                    "Error",
                    f"Could not delete favorite: {str(e)}"
                )

        # Add buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Delete Selected",
            command=delete_selected
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Close",
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(button_frame, text="Export Favorites",
                  command=self.export_favorites_dialog).pack(side=tk.LEFT, padx=5)

        # Initial population
        update_favorites_list()
        return dialog

    # ========== PHASE 2: POLISH & EXPLORATION UI FEATURES ==========

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions (UX-5)."""
        self.root.bind('<Control-g>', lambda e: self.generate_malaphor())
        self.root.bind('<Control-c>', self._copy_shortcut)
        self.root.bind('<Control-h>', lambda e: self.show_history_dialog())
        self.root.bind('<Control-f>', lambda e: self.focus_search_box())
        self.root.bind('<Control-s>', lambda e: self.add_to_favorites())
        self.root.bind('<Control-z>', lambda e: self.undo_last_action())
        self.root.bind('<Control-Y>', lambda e: self.redo_last_action())
        self.root.bind('<Control-Shift-Z>', lambda e: self.redo_last_action())

    def _copy_shortcut(self, event):
        if isinstance(event.widget, (tk.Text, tk.Entry, ttk.Entry, ttk.Combobox)):
            return None
        self.copy_to_clipboard()
        return 'break'

    def focus_search_box(self):
        """Open source search and focus its first entry."""
        self.show_manual_combine_dialog()
        dialog = self.root.winfo_children()[-1]
        def focus(widget):
            for child in widget.winfo_children():
                if isinstance(child, (tk.Entry, ttk.Entry)):
                    child.focus_set()
                    return True
                if focus(child):
                    return True
            return False
        focus(dialog)

    def undo_last_action(self):
        """Undo the most recent destructive action."""
        if self.generator.undo_last_action():
            self.update_history()
            tkinter.messagebox.showinfo("Undo", "Last action restored.")
        else:
            tkinter.messagebox.showwarning("Undo", "Could not save the restored data." if self.generator.undo_stack.can_undo() else "Nothing to undo.")

    def redo_last_action(self):
        """Redo the most recent undone action."""
        if self.generator.redo_last_action():
            self.update_history()
            tkinter.messagebox.showinfo("Redo", "Action restored.")
        else:
            tkinter.messagebox.showwarning("Redo", "Could not save the restored data." if self.generator.undo_stack.can_redo() else "Nothing to redo.")

    def export_current_malaphor_image(self):
        """Export the current malaphor as a PNG or SVG image."""
        current_text = self.sentence_label.cget("text")
        if not current_text or current_text == "Click 'Generate' to create a malaphor":
            tkinter.messagebox.showwarning("No Malaphor", "Generate a malaphor first.")
            return

        sourced = self.generator.history[-1] if self.generator.history else {"malaphor": current_text.split("\n", 1)[0], "source1": "", "source2": ""}
        malaphor = sourced.get("malaphor", current_text.split("\n", 1)[0])
        source1 = sourced.get("source1", "")
        source2 = sourced.get("source2", "")

        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg"), ("All files", "*.*")],
            initialfile="malaphor_export"
        )
        if not file_path:
            return

        fmt = "png" if file_path.lower().endswith(".png") else "svg"
        success = self.generator.export_malaphor_image(malaphor, source1, source2, file_path, image_format=fmt)
        if success:
            tkinter.messagebox.showinfo("Export Complete", f"Image saved to:\n{file_path}")
        else:
            tkinter.messagebox.showerror("Export Failed", "Could not export the malaphor image.")

    # UX-9: Copy Generation Stats (formatted text)
    def copy_generation_stats(self):
        """Copy malaphor with sources in formatted way (UX-9)."""
        current_text = self.sentence_label.cget("text")
        if not current_text or current_text == "Click 'Generate' to create a malaphor":
            tkinter.messagebox.showwarning("No Malaphor", "Generate a malaphor first!")
            return

        # Parse the current display to extract components
        lines = current_text.split('\n')
        if len(lines) >= 3:
            malaphor = lines[0]
            # Find source phrases in history
            if self.generator.history:
                last_item = self.generator.history[-1]
                source1 = last_item.get('source1', '')
                source2 = last_item.get('source2', '')

                # Show format selection dialog
                dialog = tk.Toplevel(self.root)
                dialog.bind('<F1>', self.assistance.context_help)
                dialog.title("Copy Format")
                dialog.geometry("400x200")
                dialog.transient(self.root)
                dialog.grab_set()

                tk.Label(dialog, text="Select format:").pack(pady=10)

                format_var = tk.StringVar(value="plain")
                tk.Radiobutton(dialog, text="Plain Text", variable=format_var, value="plain").pack(anchor=tk.W, padx=50)
                tk.Radiobutton(dialog, text="Markdown", variable=format_var, value="markdown").pack(anchor=tk.W, padx=50)
                tk.Radiobutton(dialog, text="JSON", variable=format_var, value="json").pack(anchor=tk.W, padx=50)

                def copy_in_format():
                    formatted = self.generator.format_malaphor_for_copy(malaphor, source1, source2, format_var.get())
                    self.root.clipboard_clear()
                    self.root.clipboard_append(formatted)
                    self.root.update()
                    tkinter.messagebox.showinfo("Copied", f"Malaphor copied in {format_var.get()} format!")
                    dialog.destroy()

                tk.Button(dialog, text="Copy", command=copy_in_format).pack(pady=10)

    # UX-10: Recent Searches Dropdown
    def show_recent_searches(self):
        """Show dropdown menu of recent searches (UX-10)."""
        recent = self.generator.get_recent_searches()
        if not recent:
            tkinter.messagebox.showinfo("No Searches", "No recent searches yet!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Recent Searches")
        dialog.geometry("300x300")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Click to rerun:").pack(pady=10)

        listbox = tk.Listbox(dialog)
        listbox.pack(fill='both', expand=True, padx=10, pady=10)

        for search in recent:
            listbox.insert(tk.END, search)

        def rerun_search():
            try:
                idx = listbox.curselection()[0]
                query = listbox.get(idx)
                results = self.generator.search(query)
                self.generator.add_recent_search(query)
                # Display results (simplified - just show count)
                tkinter.messagebox.showinfo("Results", f"Found {len(results)} phrase(s) matching '{query}'")
                dialog.destroy()
            except IndexError:
                tkinter.messagebox.showwarning("Selection", "Select a search to rerun!")

        def clear_history():
            if tkinter.messagebox.askyesno("Clear", "Clear all recent searches?"):
                self.generator.clear_recent_searches()
                dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Rerun", command=rerun_search).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear All", command=clear_history).pack(side=tk.LEFT, padx=5)

    # FEAT-2: Generate N Suggestions
    def show_suggestions_dialog(self):
        """Show dialog with multiple suggestions for user to select from (FEAT-2)."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Generate Multiple Suggestions")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Controls frame
        controls = tk.Frame(dialog)
        controls.pack(fill='x', padx=10, pady=10)

        tk.Label(controls, text="Number of suggestions:").pack(side=tk.LEFT, padx=5)
        count_var = tk.IntVar(value=5)
        count_spin = tk.Spinbox(controls, from_=1, to=20, textvariable=count_var, width=5)
        count_spin.pack(side=tk.LEFT, padx=5)

        suggestions_listbox = tk.Listbox(dialog, height=15)
        suggestions_listbox.pack(fill='both', expand=True, padx=10, pady=5)

        def generate_suggestions():
            try:
                count = count_var.get()
                suggestions = self.generator.generate_multiple(count)
                suggestions_listbox.delete(0, tk.END)

                for i, sugg in enumerate(suggestions, 1):
                    suggestions_listbox.insert(tk.END, f"{i}. {sugg['malaphor']}")
                    suggestions_listbox.insert(tk.END, f"   From: {sugg['source1']} + {sugg['source2']}")
                    suggestions_listbox.insert(tk.END, '')
            except ValueError as e:
                tkinter.messagebox.showerror("Error", str(e))

        def select_suggestion():
            try:
                selections = suggestions_listbox.curselection()
                if selections:
                    line = suggestions_listbox.get(selections[0])
                    # Extract malaphor from line
                    if line.startswith(tuple(str(i) for i in range(1, 21))):
                        malaphor = line.split('. ', 1)[1]
                        # Find the full suggestion
                        for sugg in self.generator.history[-10:]:
                            if sugg['malaphor'] == malaphor:
                                self.sentence_label.config(
                                    text=(f"{sugg['malaphor']}\n\n"
                                          f"Created from:\n"
                                          f"1. {sugg['source1']}\n"
                                          f"2. {sugg['source2']}")
                                )
                                self.update_history()
                                dialog.destroy()
                                return
            except IndexError:
                pass

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Generate", command=generate_suggestions).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Select & Use", command=select_suggestion).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Generate initial suggestions
        generate_suggestions()

    # FEAT-7: Phrase Similarity Detection (Warning before adding)
    def check_phrase_similarity_and_add(self, beginning: str, ending: str, original: str = None):
        """Check for similar phrases before adding and warn user (FEAT-7)."""
        if original is None:
            original = f"{beginning} {ending}"

        similar = self.generator.detect_similar_phrases(original)
        if similar:
            dialog = tk.Toplevel(self.root)
            dialog.bind('<F1>', self.assistance.context_help)
            dialog.title("Similar Phrase Warning")
            dialog.geometry("500x300")
            dialog.transient(self.root)
            dialog.grab_set()

            msg = f"This phrase is {(similar[0][1]*100):.0f}% similar to:\n\n"
            for proverb, score in similar[:3]:
                msg += f"• {proverb['original']} ({score*100:.0f}%)\n"
            msg += "\nDo you want to add it anyway?"

            tk.Label(dialog, text=msg, wraplength=400).pack(padx=10, pady=10)

            def add_anyway():
                asyncio.run(self.generator.add_new_proverb(beginning, ending))
                dialog.destroy()

            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=10)
            tk.Button(button_frame, text="Add Anyway", command=add_anyway).pack(side=tk.LEFT, padx=5)
            tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        else:
            asyncio.run(self.generator.add_new_proverb(beginning, ending))
            tkinter.messagebox.showinfo("Success", "Phrase added successfully!")

    # FEAT-8: Batch Phrase Import with Auto-Splitting
    def show_batch_import_dialog(self):
        """Show dialog for batch importing phrases with auto-split preview (FEAT-8)."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Batch Import Phrases")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        dialog.grab_set()

        # Input frame
        input_frame = tk.LabelFrame(dialog, text="Enter phrases (one per line):")
        input_frame.pack(fill='both', expand=True, padx=10, pady=10)

        input_text = tk.Text(input_frame, height=10, width=80)
        input_text.pack(fill='both', expand=True, side=tk.LEFT)

        scrollbar = tk.Scrollbar(input_frame)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        input_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=input_text.yview)

        # Preview frame
        preview_frame = tk.LabelFrame(dialog, text="Preview (auto-split):")
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)

        preview_tree_frame = tk.Frame(preview_frame)
        preview_tree_frame.pack(fill='both', expand=True)

        # Create table-like display
        preview_text = tk.Text(preview_tree_frame, height=10, width=80)
        preview_text.pack(fill='both', expand=True, side=tk.LEFT)
        preview_text.config(state=tk.DISABLED)

        preview_scroll = tk.Scrollbar(preview_tree_frame)
        preview_scroll.pack(side=tk.RIGHT, fill='y')
        preview_text.config(yscrollcommand=preview_scroll.set)
        preview_scroll.config(command=preview_text.yview)

        def update_preview(*args):
            text_content = input_text.get("1.0", tk.END).strip()
            if text_content:
                phrases = self.generator.parse_batch_phrases(text_content)
                preview_text.config(state=tk.NORMAL)
                preview_text.delete("1.0", tk.END)
                preview_text.insert(tk.END, "Original | Beginning | Ending\n")
                preview_text.insert(tk.END, "-" * 80 + "\n")

                for original, beginning, ending in phrases:
                    preview_text.insert(tk.END, f"{original}\n  -> {beginning} | {ending}\n\n")

                preview_text.config(state=tk.DISABLED)

        input_text.bind("<<Change>>", update_preview)
        # Also update on key release
        input_text.bind("<KeyRelease>", update_preview)

        def import_phrases():
            text_content = input_text.get("1.0", tk.END).strip()
            if not text_content:
                tkinter.messagebox.showwarning("Empty", "Please enter some phrases!")
                return

            phrases = self.generator.parse_batch_phrases(text_content)
            imported, duplicates = asyncio.run(self.generator.import_batch_phrases(phrases))

            result_msg = f"Imported: {imported}\nDuplicates skipped: {duplicates}"
            tkinter.messagebox.showinfo("Import Complete", result_msg)
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Import", command=import_phrases).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        update_preview()

    # FEAT-3: Weighted Generation Mode Toggle
    def show_weighted_generation_dialog(self):
        """Show dialog for weighted generation (based on ratings)."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Smart Generation (Weighted by Ratings)")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Generate using ratings data?", font=("Arial", 12)).pack(pady=20)

        mode_var = tk.StringVar(value="smart")
        tk.Radiobutton(dialog, text="Smart Mode (weighted by ratings)", variable=mode_var, value="smart").pack(anchor=tk.W, padx=50)
        tk.Radiobutton(dialog, text="Random Mode (no weighting)", variable=mode_var, value="random").pack(anchor=tk.W, padx=50)

        def generate_smart():
            result = self.generator.generate_weighted_random(smart_mode=(mode_var.get() == "smart"))
            self.sentence_label.config(
                text=(f"{result['malaphor']}\n\n"
                      f"Created from:\n"
                      f"1. {result['source1']}\n"
                      f"2. {result['source2']}")
            )
            self.update_history()
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="Generate", command=generate_smart).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def run(self):
        """Start the application."""
        self.setup_keyboard_shortcuts()
        if not self.preferences.get('onboarding_complete') and not self.generator.load_errors:
            self._welcome_after = self.root.after(100, self.assistance.welcome)
        try:
            self.root.mainloop()
        finally:
            self.close()

    def close(self):
        """Clean up resources."""
        try:
            self.generator.stop_auto_save()
            self.generator._run_auto_save()
        except Exception:
            pass
        if hasattr(self, '_welcome_after'):
            self.root.after_cancel(self._welcome_after)
        self.assistance.close()
        self._cleanup_tooltips()
        for dialog in self.dialogs.values():
            try:
                dialog.destroy()
            except tk.TclError:
                pass  # Dialog already destroyed
        if hasattr(self, 'root') and self.root:
            self.root.quit()

    # ============================================================================
    # DATA-2: Source/Attribution UI Methods
    # ============================================================================

    def show_source_management_dialog(self):
        """Show dialog for managing phrase sources."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Manage Phrase Sources - maliphors-inator")
        dialog.geometry("700x500")

        # Preset sources
        preset_sources = [
            "Shakespeare", "Folk Wisdom", "Modern", "Historical",
            "Aesop's Fables", "Proverbs", "Literature", "Science",
            "Business", "Unknown"
        ]

        # Title
        title_frame = tk.Frame(dialog)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(title_frame, text="Manage Phrase Sources", font=("Arial", 12, "bold")).pack()

        # Filter by current source
        filter_frame = tk.Frame(dialog)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(filter_frame, text="Filter by source:").pack(side=tk.LEFT)

        source_var = tk.StringVar()
        source_combo = ttk.Combobox(filter_frame, textvariable=source_var,
                                    values=list(self.generator.get_all_sources()) + ["All"],
                                    state="readonly", width=30)
        source_combo.pack(side=tk.LEFT, padx=5)
        source_combo.set("All")

        # Phrase list with source selector
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Canvas with scrollbar
        canvas = tk.Canvas(list_frame, height=300)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def update_list(*args):
            # Clear existing widgets
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            filter_value = source_var.get()
            phrases = self.generator.proverbs if filter_value == "All" else self.generator.get_phrases_by_source(filter_value)

            for idx, phrase in enumerate(phrases):
                phrase_frame = tk.Frame(scrollable_frame, relief=tk.SUNKEN, borderwidth=1)
                phrase_frame.pack(fill=tk.X, pady=5)

                # Phrase text
                original = phrase.get("original", "Unknown")[:50] + "..." if len(phrase.get("original", "")) > 50 else phrase.get("original", "Unknown")
                tk.Label(phrase_frame, text=original, font=("Arial", 9)).pack(side=tk.LEFT, padx=5, pady=3)

                # Source selector
                current_source = phrase.get("source", "Unknown")
                source_combo_inner = ttk.Combobox(phrase_frame, values=preset_sources,
                                                   width=20, state="readonly")
                source_combo_inner.set(current_source)
                source_combo_inner.pack(side=tk.LEFT, padx=5, pady=3)

                # Set callback
                def on_source_change(idx=idx, combo=source_combo_inner):
                    new_source = combo.get()
                    self.generator.set_phrase_source(idx, new_source)

                source_combo_inner.bind("<<ComboboxSelected>>", lambda e, cb=source_combo_inner, i=idx: on_source_change(i, cb))

        source_combo.bind("<<ComboboxSelected>>", update_list)

        # Initial population
        update_list()

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Save button
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        async def save_sources():
            try:
                await self.generator._save_to_file("malaphors.json", {"proverbs": self.generator.proverbs})
                tk.messagebox.showinfo("Success", "Sources saved successfully!")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to save sources: {str(e)}")

        def save_sync():
            asyncio.run(save_sources())

        tk.Button(button_frame, text="Save Sources", command=save_sync, bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    # ============================================================================
    # DATA-4: Database Validation & Deduplication UI Methods
    # ============================================================================

    def show_database_validation_dialog(self):
        """Show dialog for database validation and deduplication."""
        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Validate & Clean Database - maliphors-inator")
        dialog.geometry("800x600")

        # Title
        title_frame = tk.Frame(dialog)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(title_frame, text="Database Validation & Cleanup", font=("Arial", 12, "bold")).pack()

        # Options
        options_frame = tk.LabelFrame(dialog, text="Cleanup Options", padx=10, pady=10)
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        remove_invalid_var = tk.BooleanVar(value=True)
        remove_duplicates_var = tk.BooleanVar(value=True)

        tk.Checkbutton(options_frame, text="Remove phrases with missing required fields",
                      variable=remove_invalid_var).pack(anchor=tk.W)
        tk.Checkbutton(options_frame, text="Remove exact duplicate phrases",
                      variable=remove_duplicates_var).pack(anchor=tk.W)

        # Results text area
        results_frame = tk.LabelFrame(dialog, text="Validation Report", padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        results_text = tk.Text(results_frame, height=15, width=80, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_text.yview)
        results_text.configure(yscrollcommand=scrollbar.set)

        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        async def run_validation():
            results_text.config(state=tk.NORMAL)
            results_text.delete(1.0, tk.END)

            try:
                # Run validation
                validation = self.generator.validate_schema()
                results_text.insert(tk.END, "=== VALIDATION REPORT ===\n\n")
                results_text.insert(tk.END, f"Total phrases: {validation['total_phrases']}\n")
                results_text.insert(tk.END, f"Valid phrases: {validation['valid']}\n")
                results_text.insert(tk.END, f"Invalid phrases: {len(validation['invalid'])}\n\n")

                if validation["invalid"]:
                    results_text.insert(tk.END, "Invalid Phrases:\n")
                    for item in validation["invalid"]:
                        results_text.insert(tk.END, f"  Index {item['index']}: {', '.join(item['issues'])}\n")

                # Check for duplicates
                exact_dupes = self.generator.find_exact_duplicates()
                similar = self.generator.find_similar_phrases(threshold=0.85)

                results_text.insert(tk.END, f"\n=== DUPLICATE DETECTION ===\n")
                results_text.insert(tk.END, f"Exact duplicates found: {len(exact_dupes)}\n")
                results_text.insert(tk.END, f"Similar phrases (>85%): {len(similar)}\n")

                if exact_dupes:
                    results_text.insert(tk.END, "\nExact Duplicates:\n")
                    for group in exact_dupes[:10]:  # Show first 10
                        phrases = [self.generator.proverbs[i].get("original", "Unknown")[:40] for i in group]
                        results_text.insert(tk.END, f"  {phrases}\n")

                results_text.config(state=tk.DISABLED)

            except Exception as e:
                results_text.insert(tk.END, f"Error during validation: {str(e)}")
                results_text.config(state=tk.DISABLED)

        def run_validation_sync():
            asyncio.run(run_validation())

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        async def run_cleanup():
            try:
                report = await self.generator.clean_database(
                    remove_invalid=remove_invalid_var.get(),
                    remove_duplicates=remove_duplicates_var.get()
                )

                message = f"Cleanup Complete!\n\n"
                message += f"Total removed: {report['total_removed']}\n"
                message += f"Validation issues: {len(report['validation']['invalid'])}\n"
                message += f"Exact duplicates removed: {report['deduplication'].get('removed_count', 0)}\n"

                tk.messagebox.showinfo("Cleanup Complete", message)
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Cleanup failed: {str(e)}")

        def run_cleanup_sync():
            asyncio.run(run_cleanup())

        tk.Button(button_frame, text="Validate Database", command=run_validation_sync, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Run Cleanup", command=run_cleanup_sync, bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    # ============================================================================
    # FEAT-4: Category/Tag System UI
    # ============================================================================

    def show_tag_management_dialog(self):
        """Show dialog for managing phrase tags."""
        import tkinter.ttk as ttk
        import asyncio

        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Tag Management")
        dialog.geometry("700x500")
        dialog.configure(padx=10, pady=10)

        # Tag filter dropdown
        filter_frame = tk.Frame(dialog)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(filter_frame, text="Filter by Tag:").pack(side=tk.LEFT, padx=5)

        all_tags = sorted(self.generator.get_all_tags())
        all_tags_display = ["All Tags"] + list(all_tags)

        tag_filter_var = tk.StringVar(value="All Tags")
        tag_filter_combo = ttk.Combobox(filter_frame, textvariable=tag_filter_var,
                                         values=all_tags_display, state="readonly", width=20)
        tag_filter_combo.pack(side=tk.LEFT, padx=5)

        # Phrases list with tags
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        phrases_text = tk.Text(list_frame, yscrollcommand=scrollbar.set, height=15, width=80)
        phrases_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=phrases_text.yview)
        phrases_text.config(state=tk.DISABLED)

        def update_phrases_list():
            phrases_text.config(state=tk.NORMAL)
            phrases_text.delete(1.0, tk.END)

            selected_tag = tag_filter_var.get()

            if selected_tag == "All Tags":
                # Show all phrases with their tags
                for idx, proverb in enumerate(self.generator.proverbs):
                    tags = proverb.get("tags", [])
                    tags_str = ", ".join(tags) if tags else "[no tags]"
                    original = proverb.get("original", "Unknown")[:50]
                    phrases_text.insert(tk.END, f"{idx}: {original}\n   Tags: {tags_str}\n\n")
            else:
                # Show only phrases with selected tag
                results = self.generator.get_phrases_by_tag(selected_tag)
                if results:
                    for idx, proverb in results:
                        tags = proverb.get("tags", [])
                        tags_str = ", ".join(tags)
                        original = proverb.get("original", "Unknown")[:50]
                        phrases_text.insert(tk.END, f"{idx}: {original}\n   Tags: {tags_str}\n\n")
                else:
                    phrases_text.insert(tk.END, f"No phrases found with tag: {selected_tag}")

            phrases_text.config(state=tk.DISABLED)

        tag_filter_combo.bind("<<ComboboxSelected>>", lambda e: update_phrases_list())
        update_phrases_list()

        # Tag editing section
        edit_frame = tk.Frame(dialog)
        edit_frame.pack(fill=tk.X, padx=5, pady=10)

        tk.Label(edit_frame, text="Edit Tags - Index:").pack(side=tk.LEFT, padx=5)
        index_entry = tk.Entry(edit_frame, width=5)
        index_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(edit_frame, text="Tags (comma-separated):").pack(side=tk.LEFT, padx=5)
        tags_entry = tk.Entry(edit_frame, width=30)
        tags_entry.pack(side=tk.LEFT, padx=5)

        def update_tags():
            try:
                idx = int(index_entry.get())
                tags_str = tags_entry.get()
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]

                if self.generator.add_tags_to_phrase(idx, tags):
                    tk.messagebox.showinfo("Success", f"Tags updated for phrase {idx}")
                    update_phrases_list()
                    index_entry.delete(0, tk.END)
                    tags_entry.delete(0, tk.END)
                else:
                    tk.messagebox.showerror("Error", f"Invalid phrase index: {idx}")
            except ValueError:
                tk.messagebox.showerror("Error", "Invalid index (must be integer)")

        tk.Button(edit_frame, text="Update Tags", command=update_tags, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        async def save_changes():
            try:
                await self.generator._save_to_file("malaphors.json", {"proverbs": self.generator.proverbs})
                tk.messagebox.showinfo("Success", "Tags saved to database")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Save failed: {str(e)}")

        def save_sync():
            asyncio.run(save_changes())

        tk.Button(button_frame, text="Save Changes", command=save_sync, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def show_generate_by_category_dialog(self):
        """Show dialog for generating malaphors by category/tag."""
        import tkinter.ttk as ttk

        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Generate by Category")
        dialog.geometry("500x400")
        dialog.configure(padx=10, pady=10)

        # Category selection
        select_frame = tk.Frame(dialog)
        select_frame.pack(fill=tk.X, padx=5, pady=10)

        tk.Label(select_frame, text="Select Category:").pack(side=tk.LEFT, padx=5)

        all_tags = sorted(self.generator.get_all_tags())
        category_options = ["Any Category"] + list(all_tags)

        category_var = tk.StringVar(value="Any Category")
        category_combo = ttk.Combobox(select_frame, textvariable=category_var,
                                       values=category_options, state="readonly", width=25)
        category_combo.pack(side=tk.LEFT, padx=5)

        # Generated malaphors display
        results_frame = tk.Frame(dialog)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        results_text = tk.Text(results_frame, yscrollcommand=scrollbar.set, height=15, width=60)
        results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=results_text.yview)
        results_text.config(state=tk.DISABLED)

        def generate_by_category():
            results_text.config(state=tk.NORMAL)
            results_text.delete(1.0, tk.END)

            category = category_var.get()
            if category == "Any Category":
                category = None

            try:
                for i in range(5):  # Generate 5 examples
                    result = self.generator.generate_with_category(category)
                    results_text.insert(tk.END, f"Malaphor {i+1}:\n")
                    results_text.insert(tk.END, f"  {result['malaphor']}\n")
                    results_text.insert(tk.END, f"  From: {result['source1']} + {result['source2']}\n")
                    results_text.insert(tk.END, f"  Category: {result.get('category', 'Any')}\n\n")

                results_text.config(state=tk.DISABLED)
            except ValueError as e:
                results_text.insert(tk.END, f"Error: {str(e)}")
                results_text.config(state=tk.DISABLED)

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        tk.Button(button_frame, text="Generate", command=generate_by_category, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

        generate_by_category()

    # ============================================================================
    # FEAT-11: Statistics Dashboard UI
    # ============================================================================

    def show_statistics_dashboard(self):
        """Show comprehensive statistics dashboard."""
        import tkinter.ttk as ttk

        dialog = tk.Toplevel(self.root)
        dialog.bind('<F1>', self.assistance.context_help)
        dialog.title("Statistics Dashboard")
        dialog.geometry("800x600")
        dialog.configure(padx=10, pady=10)

        # Get statistics
        stats = self.generator.get_statistics()

        # Summary section
        summary_frame = tk.LabelFrame(dialog, text="Summary Statistics", padx=10, pady=10)
        summary_frame.pack(fill=tk.X, padx=5, pady=5)

        summary_data = [
            ("Total Phrases", str(stats["total_phrases"])),
            ("Total Generated", str(stats["total_generated"])),
            ("Total Favorites", str(stats["total_favorites"])),
            ("Total Tags", str(stats["total_tags"])),
            ("Average Rating", f"{stats['average_rating']:.2f}")
        ]

        for label, value in summary_data:
            frame = tk.Frame(summary_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=label + ":", width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(frame, text=value, font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=20)

        # Tabbed interface
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        # Top Phrases Tab
        phrases_frame = tk.Frame(notebook)
        notebook.add(phrases_frame, text="Top Phrases")

        scrollbar = tk.Scrollbar(phrases_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        phrases_text = tk.Text(phrases_frame, yscrollcommand=scrollbar.set, height=15)
        phrases_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=phrases_text.yview)
        phrases_text.config(state=tk.DISABLED)

        phrases_text.config(state=tk.NORMAL)
        phrases_text.insert(tk.END, "MOST FREQUENTLY USED PHRASES\n")
        phrases_text.insert(tk.END, "=" * 50 + "\n\n")
        for phrase, count in list(stats["phrase_usage"].items())[:15]:
            phrases_text.insert(tk.END, f"{phrase[:45]:<45} : {count:>3} uses\n")
        phrases_text.config(state=tk.DISABLED)

        # Top Tags Tab
        tags_frame = tk.Frame(notebook)
        notebook.add(tags_frame, text="Top Tags")

        scrollbar = tk.Scrollbar(tags_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tags_text = tk.Text(tags_frame, yscrollcommand=scrollbar.set, height=15)
        tags_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=tags_text.yview)
        tags_text.config(state=tk.DISABLED)

        tags_text.config(state=tk.NORMAL)
        tags_text.insert(tk.END, "TOP TAGS\n")
        tags_text.insert(tk.END, "=" * 50 + "\n\n")
        for tag, count in stats["top_tags"]:
            tags_text.insert(tk.END, f"{tag:<30} : {count:>3} phrases\n")
        tags_text.config(state=tk.DISABLED)

        # Source Distribution Tab
        source_frame = tk.Frame(notebook)
        notebook.add(source_frame, text="Sources")

        scrollbar = tk.Scrollbar(source_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        source_text = tk.Text(source_frame, yscrollcommand=scrollbar.set, height=15)
        source_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=source_text.yview)
        source_text.config(state=tk.DISABLED)

        source_text.config(state=tk.NORMAL)
        source_text.insert(tk.END, "PHRASE DISTRIBUTION BY SOURCE\n")
        source_text.insert(tk.END, "=" * 50 + "\n\n")
        total = sum(stats["source_distribution"].values())
        for source, count in stats["source_distribution"].items():
            percentage = (count / total * 100) if total > 0 else 0
            source_text.insert(tk.END, f"{source:<30} : {count:>3} ({percentage:>5.1f}%)\n")
        source_text.config(state=tk.DISABLED)

        # Top Rated Tab
        rated_frame = tk.Frame(notebook)
        notebook.add(rated_frame, text="Top Rated")

        scrollbar = tk.Scrollbar(rated_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        rated_text = tk.Text(rated_frame, yscrollcommand=scrollbar.set, height=15)
        rated_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=rated_text.yview)
        rated_text.config(state=tk.DISABLED)

        rated_text.config(state=tk.NORMAL)
        if stats["top_rated_malaphors"]:
            rated_text.insert(tk.END, "TOP 10 RATED MALAPHORS\n")
            rated_text.insert(tk.END, "=" * 70 + "\n\n")
            for item in stats["top_rated_malaphors"]:
                rating_stars = "⭐" * int(item["rating"])
                malaphor = item["malaphor"][:50]
                rated_text.insert(tk.END, f"{malaphor:<50} {rating_stars}\n")
        else:
            rated_text.insert(tk.END, "No rated malaphors yet.\nGenerate and rate some malaphors to see them here.")
        rated_text.config(state=tk.DISABLED)

        # Export button
        export_frame = tk.Frame(dialog)
        export_frame.pack(fill=tk.X, padx=5, pady=10)

        def export_stats():
            try:
                csv_content = self.generator.export_statistics_csv()
                file_path = tk.filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if file_path:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(csv_content)
                    tk.messagebox.showinfo("Success", f"Statistics exported to:\n{file_path}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Export failed: {str(e)}")

        tk.Button(export_frame, text="Export as CSV", command=export_stats, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(export_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        self._apply_theme(dialog)
