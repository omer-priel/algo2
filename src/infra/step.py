
import abc

import io

from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import networkx as nx


DrawReturn = tuple[plt.Figure, str] | tuple[None, str]


class Step(abc.ABC):
    @abc.abstractmethod
    def compile(self) -> tuple[ImageTk.PhotoImage, str]:
        pass


class PlotStep(Step):
    @abc.abstractmethod
    def draw(self) -> DrawReturn:
        pass

    def compile(self) -> tuple[ImageTk.PhotoImage, str]:
        fig, text = self.draw()

        if fig is None:
            fig = plt.gcf()

        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = ImageTk.PhotoImage(Image.open(buf))

        plt.figure().clear()
        plt.close()
        plt.cla()
        plt.clf()

        return img, text


class GraphStep(PlotStep):
    def __init__(self, graph: nx.Graph, text: str = ""):
        self.graph = graph.copy()
        self.text = text

    def draw(self) -> DrawReturn:
        nx.draw_networkx(self.graph)
        return None, self.text
