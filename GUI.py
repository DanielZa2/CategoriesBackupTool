import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import font
import Main as bk
import datetime

"""
Design:

Button 1:  Detect / backup sharedconfig.vdf
Button 2: Export readable format of sharedconfig.vdf
Button 3: restore backedup sharedconfig.vdf



Checkbox 1: Show trademark / copyright signs in names

"""


class Exporter:
    INSTRUCTION = \
        ("INSTRUCTION:\n"
         " Select the steam users you want to backup / export.\n"
         " If your user isn't listed on the box bellow you can add it by browsing to:\n"
         " Steam\\userdata\\<USER_ID>\\7\\remote\\sharedconfig.vdf")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Categories exporter")
        self.frame_text = tk.Frame(self.root)
        self.frame_text.pack(side=tk.TOP)

        self.text_output = tk.Text(self.frame_text)
        self.text_output.pack(side=tk.LEFT)

        self.text_output.insert(tk.END, Exporter.INSTRUCTION)

        self.scroll_text = tk.Scrollbar(self.frame_text, orient=tk.VERTICAL, command=self.text_output.yview)
        self.scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_output['yscrollcommand'] = self.scroll_text.set

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(side=tk.BOTTOM)

        self.button_backup = tk.Button(self.frame_buttons, text="backup", command=self.action_backup)
        self.button_restore = tk.Button(self.frame_buttons, text="restore", command=self.action_restore)
        self.button_export = tk.Button(self.frame_buttons, text="export", command=self.action_export)
        self.checkbox_symbols_var = False
        self.checkbox_symbols = tk.Checkbutton(self.frame_buttons, text="Hide legal symbols", command=self.action_checkbox)
        self.button_backup.pack(side=tk.LEFT)
        self.button_restore.pack(side=tk.LEFT)
        self.button_export.pack(side=tk.LEFT)
        self.checkbox_symbols.pack(side=tk.LEFT)

        self.steam_location = None
        self.steam_categories = None
        self.steam_applist = None


    def action_checkbox(self):
        self.checkbox_symbols_var = not self.checkbox_symbols_var

    def action_backup(self):
        try:
            selection = tk.filedialog.asksaveasfilename(parent=self.root, title="Save backup to..", initialfile="sharedconfig.vdf",
                                                        filetypes={("Valve's Data Format", "*.vdf"), ("Text file", "*.txt"), ("all files", "*.*")})
            if selection == self.steam_location:
                tk.messagebox.showerror("Backup Error", "Backup error: Source and target file are the same", parent=self.root)
            if selection and selection != self.steam_location:
                bk.backup_config(self.steam_location, selection)
        except bk.ParseException:
            tk.messagebox.showerror("Backup Error", "Backup error: The source file is probably not sharedconfig.vdf", parent=self.root)

    def action_restore(self):
        try:
            selection = tk.filedialog.askopenfilename(parent=self.root, title="Restore backup from..", initialfile="sharedconfig.vdf",
                                                      filetypes={("Valve's Data Format", "*.vdf"), ("Text file", "*.txt"), ("all files", "*.*")})

            if selection == self.steam_location:
                tk.messagebox.showerror("Restore Error", "Restore error: Source and target file are the same", parent=self.root)
            if selection and selection != self.steam_location:
                bk.restore_config(selection, self.steam_location)
        except bk.ParseException:
            tk.messagebox.showerror("Restore Error", "Restore error: The source file is probably not sharedconfig.vdf", parent=self.root)

    def action_export(self):
        if self.steam_categories is None:
            self.steam_categories = bk.Categories.factory(self.steam_location)
            self.steam_categories.name_apps(self.steam_applist)

        text = self.steam_categories.apps_string(self.checkbox_symbols_var)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, text)
        # TODO insert defualt name with the date
        # TODO play around with the defaultextension parameter in order to make the extension sleected by filetypes be the one used when no extension  is selected
        selection = tk.filedialog.asksaveasfilename(parent=self.root, defaultextension=".txt", title="Export to..", filetypes={("Text file", "*.txt"), ("all files", "*.*")})
        if selection:
            with open(selection, "w", encoding='UTF-8') as file:
                file.write(text)

    def __scroll_handler__(self, *l):
        op, how_many = l[0], l[1]

        if op == 'scroll':
            units = l[2]
            self.text_output.xview_scroll(how_many, units)
        elif op == 'moveto':
            self.text_output.xview_moveto(how_many)

    def start(self, locations):
        self.steam_location = locations
        self.text_output.insert(tk.END, "\n\nSteam Location:" + str(locations))
        self.steam_applist = bk.SteamAppList().fetch()
        self.root.mainloop()


class SteamSelector:
    INSTRUCTION = \
        ("INSTRUCTION:\n"
         " Select the steam users you want to backup / export.\n"
         " If your user isn't listed on the box bellow you can add it by browsing to:\n"
         " Steam\\userdata\\<USER_ID>\\7\\remote\\sharedconfig.vdf")

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Categories exporter")
        self.frame_select = tk.Frame(self.root)
        self.frame_select.pack(side=tk.TOP)

        self.label_instruction = tk.Label(self.frame_select, text=SteamSelector.INSTRUCTION, justify=tk.LEFT)
        self.label_instruction.pack(side=tk.TOP)

        self.listbox_selector = SteamSelector.Listbox(self.frame_select, selectmode=tk.SINGLE)
        self.listbox_selector.pack(side=tk.TOP)

        self.frame_buttons = tk.Frame(self.root)
        self.frame_buttons.pack(side=tk.BOTTOM)

        self.button_select = tk.Button(self.frame_buttons, text="Select", command=self.action_select)
        self.button_browse = tk.Button(self.frame_buttons, text="Browse", command=self.action_browse)
        self.button_select.pack(side=tk.LEFT)
        self.button_browse.pack(side=tk.LEFT)

        self.time_button_click_delay = datetime.datetime.now()

    def action_browse(self):
        delta = datetime.datetime.now() - self.time_button_click_delay
        if delta.seconds <= 0.5:
            return
        self.time_button_click_delay = datetime.datetime.now()
        selection = tk.filedialog.askopenfilename(parent=self.root, title="Select sharecondig.vdf..", initialfile="sharedconfig.vdf", filetypes={("Valve's Data Format", "*.vdf")}, mustexist=True)
        if selection:
            self.listbox_selector.insert(tk.END, selection)
            self.listbox_selector.autowidth(250)

    def action_select(self):

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
        locations = bk.locate_steam()
        for user_id, loc in locations:
            self.listbox_selector.insert(tk.END, loc)

        self.listbox_selector.autowidth(250)
        self.root.mainloop()

    class Listbox(tk.Listbox):
        """Source:http://stackoverflow.com/a/15787278/2842452"""

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


def main():
    selector = SteamSelector()
    selector.start()


main()
