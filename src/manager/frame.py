# Frame of Manager
from __future__ import annotations
from typing import TYPE_CHECKING

from typing import Any, Callable

from functools import partial

import tkinter as tk

if TYPE_CHECKING:
    from src.manager.manager import Manager


class Frame:
    frame: tk.Frame | None = None
    content: tk.Frame | None = None
    menubar: tk.Frame | None = None
    menu_btn: tk.Button | None = None
    next_btn: tk.Button | None = None
    showed: bool

    def __init__(self, manager: Manager,
                 next_handler: Callable[[Any], None] | None = None, has_menu_btn: bool = True,
                 tab_w: int = 10, tab_h: int = 20):
        self.manager = manager
        self.has_menu_btn = has_menu_btn
        self.next_handler = next_handler
        self.tab_w = tab_w
        self.tab_h = tab_h
        self.button_w = 56
        self.button_h = 25

        self.showed = False

        self.frame = None
        self.content = None
        self.menubar = None
        self.menu_btn = None
        self.next_btn = None

    def menu_handler(self) -> None:
        self.manager.change_frame(0, {})

    def show(self):
        self.showed = True

        self.frame = tk.Frame(self.manager.window)
        self.frame.pack()
        self.frame.pack_propagate(False)
        self.frame.configure()
        self.frame.place(x=0, y=0)
        self.frame.configure(width=self.manager.window_width, height=self.manager.window_height)

        self.content = tk.Frame(self.frame)
        self.content.pack()
        self.content.pack_propagate(False)
        self.content.place(x=0, y=0)
        self.content.configure(width=self.manager.window_width, height=self.manager.window_height - 2 * self.tab_h - self.button_h)
        self.content.place(x=0, y=0)

        self.menubar = tk.Frame(self.frame)
        self.menubar.pack()
        self.menubar.pack_propagate(False)
        self.menubar.place(x=0, y=self.manager.window_height - 2 * self.tab_h - self.button_h)
        self.menubar.configure(width=self.manager.window_width, height=2 * self.tab_h + self.button_h)

        if self.has_menu_btn:
            self.menu_btn = tk.Button(self.menubar, text="Menu", bg="blue", command=partial(Frame.menu_handler, self))
            self.menu_btn.place(x=self.manager.window_width - self.button_w - self.tab_w, y=self.tab_h)

        if self.next_handler is not None:
            self.next_btn = tk.Button(self.menubar, text="Next", bg="green", command=partial(self.next_handler, self))
            self.next_btn.place(x=self.manager.window_width - 2 * self.button_w - 2 * self.tab_w, y=self.tab_h)

    def hide(self):
        self.showed = False

        self.content.destroy()
        self.menubar.destroy()
        self.frame.destroy()

        self.content = None
        self.menubar = None
        self.frame = None
        self.menu_btn = None
        self.next_btn = None

    def enter(self, args: dict):
        pass

    def leave(self):
        pass
