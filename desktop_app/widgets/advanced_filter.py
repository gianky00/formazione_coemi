"""
Advanced Column Filter Widget for Intelleo.
Provides Excel-like filtering with multi-select, search, and date tree grouping.
"""

import tkinter as tk
from collections import defaultdict
from datetime import datetime
from tkinter import ttk


class AdvancedFilterPopup(tk.Toplevel):
    """
    Advanced filter popup with multi-select checkboxes and search.
    For date columns, provides hierarchical year/month/day filtering.
    """

    def __init__(self, parent, tree, column, column_display_name, on_filter_change=None):
        super().__init__(parent)
        self.tree = tree
        self.column = column
        self.column_display_name = column_display_name
        self.on_filter_change = on_filter_change

        # Detect if date column
        self.is_date_column = self._detect_date_column()

        # Store current filter state
        self.selected_values = set()
        self.all_values = []

        self.title(f"Filtra: {column_display_name}")
        self.geometry("320x450")
        self.resizable(False, True)
        self.transient(parent)

        # Make it stay on top
        self.attributes("-topmost", True)

        self.setup_ui()
        self.load_values()

        # Position near mouse
        self.update_idletasks()
        x = self.winfo_pointerx() - 160
        y = self.winfo_pointery() + 10
        self.geometry(f"+{x}+{y}")

        # Focus
        self.focus_set()
        self.search_entry.focus_set()

    def _detect_date_column(self):
        """Detect if this column contains dates."""
        date_keywords = ["data", "date", "scadenza", "rilascio", "nascita", "emissione"]
        return any(kw in self.column.lower() for kw in date_keywords)

    def setup_ui(self):
        main_frame = tk.Frame(self, bg="#FFFFFF", padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Search bar
        search_frame = tk.Frame(main_frame, bg="#FFFFFF")
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Cerca:", bg="#FFFFFF", font=("Segoe UI", 9)).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Select all / Deselect all
        btn_frame = tk.Frame(main_frame, bg="#FFFFFF")
        btn_frame.pack(fill="x", pady=(0, 5))

        tk.Button(
            btn_frame,
            text="Seleziona tutto",
            command=self._select_all,
            bg="#3B82F6",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
        ).pack(side="left", padx=2)
        tk.Button(
            btn_frame,
            text="Deseleziona tutto",
            command=self._deselect_all,
            bg="#6B7280",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
        ).pack(side="left", padx=2)
        tk.Button(
            btn_frame,
            text="Inverti",
            command=self._invert_selection,
            bg="#9CA3AF",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
        ).pack(side="left", padx=2)

        # Checkbox list container
        list_container = tk.Frame(main_frame, bg="#FFFFFF")
        list_container.pack(fill="both", expand=True, pady=5)

        # Canvas for scrolling
        self.canvas = tk.Canvas(
            list_container, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB"
        )
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)

        self.checkbox_frame = tk.Frame(self.canvas, bg="#FFFFFF")
        self.checkbox_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.checkbox_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Expand checkbox frame width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling - use bind instead of bind_all to avoid TclError
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.checkbox_frame.bind("<MouseWheel>", self._on_mousewheel)

        # Action buttons
        action_frame = tk.Frame(main_frame, bg="#FFFFFF")
        action_frame.pack(fill="x", pady=(10, 0))

        tk.Button(
            action_frame,
            text="Applica",
            command=self._apply_filter,
            bg="#10B981",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            width=10,
        ).pack(side="right", padx=5)
        tk.Button(
            action_frame,
            text="Cancella filtro",
            command=self._clear_filter,
            bg="#EF4444",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            width=12,
        ).pack(side="right", padx=5)
        tk.Button(
            action_frame,
            text="Annulla",
            command=self.destroy,
            bg="#6B7280",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            width=8,
        ).pack(side="left")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width - 4)

    def _on_mousewheel(self, event):
        try:
            if self.winfo_exists() and self.canvas.winfo_exists():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass

    def load_values(self):
        """Load unique values from tree column."""
        col_idx = list(self.tree["columns"]).index(self.column)

        values = []
        for item in self.tree.get_children():
            val = self.tree.item(item)["values"][col_idx]
            if val is not None:
                values.append(str(val))

        if self.is_date_column:
            self._load_date_tree(values)
        else:
            self._load_flat_list(values)

    def _load_flat_list(self, values):
        """Load values as flat checkbox list."""
        unique_values = sorted(set(v for v in values if v and v.lower() != "none"))
        self.all_values = unique_values

        # Include empty/none option
        if any(not v or v.lower() == "none" for v in values):
            unique_values = ["(Vuoto)"] + list(unique_values)

        self.checkboxes = {}
        for value in unique_values:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(
                self.checkbox_frame, text=value, variable=var, style="Filter.TCheckbutton"
            )
            cb.pack(anchor="w", pady=1, padx=5)
            self.checkboxes[value] = var
            self.selected_values.add(value)

    def _load_date_tree(self, values):
        """Load date values as hierarchical tree (Year > Month > Day)."""
        # Parse dates and group by year/month
        date_tree = defaultdict(lambda: defaultdict(set))
        unparsed = set()

        for val in values:
            if not val or val.lower() == "none" or val == "NESSUNA":
                unparsed.add("(Vuoto)")
                continue

            parsed = self._parse_date(val)
            if parsed:
                year, month, day = parsed
                date_tree[year][month].add(day)
            else:
                unparsed.add(val)

        self.checkboxes = {}
        self.year_vars = {}
        self.month_vars = {}
        self.day_vars = {}

        # Build hierarchical checkboxes
        for year in sorted(date_tree.keys(), reverse=True):
            # Year level
            year_var = tk.BooleanVar(value=True)
            self.year_vars[year] = year_var

            year_frame = tk.Frame(self.checkbox_frame, bg="#FFFFFF")
            year_frame.pack(anchor="w", fill="x")

            year_cb = ttk.Checkbutton(
                year_frame,
                text=f"\u25bc {year}",
                variable=year_var,
                command=lambda y=year: self._toggle_year(y),
            )
            year_cb.pack(anchor="w", padx=5)

            # Month container (collapsible)
            month_container = tk.Frame(year_frame, bg="#FFFFFF")
            month_container.pack(anchor="w", fill="x", padx=20)

            for month in sorted(date_tree[year].keys()):
                month_name = self._get_month_name(month)
                month_key = (year, month)
                month_var = tk.BooleanVar(value=True)
                self.month_vars[month_key] = month_var

                month_frame = tk.Frame(month_container, bg="#FFFFFF")
                month_frame.pack(anchor="w", fill="x")

                month_cb = ttk.Checkbutton(
                    month_frame,
                    text=f"\u25b8 {month_name}",
                    variable=month_var,
                    command=lambda mk=month_key: self._toggle_month(mk),
                )
                month_cb.pack(anchor="w", padx=5)

                # Days container
                day_container = tk.Frame(month_frame, bg="#FFFFFF")
                day_container.pack(anchor="w", fill="x", padx=20)

                for day in sorted(date_tree[year][month]):
                    day_key = (year, month, day)
                    day_var = tk.BooleanVar(value=True)
                    self.day_vars[day_key] = day_var

                    day_cb = ttk.Checkbutton(
                        day_container,
                        text=f"{day:02d}",
                        variable=day_var,
                        command=lambda dk=day_key: self._on_day_toggle(dk),
                    )
                    day_cb.pack(anchor="w", padx=5)

                    self.checkboxes[day_key] = day_var

        # Unparsed values
        if unparsed:
            sep = ttk.Separator(self.checkbox_frame, orient="horizontal")
            sep.pack(fill="x", pady=5, padx=5)

            for val in sorted(unparsed):
                var = tk.BooleanVar(value=True)
                cb = ttk.Checkbutton(self.checkbox_frame, text=val, variable=var)
                cb.pack(anchor="w", pady=1, padx=5)
                self.checkboxes[val] = var

    def _parse_date(self, val):
        """Parse date string and return (year, month, day) tuple."""
        formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(str(val).strip(), fmt)
                return (dt.year, dt.month, dt.day)
            except:
                continue
        return None

    def _get_month_name(self, month):
        """Get Italian month name."""
        months = [
            "",
            "Gennaio",
            "Febbraio",
            "Marzo",
            "Aprile",
            "Maggio",
            "Giugno",
            "Luglio",
            "Agosto",
            "Settembre",
            "Ottobre",
            "Novembre",
            "Dicembre",
        ]
        return months[month] if 1 <= month <= 12 else str(month)

    def _toggle_year(self, year):
        """Toggle all months/days under a year."""
        state = self.year_vars[year].get()
        for (y, m), var in self.month_vars.items():
            if y == year:
                var.set(state)
        for (y, m, d), var in self.day_vars.items():
            if y == year:
                var.set(state)

    def _toggle_month(self, month_key):
        """Toggle all days under a month."""
        year, month = month_key
        state = self.month_vars[month_key].get()
        for (y, m, d), var in self.day_vars.items():
            if y == year and m == month:
                var.set(state)

    def _on_day_toggle(self, day_key):
        """Update parent checkboxes when day is toggled."""
        year, month, day = day_key

        # Check if all days in month are selected
        month_days = [(y, m, d) for (y, m, d) in self.day_vars.keys() if y == year and m == month]
        all_selected = all(self.day_vars[dk].get() for dk in month_days)
        self.month_vars[(year, month)].set(all_selected)

        # Check if all months in year are selected
        year_months = [(y, m) for (y, m) in self.month_vars.keys() if y == year]
        all_months_selected = all(self.month_vars[mk].get() for mk in year_months)
        self.year_vars[year].set(all_months_selected)

    def _on_search_change(self, *args):
        """Filter checkboxes based on search."""
        search_text = self.search_var.get().lower()

        for widget in self.checkbox_frame.winfo_children():
            widget.pack_forget()

        for widget in self.checkbox_frame.winfo_children():
            text = ""
            if isinstance(widget, ttk.Checkbutton):
                text = str(widget.cget("text")).lower()

            if not search_text or search_text in text:
                widget.pack(anchor="w", pady=1, padx=5)

    def _select_all(self):
        """Select all visible checkboxes."""
        for var in self.checkboxes.values():
            var.set(True)
        for var in getattr(self, "year_vars", {}).values():
            var.set(True)
        for var in getattr(self, "month_vars", {}).values():
            var.set(True)
        for var in getattr(self, "day_vars", {}).values():
            var.set(True)

    def _deselect_all(self):
        """Deselect all checkboxes."""
        for var in self.checkboxes.values():
            var.set(False)
        for var in getattr(self, "year_vars", {}).values():
            var.set(False)
        for var in getattr(self, "month_vars", {}).values():
            var.set(False)
        for var in getattr(self, "day_vars", {}).values():
            var.set(False)

    def _invert_selection(self):
        """Invert selection."""
        for var in self.checkboxes.values():
            var.set(not var.get())

    def _apply_filter(self):
        """Apply the filter."""
        if self.is_date_column:
            selected_dates = set()
            for (y, m, d), var in self.day_vars.items():
                if var.get():
                    selected_dates.add((y, m, d))

            # Include unparsed values
            for key, var in self.checkboxes.items():
                if not isinstance(key, tuple) and var.get():
                    selected_dates.add(key)

            if self.on_filter_change:
                self.on_filter_change(self.column, "date", selected_dates)
        else:
            selected = set()
            for val, var in self.checkboxes.items():
                if var.get():
                    selected.add(val)

            if self.on_filter_change:
                self.on_filter_change(self.column, "values", selected)

        self.destroy()

    def _clear_filter(self):
        """Clear filter for this column."""
        if self.on_filter_change:
            self.on_filter_change(self.column, "clear", None)
        self.destroy()


