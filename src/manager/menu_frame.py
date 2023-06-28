from __future__ import annotations
from typing import TYPE_CHECKING

from functools import partial

import tkinter as tk

from src.manager.frame import Frame

if TYPE_CHECKING:
    from src.manager.manager import Manager


class MenuFrame(Frame):
    def __init__(self, manager: Manager):
        super().__init__(manager, has_menu_btn=False)

    def enter(self, args: dict):
        self.show()

        y = 100
        for controller_index in range(len(self.manager.algo_controllers)):
            controller = self.manager.algo_controllers[controller_index]
            algo_btn = tk.Button(self.content, text=controller.name, command=partial(MenuFrame.algo_btn_handler, self, controller_index))
            algo_btn.place(x=self.manager.window_width / 2 - 30, y=y)

            y += 60

    def leave(self):
        self.hide()

    def algo_btn_handler(self, controller_index: int) -> None:
        self.manager.current_controller = controller_index
        self.manager.change_frame(1, {})
