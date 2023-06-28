from __future__ import annotations
from typing import TYPE_CHECKING

from functools import partial

import networkx as nx
import tkinter as tk

from src.manager.frame import Frame
from src.tracker.tracker import Tracker


if TYPE_CHECKING:
    from src.manager.manager import Manager


class TrackerFrame(Frame):
    trackers: list[Tracker]
    selected_tracker: tk.StringVar | None = None
    selected_tracker_index: int = 0
    selected_step: tk.StringVar | None = None
    selected_step_index: list[int]
    text_var: tk.StringVar | None = None

    canvas: tk.Canvas | None = None
    text_bord: tk.Label | None = None
    text_bord_h: int = 50

    def __init__(self, manager: Manager):
        super().__init__(manager)

        self.trackers = []
        self.selected_step_index = []

    def enter(self, args: dict) -> None:
        self.show()

        self.trackers = []
        self.selected_step_index = []

        controller = self.manager.algo_controllers[self.manager.current_controller]
        algo_inputs: list[tuple[nx.Graph, dict]] = args["algo_inputs"]

        if len(algo_inputs) == 0:
            self.manager.change_frame(0, {})
            return

        # running the algo on inputs
        self.content.update()

        running_label = tk.Label(self.content, text="Running")
        running_label.pack()
        running_label.place(x=self.content.winfo_width() / 2 - 20, y=self.content.winfo_height() / 2)
        running_label.update()

        for algo_input_index in range(len(algo_inputs)):
            graph, args = algo_inputs[algo_input_index]

            running_label.configure(text="Running - {} / {}".format(algo_input_index, len(algo_inputs)))
            running_label.update()

            # run the algo
            algo = controller.run()
            res = algo.run(graph, args)
            print(res)

            tracker = algo.get_tracker()
            if len(tracker.steps) > 0:
                self.trackers.append(tracker)
                self.selected_step_index.append(0)

        if len(self.trackers) == 0:
            running_label.configure(text="Ended without trackers!")
            return

        running_label.destroy()


        # present the results
        self.selected_tracker = tk.StringVar()
        self.selected_tracker.set('1')
        self.selected_tracker.trace("w", partial(TrackerFrame.tracker_changed, self))
        self.selected_step = tk.StringVar()
        self.selected_step.set('1')
        self.text_var = tk.StringVar()
        self.text_var.set('')

        # add menubar elements
        x = self.tab_w

        label = tk.Label(self.menubar, text="Graph:")
        label.pack()
        label.place(x=x, y=self.tab_h)
        label.update()
        x += label.winfo_width() + self.tab_w

        drop = tk.OptionMenu(self.menubar, self.selected_tracker, *[str(i+1) for i in range(len(self.trackers))])
        drop.pack()
        drop.place(x=x, y=self.tab_h)
        drop.update()
        x += drop.winfo_width() + self.tab_w

        btn = tk.Button(self.menubar, text="Prev Graph", bg="blue", command=partial(self.prev_tracker_handler, self))
        btn.pack()
        btn.place(x=x, y=self.tab_h)
        btn.update()
        x += btn.winfo_width() + self.tab_w

        btn = tk.Button(self.menubar, text="Next Graph", bg="green", command=partial(self.next_tracker_handler, self))
        btn.pack()
        btn.place(x=x, y=self.tab_h)
        btn.update()
        x += btn.winfo_width() + self.tab_w

        label = tk.Label(self.menubar, text="Step:")
        label.pack()
        label.place(x=x, y=self.tab_h)
        label.update()
        x += label.winfo_width() + self.tab_w

        entry = tk.Entry(self.menubar, textvariable=self.selected_step, width=8)
        entry.pack()
        entry.place(x=x, y=self.tab_h)
        entry.update()
        entry.bind("<Return>", partial(TrackerFrame.step_changed, self))
        x += entry.winfo_width() + self.tab_w

        btn = tk.Button(self.menubar, text="Prev", bg="blue", command=partial(self.prev_step_handler, self))
        btn.pack()
        btn.place(x=x, y=self.tab_h)
        btn.update()
        x += btn.winfo_width() + self.tab_w

        btn = tk.Button(self.menubar, text="Next", bg="green", command=partial(self.next_step_handler, self))
        btn.pack()
        btn.place(x=x, y=self.tab_h)
        btn.update()
        x += btn.winfo_width() + self.tab_w

        # create content
        self.content.update()

        self.canvas = tk.Canvas(self.content, width=self.content.winfo_width(), height=self.content.winfo_height() - self.text_bord_h)
        self.canvas.pack(side=tk.TOP)

        self.text_bord = tk.Label(self.content, textvariable=self.text_var)
        self.text_bord.pack(side=tk.BOTTOM)
        self.text_bord.update()

        self.update_borad()

    def leave(self):
        self.hide()

        if self.selected_tracker is not None:
            self.selected_tracker.set('')
            self.selected_tracker = None

        if self.selected_step is not None:
            self.selected_step.set('')
            self.selected_step = None

        if self.text_var is not None:
            self.text_var.set('')
            self.text_var = None

    def get_tracker_index(self) -> int:
        return self.selected_tracker_index

    def get_step_index(self) -> int:
        return self.selected_step_index[self.get_tracker_index()]

    def tracker_changed(self, var: tk.StringVar, index: int, mode: str):
        if not self.showed:
            return

        try:
            num = int(self.selected_tracker.get()) - 1
            if num < 0:
                self.selected_tracker_index = 0
            elif num >= len(self.trackers):
                self.selected_tracker_index = len(self.trackers) - 1
            else:
                self.selected_tracker_index = num
                self.selected_step.set(str(self.get_step_index() + 1))
                self.update_borad()
                return
        except:
            pass

        self.selected_tracker.set(str(self.get_tracker_index() + 1))
        self.selected_step.set(str(self.get_step_index() + 1))
        self.update_borad()

    def step_changed(self, event: tk.Event):
        if not self.showed:
            return

        try:
            num = int(self.selected_step.get()) - 1
            if num < 0:
                self.selected_step_index[self.get_tracker_index()] = 0
            elif num >= len(self.trackers[self.get_tracker_index()].steps):
                self.selected_step_index[self.get_tracker_index()] = len(self.trackers[self.get_tracker_index()].steps) - 1
            else:
                self.selected_step_index[self.get_tracker_index()] = num
                self.update_borad()
                return
        except:
            pass

        self.selected_step.set(str(self.get_step_index() + 1))
        self.update_borad()

    def update_borad(self):
        if not self.showed:
            return

        img, text = self.trackers[self.get_tracker_index()].steps[self.get_step_index()]

        self.canvas.update()

        x = int(self.canvas.winfo_width() / 2)
        y = int(self.canvas.winfo_height() / 2)

        self.canvas.destroy()

        self.canvas = tk.Canvas(self.content, width=self.content.winfo_width(), height=self.content.winfo_height() - self.text_bord_h)
        self.canvas.pack(side=tk.TOP)

        self.canvas.create_image(x, y, image=img)
        self.canvas.update()

        self.text_var.set(text)

    def prev_tracker_handler(self, event: tk.Event):
        if not self.showed:
            return

        i = self.get_tracker_index() - 1

        if i >= 0:
            self.selected_tracker.set(str(i + 1))
            self.update_borad()

    def next_tracker_handler(self, event: tk.Event):
        if not self.showed:
            return

        i = self.get_tracker_index() + 1

        if i < len(self.trackers):
            self.selected_tracker.set(str(i + 1))
            self.update_borad()

    def prev_step_handler(self, event: tk.Event):
        if not self.showed:
            return

        j = self.get_tracker_index()
        i = self.get_step_index() - 1

        if i >= 0:
            self.selected_step_index[j] = i
            self.selected_step.set(str(i + 1))
            self.update_borad()

    def next_step_handler(self, event: tk.Event):
        if not self.showed:
            return

        j = self.get_tracker_index()
        i = self.get_step_index() + 1

        if i < len(self.trackers[j].steps):
            self.selected_step_index[j] = i
            self.selected_step.set(str(i + 1))
            self.update_borad()


