#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import Tkinter as tk
import tkMessageBox as tkmb
# import ttk
import math

from spearman import Model

tk.Widget.widgets = dict()


class Window(tk.Tk):
    """Main window class"""
    WIDTH_MENU = 50
    CANVAS_SIZE = 500
    CANVAS_INDENT = 20
    CANVAS_BG_COLOR = "white"
    SMALL_RADIUS = 15
    CONTRA_RADIUS = 30
    TITLE = "Spearman correlation"
    ICON = r"./spearman.ico"
    RGB_MASK = "#{red:02X}{green:02X}{blue:02X}"
    FONT = ("Arial", 12)

    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_title(self.TITLE)
        self._init_widgets()

    def _init_widgets(self):
        self.vpan = tk.PanedWindow(self, orient=tk.VERTICAL)

        self.pan = tk.PanedWindow(sashrelief=tk.RAISED)
        self.status_frame = tk.Frame(self.vpan)

        self.vpan.add(self.pan)

        self.vpan.pack(fill=tk.BOTH, expand=1)

        self.menu_frame = tk.Frame(self.pan)
        self.canvas_frame = tk.Frame(self.pan)

        self.pan.add(self.menu_frame)
        self.pan.add(self.canvas_frame)

        # self.menu_frame.pack(side='left', fill='y')
        # self.canvas_frame.pack(side='right', fill='both')

        self._init_menu(self.menu_frame)
        self._init_canvas(self.canvas_frame)
        self._init_stat_bar(self.status_frame)

    def _init_menu(self, frame):
        frame.widgets["label_host"] = tk.Label(self.menu_frame, text="host", font=self.FONT)
        frame.widgets["entry_host"] = tk.Entry(self.menu_frame, font=self.FONT)

        frame.widgets["label_port"] = tk.Label(self.menu_frame, text="port", font=self.FONT)
        frame.widgets["entry_port"] = tk.Entry(self.menu_frame, font=self.FONT)

        frame.widgets["label_frame"] = tk.Label(self.menu_frame, text="frame size", font=self.FONT)
        frame.widgets["entry_frame"] = tk.Entry(self.menu_frame, font=self.FONT)

        frame.widgets["button_start"] = tk.Button(self.menu_frame, text="start", font=self.FONT)
        frame.widgets["button_start"].bind("<Button-1>", self.event_start)

        frame.widgets["button_stop"] = tk.Button(self.menu_frame, text="stop", font=self.FONT)
        frame.widgets["button_stop"].bind("<Button-1>", self.event_stop)

        frame.widgets["label_host"].grid(row=0, column=0, columnspan=1, sticky=tk.W)
        frame.widgets["entry_host"].grid(row=0, column=1, columnspan=2, sticky=tk.W)

        frame.widgets["label_port"].grid(row=1, column=0, columnspan=1, sticky=tk.W)
        frame.widgets["entry_port"].grid(row=1, column=1, columnspan=2, sticky=tk.W)

        frame.widgets["label_frame"].grid(row=2, column=0, columnspan=1, sticky=tk.W)
        frame.widgets["entry_frame"].grid(row=2, column=1, columnspan=2, sticky=tk.W)

        frame.widgets["button_start"].grid(row=3, column=0, columnspan=3, sticky=tk.EW)

    def _init_canvas(self, frame, size=CANVAS_SIZE, shift=CANVAS_INDENT):
        frame.widgets["can"] = tk.Canvas(
            frame,
            height=size,
            width=size,
            bg=self.CANVAS_BG_COLOR
            )

        self.can = frame.widgets["can"]

        self.can.item_coords = dict()
        self.can.circles = dict()
        self.can.clables = dict()
        self.can.lines = dict()
        self.can.node_number = 0

        self.size = size
        self.shift = shift

        self.draw_headfield()

        self.can.pack(fill=tk.BOTH, expand=1)

    def _init_stat_bar(self, frame):
        self.status_msg = tk.StringVar()
        frame.widgets["label"] = tk.Label(
            frame, textvariable=self.status_msg, font=self.FONT
            )
        self.status_lable = frame.widgets["label"]
        self.status_lable.grid(sticky=tk.W)

    def draw_headfield(self):
        self.can.widgets["big_oval"] = self.can.create_oval(
            self.shift, self.shift, self.size-self.shift, self.size-self.shift, width=2
            )

        self.can.widgets["nose"] = self.can.create_oval(
            self.size/2-10, self.shift/2, self.size/2+10, 3*self.shift/2,
            width=0, fill="red"
            )

        self.can.widgets["ear_left"] = self.can.create_oval(
            self.shift/2, self.size/2-10, 3*self.shift/2, self.size/2+10,
            width=0, fill="blue"
            )

        self.can.widgets["ear_left"] = self.can.create_oval(
            self.size-3*self.shift/2, self.size/2-10, self.size-self.shift/2, self.size/2+10,
            width=0, fill="blue"
            )

    def draw_graph(self, number, center=None):
        angle = 360/number
        radius = (self.CANVAS_SIZE)//2-self.CANVAS_INDENT-self.CONTRA_RADIUS
        small_radius = ((2*math.pi*radius)/number)*0.4

        if small_radius >= self.CONTRA_RADIUS-10:
            small_radius = self.CONTRA_RADIUS-10

        if not center:
            center = [self.CANVAS_SIZE//2]*2
        self.coords = dict.fromkeys(range(number))

        # calculate coordinates of all circles
        for index, item in enumerate(self.coords):
            coords = self.circle(
                radius,
                angle*index-180,
                *center
                )
            self.coords[item] = coords

        # draw graph edges
        self.draw_edges()

        # draw graph nodes
        self.draw_nodes(small_radius)

    def draw_edges(self):
        # self.can.lines = dict()
        circles = self.coords.keys()
        for x in circles:
            for y in circles[x+1:]:
                pair_coords = self.coords[x]+self.coords[y]

                self.can.lines[(x, y)] = self.can.create_line(
                    # *self.get_shift(*pair_coords),
                    *pair_coords,
                    fill="blue", width=2
                    )

    def draw_nodes(self, radius):
        for item in self.coords.items():
            self.draw_named_circle(*item[1], name=item[0], radius=radius)

    def draw_named_circle(self, x, y, name, radius=SMALL_RADIUS):
        self.can.circles = dict()
        self.can.clables = dict()
        self.can.circles[name] = self.can.create_oval(
            x-radius,
            y-radius,
            x+radius,
            y+radius,
            width=2,
            fill=self.CANVAS_BG_COLOR
            )

        self.can.clables[name] = self.can.create_text(
            x, y, text=str(name)
            )

    def circle(self, r, q, x, y):
        angle = (math.pi/180)*q
        x_cd = x+r*math.sin(angle)
        y_cd = y+r*math.cos(angle)
        return (x_cd, y_cd)

    def renew_colors(self, update):
        for item in update.items():
            self.can.itemconfig(
                self.can.lines[item[0]],
                fill=self.RGB_MASK.format(
                    red=int(255-255*item[1]),
                    green=int(255*item[1]),
                    blue=0
                    )
                )

    def clear_graph(self):
        # self.can.delete("all")
        map(self.can.delete, self.can.circles.values())
        map(self.can.delete, self.can.clables.values())
        map(self.can.delete, self.can.lines.values())

        self.can.item_coords = dict()
        self.can.circles = dict()
        self.can.clables = dict()
        self.can.lines = dict()

    def event_start(self, event):
        self.fields_down()

    def event_stop(self, event):
        self.fields_up()

    def fields_down(self):
        self.menu_frame.widgets["entry_host"].config(state=tk.DISABLED)
        self.menu_frame.widgets["entry_port"].config(state=tk.DISABLED)
        self.menu_frame.widgets["entry_frame"].config(state=tk.DISABLED)
        self.menu_frame.widgets["button_start"].grid_remove()
        self.menu_frame.widgets["button_stop"].grid(
            row=3, column=0, columnspan=3, sticky=tk.EW
            )

    def fields_up(self):
        self.menu_frame.widgets["entry_host"].config(state=tk.NORMAL)
        self.menu_frame.widgets["entry_port"].config(state=tk.NORMAL)
        self.menu_frame.widgets["entry_frame"].config(state=tk.NORMAL)
        self.menu_frame.widgets["button_stop"].grid_remove()
        self.menu_frame.widgets["button_start"].grid(
            row=3, column=0, columnspan=3, sticky=tk.EW
            )

    def get_fields(self):
        entry_host = self.menu_frame.widgets["entry_host"].get()
        entry_port = self.menu_frame.widgets["entry_port"].get()
        entry_frame = self.menu_frame.widgets["entry_frame"].get()

        fields = (
            ["127.0.0.1", entry_host][bool(entry_host)],
            int([8000, entry_port][bool(entry_port)]),
            int([10, entry_frame][bool(entry_frame)]),
            )
        return fields

    def msg_info(self, message, title="Info"):
        tkmb.showinfo(title=title, message=message)

    def msg_warning(self, message, title="Warning"):
        tkmb.showwarning(title=title, message=message)

    def msg_error(self, message, title="Error"):
        tkmb.showerror(title=title, message=message)

    def msg_status(self, message):
        self.vpan.add(self.status_frame)
        self.status_msg.set(message)
        # self.status_lable.grid()

    def status_clear(self):
        self.vpan.forget(self.status_frame)
        self.status_msg.set("")


class Presenter(object):
    """Processing presenter"""

    def __init__(self):
        self.view = Window()
        self.model = Model()
        self.run_state = None

        self._bind_view_events()

    def _bind_view_events(self):
        self.view.menu_frame.widgets["button_start"].bind(
            "<Button-1>", self.event_start
            )

        self.view.menu_frame.widgets["button_stop"].bind(
            "<Button-1>", self.event_stop
            )
        self.view.bind("<<Stop>>", self.event_stop)

    def event_start(self, event):
        """ Event: called when main
            calculation loop starts """

        self.view.event_start(event)
        self.run_state = True
        print("event start")
        # self.view.msg_status("test")

        start = self.start_spearman()

        if start:
            self.view.after_idle(self.calculate_loop)
        else:
            self.view.event_generate("<<Stop>>")

    def event_stop(self, event):
        """ Event: called when main
            calculation loop ends """

        self.view.event_stop(event)
        self.run_state = False
        print("event stop")
        # self.view.status_clear()

    def run(self):
        self.view.mainloop()

    def start_spearman(self):
        fields = self.view.get_fields()
        result = self.model.start_spearman(*fields)
        if not result:
            self.view.msg_error(
                "Error while connecting {host}:{port}".format(
                    fields[0], fields[1]
                    )
                )
        return result

    def calculate_loop(self):
        full_dict = self.model.calculate_loop()
        if full_dict and self.run_state:
            if full_dict["keys"] != self.view.can.node_number:
                self.view.can.node_number = full_dict["keys"]
                self.view.clear_graph()
                self.view.draw_graph(full_dict["keys"])

            self.view.renew_colors(full_dict["kfs"])

            self.view.after_idle(self.calculate_loop)

        elif self.run_state:
            self.view.event_generate("<<Stop>>")

    def stop_spearman(self):
        self.model.stop_spearman()


def main():
    presenter = Presenter()
    presenter.run()


if __name__ == '__main__':
    main()
