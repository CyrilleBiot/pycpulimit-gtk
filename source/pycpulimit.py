#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import  os
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class cpulimit(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Python CPU Limit")

        if os.path.exists('.git'):
            self.pathDir = "./"
        # Launch since a deb package install
        else:
            self.pathDir = "/usr/share/pycpulimit/"

        self.set_border_width(10)
        self.set_resizable(False)
        self.set_icon_from_file(self.pathDir + "apropos.png")
        self.set_border_width(10)



        # VARIABLES
        self.cpu_nb_total = (len(os.sched_getaffinity(0)))
        self.cpu_nb_to_use = (len(os.sched_getaffinity(0)))
        self.cmd_shell = ""

        # SpinButton & label spinbutton
        adjustment = Gtk.Adjustment(upper=100, step_increment=5, page_increment=10)
        self.spinbutton = Gtk.SpinButton()
        self.spinbutton.set_adjustment(adjustment)
        self.spinbutton.set_value(35)
        self.spinbutton.connect("value-changed", self.on_value_changed)
        label_limit = Gtk.Label(label="% DE CHARGE CPU")
        label_cpu_number_to_use = Gtk.Label(label="Nombres de CPU à utiliser :")

        # GRID
        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)
        grid.set_column_spacing(6)
        grid.set_row_spacing(15)
        grid.set_row_homogeneous(False)

        grid.attach(self.spinbutton, 0, 0, 5, 1)
        grid.attach(label_limit, 6, 0, 2, 1)
        grid.attach(label_cpu_number_to_use, 0, 1, 7, 1)

        self.entry_command = Gtk.Entry()
        self.entry_command.connect("focus-out-event", self.on_lost_focus)

        switch = [0] * self.cpu_nb_total
        label_switch  = [0] * self.cpu_nb_total

        for j in range(self.cpu_nb_total):
            switch[j] = Gtk.Switch()
            switch[j].set_active(True)
            if j == 0:
                switch[j].set_sensitive(False)
                switch[j].set_property("tooltip-text", "Au moins un CPU de nécessaire...")

            switch[j].connect("notify::active", self.on_switch_activated)
            label_switch[j] = Gtk.Label(label="CPU {}".format( (j+1)))
            grid.attach(switch[j], 2,2+j,2,1)
            grid.attach(label_switch[j],5,2+j,3,1)

        # Bouton OK
        button_OK = Gtk.Button(label = "Lancer la commande")
        button_OK.connect("clicked", self.on_clic_OK)
        button_OK.connect('pressed', self.on_button_pressed)
        button_OK.connect('released', self.on_button_released)

        # LABEL PROCESS
        self.label_waiting = Gtk.Label(label="")

        # Attache sur le grid
        grid.attach(self.entry_command,0,j+4,9,1)
        grid.attach(button_OK, 0, j+5,9,1)
        grid.attach(self.label_waiting,0,j+6,9,1)

        # add the grid to the window
        self.add(grid)


    def on_button_pressed(self, widget):
        if self.entry_command.get_text() != "":
            self.label_waiting.set_name("text-red")
            self.label_waiting.set_text("WAITING DURANT PROCESS")

    def on_button_released(self, widget):
        if self.entry_command.get_text() != "":
            self.label_waiting.set_name("text")
            self.label_waiting.set_text("PROCESS IS DONE.")

    def on_lost_focus(self, widget, button):
        self.on_udpate_command()

    def on_udpate_command(self):
        self.cmd_shell = ""
        self.cmd_shell = "nice -n 20 cpulimit --limit " + str(self.spinbutton.get_value_as_int()) + " --cpu " \
                         + str(self.cpu_nb_to_use) + " -z -- " + str(self.entry_command.get_text())
        print(self.cmd_shell)

    def on_value_changed(self, scroll):
        self.on_udpate_command()

    def on_switch_activated(self, switch, param):
        print(param)
        if switch.get_active():
            state = "on"
            action = 1
        else:
            state = "off"
            action = -1
        self.cpu_nb_to_use = self.cpu_nb_to_use + action
        self.on_udpate_command()

    def on_clic_OK(self, button):
        if self.entry_command.get_text() == "":
            self.warning_alert(self, "Zone d'information manquante", "Veuillez saisir la commande à passer à cpulimit")
            self.entry_command.grab_focus()
            return None
        else:
            print(self.cmd_shell)
            self.cmd_shell = self.cmd_shell.split(" ")

            command_shell_process = subprocess.Popen(self.cmd_shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, errors = command_shell_process.communicate(input="Hello from the other side!")
            command_shell_process.wait()

            # Recuperer le num du process
            output = output.split(" ")

            msg_process = "Process " + output[-2] + " dead!\n"
            if errors != msg_process:
                self.warning_alert(self, "Des erreurs ont été rencontrées.", errors)

    def gtk_style(self):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(self.pathDir + 'style.css')

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    def warning_alert(self, widget, message1, message2):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CANCEL,
            text=message1,
        )
        dialog.format_secondary_text(message2)
        dialog.run()
        dialog.destroy()


win = cpulimit()
win.connect("destroy", Gtk.main_quit)
win.gtk_style()
win.show_all()
Gtk.main()