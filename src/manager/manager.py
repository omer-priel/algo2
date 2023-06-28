# the manager window

import tkinter as tk

from src.infra.algo_controller import AlgoController

from src.manager.frame import Frame
from src.manager.menu_frame import MenuFrame
from src.manager.select_frame import SelectFrame
from src.manager.create_graph_frame import CreateGraphFrame
from src.manager.tracker_frame import TrackerFrame


class Manager:
    def __init__(self, window_width: int, window_height: int, algo_controllers: list[AlgoController]) -> None:
        self.window_width = window_width
        self.window_height = window_height
        self.algo_controllers = algo_controllers

        self.current_controller = -1
        self.displayed_frame = 0

        self.window = tk.Tk()
        self.window.title("Manager")
        self.window.resizable(width=False, height=False)
        self.window.geometry('{}x{}'.format(self.window_width, self.window_height))

        self.frames: list[Frame] = [MenuFrame(self), SelectFrame(self), CreateGraphFrame(self), TrackerFrame(self)]

        self.frames[0].enter({})

    def run(self) -> None:
        self.window.mainloop()

    def change_frame(self, index: int, args: dict):
        self.frames[self.displayed_frame].leave()
        self.displayed_frame = index
        self.frames[self.displayed_frame].enter(args)