class FilterableTreeview(ttk.Treeview):
    """
    Extended Treeview with advanced filtering capabilities.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.column_filters = {}  # column -> (filter_type, filter_data)
        self.original_data = []  # Store original data for filtering
        self.column_display_names = {}  # column id -> display name

        # Bind right-click on headings
        self.bind("<Button-3>", self._on_header_right_click)

    def set_column_display_names(self, names_dict):
        """Set display names for columns."""
        self.column_display_names = names_dict

    def store_original_data(self, data):
        """Store original data for filtering."""
        self.original_data = list(data)

    def _on_header_right_click(self, event):
        """Handle right-click on column header."""
        region = self.identify_region(event.x, event.y)

        if region == "heading":
            column = self.identify_column(event.x)
            if column:
                # Get column id (remove '#' prefix)
                col_id = column.replace("#", "")
                if col_id.isdigit():
                    col_idx = int(col_id) - 1
                    if 0 <= col_idx < len(self["columns"]):
                        col_name = self["columns"][col_idx]
                        display_name = self.column_display_names.get(col_name, col_name)
                        self._show_filter_popup(col_name, display_name)

    def _show_filter_popup(self, column, display_name):
        """Show filter popup for column."""
        popup = AdvancedFilterPopup(
            self.winfo_toplevel(),
            self,
            column,
            display_name,
            on_filter_change=self._on_filter_change,
        )

    def _on_filter_change(self, column, filter_type, filter_data):
        """Handle filter change from popup."""
        if filter_type == "clear":
            if column in self.column_filters:
                del self.column_filters[column]
        else:
            self.column_filters[column] = (filter_type, filter_data)

        self._apply_all_filters()

    def _apply_all_filters(self):
        """Apply all active filters."""
        # This should be overridden by the view that uses this treeview
        # to properly filter and redisplay data
        pass

    def get_filter_predicate(self, column, value):
        """Check if value passes filter for column."""
        if column not in self.column_filters:
            return True

        filter_type, filter_data = self.column_filters[column]

        if filter_type == "values":
            str_val = str(value) if value else "(Vuoto)"
            if not value or str(value).lower() == "none":
                str_val = "(Vuoto)"
            return str_val in filter_data

        elif filter_type == "date":
            if not value or str(value).lower() in ["none", "nessuna", ""]:
                return "(Vuoto)" in filter_data

            # Parse the date
            parsed = self._parse_date_value(value)
            if parsed:
                return parsed in filter_data
            else:
                return str(value) in filter_data

        return True

    def _parse_date_value(self, val):
        """Parse date value to tuple."""
        formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(str(val).strip(), fmt)
                return (dt.year, dt.month, dt.day)
            except:
                continue
        return None

    def has_active_filters(self):
        """Check if any filters are active."""
        return len(self.column_filters) > 0

    def clear_all_filters(self):
        """Clear all filters."""
        self.column_filters.clear()
        self._apply_all_filters()

    def get_active_filter_columns(self):
        """Get list of columns with active filters."""
        return list(self.column_filters.keys())


def setup_filterable_treeview(tree, column_names):
    """
    Setup a treeview with filtering capabilities.
    Returns methods to bind to the tree.
    """
    # Store column filters
    tree._column_filters = {}
    tree._column_display_names = column_names

    def on_header_right_click(event):
        region = tree.identify_region(event.x, event.y)
        if region == "heading":
            column = tree.identify_column(event.x)
            if column:
                col_id = column.replace("#", "")
                if col_id.isdigit():
                    col_idx = int(col_id) - 1
                    cols = list(tree["columns"])
                    if 0 <= col_idx < len(cols):
                        col_name = cols[col_idx]
                        display_name = column_names.get(col_name, col_name)

                        def on_filter(col, ftype, fdata):
                            if ftype == "clear":
                                if col in tree._column_filters:
                                    del tree._column_filters[col]
                            else:
                                tree._column_filters[col] = (ftype, fdata)
                            # Trigger custom event
                            tree.event_generate("<<FilterChanged>>")

                        AdvancedFilterPopup(
                            tree.winfo_toplevel(),
                            tree,
                            col_name,
                            display_name,
                            on_filter_change=on_filter,
                        )

    tree.bind("<Button-3>", on_header_right_click)

    def check_filter(column, value):
        """Check if value passes filter."""
        if column not in tree._column_filters:
            return True

        ftype, fdata = tree._column_filters[column]

        if ftype == "values":
            str_val = str(value) if value else "(Vuoto)"
            if not value or str(value).lower() in ["none", "nessuna"]:
                str_val = "(Vuoto)"
            return str_val in fdata

        elif ftype == "date":
            if not value or str(value).lower() in ["none", "nessuna", ""]:
                return "(Vuoto)" in fdata

            # Parse date
            for fmt in ["%d/%m/%Y", "%Y-%m-%d"]:
                try:
                    dt = datetime.strptime(str(value).strip(), fmt)
                    return (dt.year, dt.month, dt.day) in fdata
                except:
                    continue
            return str(value) in fdata

        return True

    tree.check_filter = check_filter

    def has_filters():
        return len(tree._column_filters) > 0

    tree.has_filters = has_filters

    def clear_filters():
        tree._column_filters.clear()
        tree.event_generate("<<FilterChanged>>")

    tree.clear_filters = clear_filters

    return tree
