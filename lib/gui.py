#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import Tkinter as tk
import tkMessageBox as tkmb
import ttk
import math

from spearman import Model

# tk.Widget.widgets = dict()
tk.Entry.default = ""

FONT = ("Arial", 12)
CUSTOM_LEN = 29

ELEMENTS_NAME = {
    0: "FP1",
    1: "F3",
    2: "C3",
    3: "P3",
    4: "O1",
    5: "F7",
    6: "T3",
    7: "T5",
    8: "FZ",
    9: "PZ",
    10: "A1",
    11: "FP2",
    12: "F4",
    13: "P4",
    14: "C4",
    15: "O2",
    16: "F8",
    17: "F4",
    18: "T6",
    19: "FPZ",
    20: "CZ",
    21: "O7",
    22: "E1",
    23: "E2",
    24: "E3",
    25: "E4",
    26: "-",
    27: "brth",
    28: "res",
    }


class MenuFrame(tk.Frame):
    """ custom Frame"""
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def get_fields(self):
        fields = dict()

        for item in self.widgets.items():
            if isinstance(item[1], tk.Entry):
                field = item[1].get()
                if not field:
                    field = item[1].default
                    item[1].insert(0, field)
                fields[item[0]] = field

        return fields


class GraphCanvas(tk.Canvas):
    """Correlation Graph Canvas"""
    CANVAS_SIZE = 800
    CANVAS_INDENT = 20
    CANVAS_BG_COLOR = "white"
    SMALL_RADIUS = 15
    CONTRA_RADIUS = 30
    # CUSTOM_LEN = 29
    RGB_MASK = "#{red:02X}{green:02X}{blue:02X}"

    def __init__(
            self, frame, height=CANVAS_SIZE, width=CANVAS_SIZE,
            bg=CANVAS_BG_COLOR, size=CANVAS_SIZE,
            shift=CANVAS_INDENT, head=True
            ):

        tk.Canvas.__init__(
            self,
            frame,
            height=height,
            width=width,
            bg=bg
            )

        self.head = head
        self.item_coords = dict()
        self.circles = dict()
        self.clables = dict()
        self.lines = dict()
        self.widgets = dict()
        self.node_number = 0

        self.size = size
        self.shift = shift

    def draw_headfield(self):
        """ draw a human head slice """

        self.widgets["big_oval"] = self.create_oval(
            self.shift, self.shift, self.size-self.shift,
            self.size-self.shift, width=2
            )

        self.widgets["nose"] = self.create_oval(
            self.size/2-10, self.shift/2,
            self.size/2+10, 3*self.shift/2,
            width=0, fill="red"
            )

        self.widgets["ear_left"] = self.create_oval(
            self.shift/2, self.size/2-10,
            3*self.shift/2, self.size/2+10,
            width=0, fill="blue"
            )

        self.widgets["ear_left"] = self.create_oval(
            self.size-3*self.shift/2, self.size/2-10,
            self.size-self.shift/2, self.size/2+10,
            width=0, fill="blue"
            )

    def create(self, number, center=None):
        """ draw relation graph """

        """ draw human head slice """
        if self.head:
            self.draw_headfield()

        angle = 360/number
        radius = (self.CANVAS_SIZE)//2-self.CANVAS_INDENT-self.CONTRA_RADIUS
        small_radius = ((2*math.pi*radius)/number)*0.4

        if small_radius >= self.CONTRA_RADIUS-10:
            small_radius = self.CONTRA_RADIUS-10

        if not center:
            center = [self.CANVAS_SIZE//2]*2
        self.coords = dict.fromkeys(range(number))

        """ calculate coordinates of all circles """
        for index, item in enumerate(self.coords):
            coords = self._circle(
                radius,
                angle*index-180,
                *center
                )
            self.coords[item] = coords

        """ draw graph edges """
        self._draw_edges()

        """ draw graph nodes """
        self._draw_nodes(small_radius)

    def _draw_edges(self):
        """ draw graph edges """
        circles = self.coords.keys()
        for x in circles:
            for y in circles[x+1:]:
                pair_coords = self.coords[x]+self.coords[y]

                self.lines[(x, y)] = self.create_line(
                    *pair_coords,
                    fill="blue", width=1
                    )

    def _draw_nodes(self, radius):
        """ draw graph nodes """
        for item in self.coords.items():
            self._draw_named_circle(
                *item[1], name=item[0], radius=radius,
                custom_name=bool(len(self.coords) == CUSTOM_LEN)
                )

    def _draw_named_circle(
            self, x, y, name,
            radius=SMALL_RADIUS, custom_name=False
            ):
        """ draw circle with it's own name """
        self.circles = dict()
        self.clables = dict()
        self.circles[name] = self.create_oval(
            x-radius,
            y-radius,
            x+radius,
            y+radius,
            width=2,
            fill=self.CANVAS_BG_COLOR
            )

        if custom_name:
            text_name = ELEMENTS_NAME[name]
        else:
            text_name = str(name)

        self.clables[name] = self.create_text(
            x, y, text=text_name
            )

    def _circle(self, r, q, x, y):
        angle = (math.pi/180)*q
        x_cd = x+r*math.sin(angle)
        y_cd = y+r*math.cos(angle)
        return (x_cd, y_cd)

    def refresh(self, update):
        for item in update.items():
            self.itemconfig(
                self.lines[item[0]],
                fill=self.RGB_MASK.format(
                    red=int(255-255*item[1]),
                    green=int(255*item[1]),
                    blue=0
                    )
                )

    def clear(self):
        self.delete("all")
        # map(self.delete, self.circles.values())
        # map(self.delete, self.clables.values())
        # map(self.delete, self.lines.values())

        self.item_coords = dict()
        self.circles = dict()
        self.clables = dict()
        self.lines = dict()


class TableCanvas(tk.Canvas):
    """Correlation Table Canvas"""
    CANVAS_SIZE = 800
    CANVAS_INDENT = 20
    CANVAS_BG_COLOR = "white"
    TRIM_FLOAT = "{0:.{1}f}"
    TRIM_LEN = 2

    def __init__(
            self, frame, height=CANVAS_SIZE, width=CANVAS_SIZE,
            bg=CANVAS_BG_COLOR, shift=CANVAS_INDENT
            ):

        tk.Canvas.__init__(
            self,
            frame,
            height=height,
            width=width,
            bg=bg
            )

        self.node_number = 0

    def create(self, number):

        self.config(
            width=self.CANVAS_INDENT*(number+3),
            height=self.CANVAS_INDENT*(number+3)
            )

        self._create_heders(number)

        self.fields = dict()
        for i in xrange(number):
            for j in xrange(number):
                if i == j:
                    def_text = '1'
                else:
                    def_text = '0'

                self.fields[(i, j)] = self.create_text(
                    self.CANVAS_INDENT*(j+2),
                    self.CANVAS_INDENT*(i+2),
                    text=def_text
                    )

    def _create_heders(self, number):
        self.header = dict()

        for x in xrange(number):
            if number == CUSTOM_LEN:
                name = ELEMENTS_NAME[x]
            else:
                name = str(x)

            self.create_text(
                self.CANVAS_INDENT*(x+2),
                self.CANVAS_INDENT*(1),
                text=name
                )
            self.create_text(
                self.CANVAS_INDENT*(1),
                self.CANVAS_INDENT*(x+2),
                text=name
                )


    def refresh(self, update):
        for item in update.items():
            one = self.fields[item[0]]
            two = self.fields[(item[0][1], item[0][0])]

            self._change_text(one, item[1], 1)
            self._change_text(two, item[1], 1)

    def _change_text(self, widget, text, trim_len=TRIM_LEN):
        self.itemconfig(
            widget,
            text=self.TRIM_FLOAT.format(text, trim_len)
            )

    def clear(self):
        self.delete("all")

        self.fields = dict()


class MatrixFrame(tk.Frame):
    """docstring for MatrixFrame"""
    TRIM_FLOAT = "{0:.{1}f}"
    TRIM_LEN = 3

    def __init__(self, frame):
        tk.Frame.__init__(self, frame)

        self.node_number = 0

    def create(self, number):

        self._craete_headers(number)

        self.vars = dict()
        for i in xrange(number):
            for j in xrange(i, number):
                self.vars[(i, j)] = tk.StringVar()

        self.fields = dict()
        for i in xrange(number):
            for j in xrange(number):
                index = (min(i, j), max(i, j))
                self.fields[(i, j)] = tk.Label(
                    self, textvariable=self.vars[index],
                    width=self.TRIM_LEN+2, bg="white"
                    )
                self.fields[(i, j)].grid(
                    row=i+1, column=j+1, sticky=tk.EW
                    )

        for i in xrange(number):
            self.vars[(i, i)].set('1')

    def _craete_headers(self, number):
        self.header = dict()
        self.header[(0, 0)] = tk.Label(self, text='')

        for x in xrange(number):
            if number == CUSTOM_LEN:
                name = ELEMENTS_NAME[x]
            else:
                name = str(x)

            self.header[(0, x+1)] = tk.Label(
                self, text=name, width=self.TRIM_LEN+2, bg="white"
                )
            self.header[(0, x+1)].grid(row=0, column=x+1, sticky=tk.EW)

            self.header[(x+1, 0)] = tk.Label(
                self, text=name, width=self.TRIM_LEN+2, bg="white"
                )
            self.header[(x+1, 0)].grid(row=x+1, column=0, sticky=tk.EW)

    def refresh(self, update):
        for item in update.items():
            self.vars[item[0]].set(
                self.TRIM_FLOAT.format(item[1], self.TRIM_LEN)
                )

    def clear(self):
        # for entry in self.header.
        for entry in self.grid_slaves():
            entry.grid_forget()

        self.header = dict()
        self.vars = dict()
        self.fields = dict()


class Window(tk.Tk):
    """Main GUI window class"""
    WIDTH_MENU = 50
    TITLE = "Spearman correlation"
    ICON = r"./spearman.ico"

    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_title(self.TITLE)
        self._init_widgets()

    def _init_widgets(self):
        """ init cintainer widgets """
        self.vpan = tk.PanedWindow(self, orient=tk.VERTICAL)
        self.vpan.pack(fill=tk.BOTH, expand=1)

        self.pan = tk.PanedWindow(sashrelief=tk.RAISED)
        self.vpan.add(self.pan)

        self.menu_frame = tk.Frame(self.pan)
        self.pan.add(self.menu_frame)

        # self.canvas_frame = tk.Frame(self.pan)
        # self.pan.add(self.canvas_frame)

        self.visual_frame = tk.Frame(self.pan)
        self.pan.add(self.visual_frame)

        """ status_frame will be added while event called """
        self.status_frame = tk.Frame(self.vpan)

        """ menu tabs """
        self.note = ttk.Notebook(self.menu_frame)
        self.note.pack()

        self.tabs = dict()
        self.tabs["net"] = MenuFrame(self.note)
        self.note.add(self.tabs["net"], text="Net")

        self.tabs["file"] = MenuFrame(self.note)
        self.note.add(self.tabs["file"], text="File")

        """ visualisation tabs """
        self.visual_note = ttk.Notebook(self.visual_frame)
        self.visual_note.pack()

        self.visual_tabs = dict()
        self.visual_tabs["canvas"] = tk.Frame(self.visual_note)
        self.visual_note.add(self.visual_tabs["canvas"], text="Graph")

        self.visual_tabs["table"] = tk.Frame(self.visual_note)
        self.visual_note.add(self.visual_tabs["table"], text="Matrix")

        """ init widgets """
        self._init_net_menu(self.tabs["net"])
        self._init_file_menu(self.tabs["file"])
        self._init_buttons(self.menu_frame)
        self._init_canvas(self.visual_tabs["canvas"], head=False)
        self._init_table(self.visual_tabs["table"])
        self._init_stat_bar(self.status_frame)

    def _init_net_menu(self, frame):
        frame.widgets = dict()
        frame.widgets["label_host"] = tk.Label(
            frame, text="host", font=FONT
            )
        frame.widgets["entry_host"] = tk.Entry(frame, font=FONT)
        frame.widgets["entry_host"].default = "127.0.0.1"

        frame.widgets["label_port"] = tk.Label(
            frame, text="port", font=FONT
            )
        frame.widgets["entry_port"] = tk.Entry(frame, font=FONT)
        frame.widgets["entry_port"].default = "8000"

        frame.widgets["label_frame"] = tk.Label(
            frame, text="frame size", font=FONT
            )
        frame.widgets["entry_frame"] = tk.Entry(frame, font=FONT)
        frame.widgets["entry_frame"].default = "10"

        frame.widgets["label_host"].grid(
            row=0, column=0, columnspan=1, sticky=tk.W
            )
        frame.widgets["entry_host"].grid(
            row=0, column=1, columnspan=2, sticky=tk.W
            )

        frame.widgets["label_port"].grid(
            row=1, column=0, columnspan=1, sticky=tk.W
            )
        frame.widgets["entry_port"].grid(
            row=1, column=1, columnspan=2, sticky=tk.W
            )

        frame.widgets["label_frame"].grid(
            row=2, column=0, columnspan=1, sticky=tk.W
            )
        frame.widgets["entry_frame"].grid(
            row=2, column=1, columnspan=2, sticky=tk.W
            )

    def _init_file_menu(self, frame):
        frame.widgets = dict()
        frame.widgets["label_file"] = tk.Label(
            frame, text="path to file", font=FONT
            )
        frame.widgets["entry_file"] = tk.Entry(frame, font=FONT)
        frame.widgets["entry_file"].default = "input.txt"

        frame.widgets["label_frame"] = tk.Label(
            frame, text="frame size", font=FONT
            )
        frame.widgets["entry_frame"] = tk.Entry(frame, font=FONT)
        frame.widgets["entry_frame"].default = "10"

        frame.widgets["label_file"].grid(
            row=0, column=0, columnspan=1, sticky=tk.W
            )
        frame.widgets["entry_file"].grid(
            row=0, column=1, columnspan=2, sticky=tk.W
            )

        frame.widgets["label_frame"].grid(
            row=1, column=0, columnspan=1, sticky=tk.W
            )
        frame.widgets["entry_frame"].grid(
            row=1, column=1, columnspan=2, sticky=tk.W
            )

    def _init_buttons(self, frame):
        frame.widgets = dict()
        self.btn_start = tk.Button(frame, text="start", font=FONT)
        self.btn_stop = tk.Button(frame, text="stop", font=FONT)

        frame.widgets["button_start"] = self.btn_start
        frame.widgets["button_stop"] = self.btn_stop

        self.btn_start.pack(fill=tk.X)

    def _init_canvas(self, frame, **kwargs):
        frame.widgets = dict()
        frame.widgets["can"] = GraphCanvas(
            frame,
            **kwargs
            )

        self.can = frame.widgets["can"]

        self.can.pack(expand=0)

    def _init_table(self, frame):
        frame.widgets = dict()
        # frame.widgets["table"] = MatrixFrame(frame)
        frame.widgets["table"] = TableCanvas(frame)

        self.table = frame.widgets["table"]

        self.table.pack(fill=tk.BOTH, expand=1)

    def _init_stat_bar(self, frame):
        frame.widgets = dict()
        self.status_msg = tk.StringVar()
        frame.widgets["label"] = tk.Label(
            frame, textvariable=self.status_msg, font=FONT
            )
        self.status_lable = frame.widgets["label"]
        self.status_lable.grid(sticky=tk.W)

    def draw_graph(self, number, center=None):
        self.can.draw_graph(number, center)

    def renew_colors(self, update):
        self.can.renew_colors(update)

    def clear_graph(self):
        self.can.clear_graph()

    def event_start(self, event):
        self.fields_down()

    def event_stop(self, event):
        self.fields_up()

    def fields_down(self):
        current_tab = self._get_current_tab()
        for widget in current_tab.widgets.values():
            widget.config(state=tk.DISABLED)
        self.btn_start.pack_forget()
        self.btn_stop.pack(fill=tk.X)

    def fields_up(self):
        current_tab = self._get_current_tab()
        for widget in current_tab.widgets.values():
            widget.config(state=tk.NORMAL)
        self.btn_stop.pack_forget()
        self.btn_start.pack(fill=tk.X)

    def get_fields(self):
        current_tab = self._get_current_tab()
        fields = current_tab.get_fields()
        return fields

    def _get_current_tab(self):
        return self.tabs.get(self.get_current_tab_name())

    def get_current_tab_name(self):
        return self.note.tab(self.note.select(), "text").lower()

    def msg_info(self, message, title="Info"):
        tkmb.showinfo(title=title, message=message)

    def msg_warning(self, message, title="Warning"):
        tkmb.showwarning(title=title, message=message)

    def msg_error(self, message, title="Error"):
        tkmb.showerror(title=title, message=message)

    def msg_status(self, message):
        self.vpan.add(self.status_frame)
        self.status_msg.set(message)

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
        self.view.btn_start.bind(
            "<Button-1>", self.event_start
            )

        self.view.btn_stop.bind(
            "<Button-1>", self.event_stop
            )
        self.view.bind("<<Stop>>", self.event_stop)

    def event_start(self, event):
        """ Event: called when main
            calculation loop starts """

        self.view.event_start(event)
        self.run_state = True
        print("event start")

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

        self.stop_spearman()

    def run(self):
        """ start gui event loop """
        self.view.mainloop()

    def start_spearman(self):
        """ prepare calculation core object """
        fields = self.view.get_fields()
        """ start calculation with input fields data """
        result = self.model.start_spearman(
            self.view.get_current_tab_name(),
            **fields
            )
        if not result:
            self.view.msg_error("Error while connecting")
        return result

    def calculate_loop(self):
        """ calculate some data package (one iteration) """
        full_dict = self.model.calculate_loop()
        if full_dict and self.run_state:
            self._check_refresh(self.view.can, full_dict["keys"])
            # if full_dict["keys"] != self.view.can.node_number:
            #     self.view.can.node_number = full_dict["keys"]
            #     self.view.can.clear()
            #     self.view.can.create(full_dict["keys"])

            self._check_refresh(self.view.table, full_dict["keys"])
            # if full_dict["keys"] != self.view.table.node_number:
            #     self.view.table.node_number = full_dict["keys"]
            #     self.view.table.clear()
            #     self.view.table.create(full_dict["keys"])

            self.view.can.refresh(full_dict["kfs"])
            self.view.table.refresh(full_dict["kfs"])

            self.view.after_idle(self.calculate_loop)

        elif self.run_state:
            self.view.event_generate("<<Stop>>")

    def stop_spearman(self):
        """ stop calculation """
        self.model.stop_spearman()

    def _check_refresh(self, widget, number):
        if number != widget.node_number:
            widget.node_number = number
            widget.clear()
            widget.create(number)


def main():
    presenter = Presenter()
    presenter.run()


if __name__ == '__main__':
    main()
