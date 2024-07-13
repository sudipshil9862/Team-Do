import gi
import os
import sys
from pathlib import Path

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk, GLib

class Task:
    def __init__(self, description):
        self.description = description
        self.status = "Create"  #values: Create, Progress, Complete

class ToDoListApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='com.example.TodoListApp', **kwargs)
        Adw.init()

    def do_activate(self):
        self.win = ToDoListWindow(application=self)
        self.win.present()

class ToDoListWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Team-Do")
        self.set_default_size(400, 300)
        
        #storing the initial size
        self.initial_width = 400
        self.initial_height = 300

        #initializing the tasks attribute here
        self.tasks = []
        
        self.headerbar = Adw.HeaderBar()
        title_label = Gtk.Label(label="Team-Do")
        title_label.add_css_class("title-label")
        self.headerbar.set_title_widget(title_label)
        self.headerbar.add_css_class("headerbar")

        # Hamburger menu button
        menu_button = Gtk.MenuButton()
        menu_icon = Gtk.Image.new_from_icon_name("open-menu-symbolic")
        menu_button.set_child(menu_icon)
        menu_button.set_menu_model(self.create_menu_model())
        self.headerbar.pack_end(menu_button)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.set_vexpand(True)
        self.box.set_hexpand(True)
        self.box.append(self.headerbar)
        self.set_content(self.box)

        # Hurrah emoji label
        self.hurrah_label = Gtk.Label(label="🎉 Hurrah! 🎉")
        self.hurrah_label.set_visible(False)  # Initially hidden
        self.box.append(self.hurrah_label)

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter a task")
        self.entry.connect("activate", self.on_add_task_clicked)
        self.box.append(self.entry)

        self.add_button = Gtk.Button(label="Add Task")
        self.add_button.add_css_class("suggested-action")
        self.add_button.add_css_class("animated-button")
        self.add_button.connect("clicked", self.on_add_task_clicked)
        self.box.append(self.add_button)

        self.listbox = Gtk.ListBox()
        self.listbox.set_vexpand(True)
        self.listbox.set_hexpand(True)
        self.box.append(self.listbox)

        #loading CSS from styles.css file
        css_provider = Gtk.CssProvider()
        css_file_path = os.path.join(os.path.dirname(__file__), '../css/styles.css')
        css_provider.load_from_path(css_file_path)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def create_menu_model(self):
        menu = Gio.Menu()
        menu.append("About", "app.about")
        menu.append("Quit", "app.quit")
        self.get_application().set_accels_for_action("app.quit", ["<Primary>q"])
        return menu

    def on_add_task_clicked(self, widget):
        description = self.entry.get_text()
        if description:
            task = Task(description)
            self.tasks.append(task)
            self.add_task_to_listbox(task)
            self.entry.set_text("")
            self.entry.grab_focus()  # Set focus back to entry widget

    def add_task_to_listbox(self, task):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_vexpand(True)
        hbox.set_hexpand(True)
        row.set_child(hbox)

        label = Gtk.Label(label=task.description, xalign=0)
        hbox.append(label)

        progress_bar = Gtk.ProgressBar()
        progress_bar.set_fraction(0.0)
        progress_bar.set_vexpand(True)
        progress_bar.set_hexpand(True)
        progress_bar.add_css_class("task-progress-bar")
        hbox.append(progress_bar)

        button_complete = Gtk.Button(label="Complete")
        button_complete.add_css_class("normal-button")
        button_progress = Gtk.Button(label="Progress")
        button_progress.add_css_class("normal-button")
        button_progress.connect("clicked", self.on_progress_clicked, task, progress_bar, button_progress, button_complete)
        hbox.append(button_progress)

        button_complete.connect("clicked", self.on_complete_clicked, task, progress_bar, button_progress, button_complete)
        hbox.append(button_complete)

        button_delete = Gtk.Button(label="Delete")
        button_delete.connect("clicked", self.on_delete_clicked, row, task)
        button_delete.add_css_class("destructive-action")
        hbox.append(button_delete)

        self.listbox.append(row)
        row.set_visible(True)

    def on_progress_clicked(self, widget, task, progress_bar, button_progress, button_complete):
        if task.status == "Progress":
            task.status = "Create"
            progress_bar.set_fraction(0.0)
            button_progress.remove_css_class("progress-button")
            button_progress.add_css_class("normal-button")
        else:
            task.status = "Progress"
            progress_bar.set_fraction(0.5)
            button_progress.add_css_class("progress-button")
            button_progress.remove_css_class("normal-button")
            if button_complete.has_css_class("complete-button"):
                button_complete.remove_css_class("complete-button")
                button_complete.add_css_class("normal-button")

    def on_complete_clicked(self, widget, task, progress_bar, button_progress, button_complete):
        if task.status == "Complete":
            task.status = "Progress"
            progress_bar.set_fraction(0.5)
            button_complete.remove_css_class("complete-button")
            button_complete.add_css_class("normal-button")
        else:
            task.status = "Complete"
            progress_bar.set_fraction(1.0)
            button_complete.add_css_class("complete-button")
            button_complete.remove_css_class("normal-button")
            if not button_progress.has_css_class("progress-button"):
                button_progress.add_css_class("progress-button")
                button_progress.remove_css_class("normal-button")
            self.show_hurrah()

    def show_hurrah(self):
        self.hurrah_label.set_visible(True)
        self.hurrah_label.add_css_class("hurrah-animation")
        GLib.timeout_add_seconds(2, self.hide_hurrah)

    def hide_hurrah(self):
        self.hurrah_label.set_visible(False)
        self.hurrah_label.remove_css_class("hurrah-animation")
        return False

    def on_delete_clicked(self, widget, row, task):
        self.tasks.remove(task)
        self.listbox.remove(row)
        if not self.tasks:
            self.set_default_size(self.initial_width, self.initial_height)
        self.force_resize()

    def force_resize(self):
        self.set_default_size(-1, -1)
        self.set_resizable(True)

if __name__ == '__main__':
    app = ToDoListApp()

    def on_about_action(action, param):
        about_dialog = Adw.AboutWindow(
            application_name="Team-Do",
            application_icon="com.example.TodoListApp",
            version="1.0.0",
            copyright="© 2024 Team-Do",
            license_type=Gtk.License.MIT_X11,
            website="https://github.com/sudipshil9862/Team-Do",
            issue_url="https://github.com/sudipshil9862/Team-Do/issues",
            comments="Team-Do is a collaborative to-do list application.",
            developers=["Sudip Shil"],
            designers=["Sudip Shil"],
            documenters=["Sudip Shil"],
            modal=True,
            transient_for=app.win
        )
        about_dialog.present()

    def on_quit_action(action, param):
        app.quit()

    app.add_action(Gio.SimpleAction.new("about", None))
    app.add_action(Gio.SimpleAction.new("quit", None))
    app.lookup_action("about").connect("activate", on_about_action)
    app.lookup_action("quit").connect("activate", on_quit_action)

    app.run(None)

