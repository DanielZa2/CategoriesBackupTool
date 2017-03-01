import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import font
import Main as bk
import ResourceStrings as st
import datetime


class SteamSelector:
    """Represent the first window of the app. Here the user will select the location of his steam library."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(st.program_title)
        self.frame_select = tk.Frame(self.root)
        self.frame_select.pack(side=tk.TOP)

        self.label_instruction = tk.Label(self.frame_select, text=st.selector_instruction, justify=tk.LEFT)
        self.label_instruction.pack(side=tk.TOP)

        self.listbox_selector = SteamSelector.Listbox(self.frame_select, selectmode=tk.SINGLE)
        self.listbox_selector.pack(side=tk.TOP)

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(side=tk.BOTTOM)

        self.button_select = tk.Button(self.frame_buttons, text=st.selector_button_select, command=self.action_select)
        self.button_browse = tk.Button(self.frame_buttons, text=st.selector_button_browse, command=self.action_browse)
        self.button_select.pack(side=tk.LEFT)
        self.button_browse.pack(side=tk.LEFT)

        self.time_button_click_delay = datetime.datetime.now()

    def action_browse(self):
        """Bound to the browse button. Allow the user to add their own steam lib if it wasn't auto-detected."""
        delta = datetime.datetime.now() - self.time_button_click_delay
        if delta.seconds <= 0.5:
            return
        self.time_button_click_delay = datetime.datetime.now()
        filetypes = [(st.vdf_file, "*.vdf"), (st.all_file, "*.*")]
        selection = tk.filedialog.askopenfilename(parent=self.root, title=st.selector_title_browse, initialfile=st.sharedconfigvdf, filetypes=filetypes)
        if selection:
            self.listbox_selector.insert(tk.END, selection)
            self.listbox_selector.autowidth(250)

    def action_select(self):
        """Bound to the select button. Selects the correct steam user and runs the second window."""
        delta = datetime.datetime.now() - self.time_button_click_delay
        if delta.seconds <= 0.5:
            return
        self.time_button_click_delay = datetime.datetime.now()

        selection = self.listbox_selector.curselection()
        if len(selection) != 1:
            return
        selected = self.listbox_selector.get(selection[0])
        exporter = Exporter()
        self.root.destroy()
        exporter.start(selected)

    def start(self):
        """Start the steam selector window."""
        locations = bk.SteamLocator.locate_steam()
        for user_id, loc in locations:
            self.listbox_selector.insert(tk.END, loc)

        self.listbox_selector.autowidth(250)
        self.root.mainloop()

    class Listbox(tk.Listbox):
        """Source: http://stackoverflow.com/a/15787278/2842452"""

        def autowidth(self, maxwidth):
            f = font.Font(font=self.cget("font"))
            pixels = 0
            for item in self.get(0, "end"):
                pixels = max(pixels, f.measure(item))
            # bump listbox size until all entries fit
            pixels += 10
            width = int(self.cget("width"))
            for w in range(0, maxwidth + 1, 5):
                if self.winfo_reqwidth() >= pixels:
                    break
                self.config(width=width + w)


