
from PIL import ImageTk

from src.infra.step import Step


class Tracker:
    steps: list[tuple[ImageTk.PhotoImage, str]]

    def __init__(self):
        self.steps = []

    def add_step(self, step: Step):
        self.steps.append(step.compile())
