from __future__ import annotations
from typing import TYPE_CHECKING

from functools import partial

import tkinter as tk
import networkx as nx

from src.manager.frame import Frame


if TYPE_CHECKING:
    from src.manager.manager import Manager


class CreateGraphFrame(Frame):
    canvas: tk.Canvas | None

    def __init__(self, manager: Manager):
        super().__init__(manager, CreateGraphFrame.next_handler)

        self.node_radius = 15

        self.nodes = []
        self.edges = []
        self.ids = 0
        self.node_selected = None

        self.canvas = None

    def enter(self, args: dict):
        self.show()

        # clean
        self.nodes = []
        self.edges = []
        self.ids = 0
        self.node_selected = None

        # create frame
        self.canvas = tk.Canvas(self.content, bg='#909090')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", partial(CreateGraphFrame.mouse_handler, self))

    def leave(self):
        self.hide()

    def next_handler(self) -> None:
        graph = nx.Graph()
        graph.add_nodes_from([node["node_id"] for node in self.nodes])
        graph.add_edges_from(self.edges)

        algo_inputs = [(graph, {})]
        self.manager.change_frame(3, {'algo_inputs': algo_inputs})

    def mouse_handler(self, event: tk.Event) -> None:
        click_on = self.get_node(event.x, event.y)

        if click_on is None:
            self.node_selected = None
            self.create_node(event.x, event.y)
        elif self.node_selected is None:
            self.node_selected = click_on
        else:
            if self.node_selected['node_id'] == click_on['node_id']:
                self.delete_node(self.node_selected)
            else:
                self.select_edge(self.node_selected, click_on)

            self.node_selected = None

        self.update_canvas()

    def update_canvas(self) -> None:
        self.canvas.delete('all')
        node_selected_id = None

        if self.node_selected is not None:
            node_selected_id = self.node_selected['node_id']

        for node in self.nodes:
            x = node['x']
            y = node['y']
            node_id = str(node['node_id'])

            self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                    x + self.node_radius, y + self.node_radius,
                                    fill="red" if node['node_id'] == node_selected_id else "blue")

            self.canvas.create_text(x, y, text=node_id, fill="black", font=('Helvetica 15 bold',))

        for edge in self.edges:
            node_a, node_b = [node for node in self.nodes if node["node_id"] in edge]
            self.canvas.create_line(node_a["x"], node_a["y"], node_b["x"], node_b["y"])

    def get_node(self, x: int, y: int) -> dict | None:
        for node in self.nodes:
            if ((node['x'] - x)**2 + (node['y'] - y)**2) <= self.node_radius ** 2:
                return node
        return None

    def create_node(self, x: int, y: int) -> None:
        node_id = self.ids
        node = {
            'node_id': node_id,
            'x': x,
            'y': y
        }

        self.nodes.append(node)
        self.ids += 1

    def delete_node(self, node: dict) -> None:
        node_id = node["node_id"]
        self.edges = [e for e in self.edges if node_id not in e]
        self.nodes = [v for v in self.nodes if v["node_id"] != node_id]
        self.ids = max([-1] + [v["node_id"] for v in self.nodes]) + 1

    def select_edge(self, node_a: dict, node_b: dict) -> None:
        v, w = node_a['node_id'], node_b['node_id']
        e = (min(v, w), max(v, w))
        if e in self.edges:
            self.edges.remove(e)
        else:
            self.edges.append(e)
