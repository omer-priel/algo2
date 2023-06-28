from __future__ import annotations
from typing import TYPE_CHECKING

from functools import partial

import tkinter as tk

from src.infra.algo_controller import AlgoTest
from src.manager.frame import Frame


if TYPE_CHECKING:
    from src.manager.manager import Manager


class SelectFrame(Frame):
    params_boxs: dict[str, dict[str, tk.StringVar]]

    def __init__(self, manager: Manager):
        super().__init__(manager)

        self.params_boxs = {}

    def enter(self, args: dict):
        self.show()

        controller = self.manager.algo_controllers[self.manager.current_controller]

        create_graph_btn = tk.Button(self.content, text="Create Custom Graph", command=partial(SelectFrame.create_graph_handler, self))
        create_graph_btn.place(x=self.manager.window_width / 2 - 50, y=100)

        y = 150

        for test in controller.tests:
            self.params_boxs[test.test_name] = {}

            x = 40

            create_graph_btn = tk.Button(self.content, text=test.test_name,
                                         command=partial(SelectFrame.test_handler, self, test))
            create_graph_btn.place(x=x, y=y)
            create_graph_btn.update()

            x_start = x + create_graph_btn.winfo_width() + 10
            x = x_start
            for test_param in test.params:
                self.content.update()
                if x + 150 > self.content.winfo_width():
                    x = x_start
                    y += 40

                label = tk.Label(self.content, text=test_param.key + ":")
                label.pack()
                label.place(x=x, y=y)
                label.update()
                x += label.winfo_width() + 5

                text_box = tk.StringVar()
                text_box.set(test_param.converter(test_param.default_value))
                if test_param.converter == bool:
                    entry = tk.Checkbutton(self.content, text='', variable=text_box, onvalue='1', offvalue='0')
                else:
                    entry = tk.Entry(self.content, textvariable=text_box, width=8)
                entry.pack()
                entry.place(x=x, y=y)
                entry.update()
                x += entry.winfo_width() + 10

                self.params_boxs[test.test_name][test_param.key] = text_box

            y += 40

    def leave(self):
        self.hide()

        for test_name in self.params_boxs:
            for parm_key in self.params_boxs[test_name]:
                self.params_boxs[test_name][parm_key].set('')

    def create_graph_handler(self):
        self.manager.change_frame(2, {})

    def test_handler(self, test: AlgoTest):
        params_valuses = {}
        for param in test.params:
            params_valuses[param.key] = param.converter(self.params_boxs[test.test_name][param.key].get())

        algo_inputs = test.test_generator(**params_valuses)
        self.manager.change_frame(3, {'algo_inputs': algo_inputs})