class Exporter:
    """Represent the second window of the app. Here the user will backup / restore / export their categories."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(st.program_title)

        self.label_instruction = tk.Label(self.root, text=st.exporter_instruction, justify=tk.LEFT)
        self.label_instruction.pack(side=tk.TOP)

        self.frame_text = tk.Frame(self.root)
        self.frame_text.pack(side=tk.TOP)

        self.text_output = tk.Text(self.frame_text, width=65)
        self.text_output.pack(side=tk.LEFT)

        self.scroll_text = tk.Scrollbar(self.frame_text, orient=tk.VERTICAL, command=self.text_output.yview)
        self.scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output['yscrollcommand'] = self.scroll_text.set

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(side=tk.BOTTOM)

        self.button_backup = tk.Button(self.frame_buttons, text=st.exporter_button_backup, command=self.action_backup)
        self.button_restore = tk.Button(self.frame_buttons, text=st.exporter_button_restore, command=self.action_restore)
        self.button_export = tk.Button(self.frame_buttons, text=st.exporter_button_export, command=self.action_export)
        self.checkbox_symbols_var = False
        self.checkbox_symbols = tk.Checkbutton(self.frame_buttons, text=st.exporter_checkbox_legal, command=self.action_checkbox)
        self.button_backup.pack(side=tk.LEFT)
        self.button_restore.pack(side=tk.LEFT)
        self.button_export.pack(side=tk.LEFT)
        self.checkbox_symbols.pack(side=tk.LEFT)

        self.steam_location = None
        self.steam_categories = None
        self.steam_applist = None

    def action_checkbox(self):
        """Bound to the checkbox. Toggles the variable telling us whatever we should show the legal symbols in the output."""
        self.checkbox_symbols_var = not self.checkbox_symbols_var

    def action_backup(self):
        """Bound to the backup button. Allows the user to select the location to which sharedconfig.vdf will be copied,"""
        try:
            filetypes = [(st.json_file, "*.json"), (st.text_file, "*.txt"), (st.all_file, "*.*")]
            selection = tk.filedialog.asksaveasfilename(parent=self.root, title=st.exporter_title_backup, defaultextension=".json", filetypes=filetypes)

            if selection == self.steam_location:
                tk.messagebox.showerror(st.error_backup, st.error_backup_text_same, parent=self.root)
            if selection and selection != self.steam_location:
                bk.BackupAndRestore.backup_config(self.steam_location, selection)
        except bk.ParseException:
            tk.messagebox.showerror(st.error_backup, st.error_backup_text_not_vdf, parent=self.root)

    def action_restore(self):
        """Bound to the restore button. Allows the user to select the location from which sharedconfig.vdf will be restored,"""
        try:
            filetypes = [(st.json_file, "*.json"), (st.text_file, "*.txt"), (st.all_file, "*.*")]
            selection = tk.filedialog.askopenfilename(parent=self.root, title=st.exporter_title_restore, defaultextension=".json", filetypes=filetypes)

            if selection == self.steam_location:
                tk.messagebox.showerror(st.error_restore, st.error_restore_text_same, parent=self.root)
            if selection and selection != self.steam_location:
                bk.BackupAndRestore.restore_config(selection, self.steam_location)
        except bk.ParseException:
            tk.messagebox.showerror(st.error_restore, st.error_restore_text_not_vdf, parent=self.root)

    def action_export(self):
        """Bound to the export button. Will trigger the main functionallity of this app. Will read sharedconfig.vdf, parse it and display / save human-readable version of it."""
        if self.steam_categories is None:
            self.steam_categories = bk.Categories.factory(self.steam_location)
            self.steam_categories.name_apps(self.steam_applist)

        text = self.steam_categories.apps_string(self.checkbox_symbols_var)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)
        filetypes = [(st.text_file, "*.txt"), (st.all_file, "*.*")]
        selection = tk.filedialog.asksaveasfilename(parent=self.root, defaultextension=".txt", title=st.exporter_title_export, filetypes=filetypes)  # (st.all_file, "*.*")
        if selection:
            with open(selection, "w", encoding='UTF-8') as file:
                file.write(text)

    def __scroll_handler__(self, *l):
        """Source: http://infohost.nmt.edu/~shipman/soft/tkinter/web/entry.html"""
        op, how_many = l[0], l[1]

        if op == 'scroll':
            units = l[2]
            self.text_output.xview_scroll(how_many, units)
        elif op == 'moveto':
            self.text_output.xview_moveto(how_many)

    def start(self, locations):
        """Start the main window"""
        self.steam_location = locations
        self.text_output.insert(tk.END, st.exporter_text_prefix + str(locations))
        self.steam_applist = bk.SteamAppList().fetch()
        self.root.mainloop()


def main():
    """Starts the GUI"""
    selector = SteamSelector()
    selector.start()


if __name__ == "__main__":
    main()
