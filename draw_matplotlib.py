from typing import List, Tuple
import matplotlib.pyplot as plt
import math
from archive.ladder import StraightLadder, Node
from matplotlib.patches import Ellipse, Circle

__all__ = ["LadderDrawer"]


def get_dist(p1: Tuple[float], p2: Tuple[float]):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class LadderDrawer:
    def __init__(
        self, ladder: StraightLadder, padding: Tuple[float] = (0.1, 0.1)
    ) -> None:
        self.line_count = ladder.line_count
        self.line_tracks = ladder.line_tracks
        self.nodes_by_lines = ladder.nodes_by_lines
        # self.result_route_lists = [ladder.get_result_route(i) for i in range(self.line_count)]
        self.padding = padding

    def get_node_alignment(self, padding: Tuple[float]) -> None:
        self.y_start, self.y_end = padding[1], 1 - padding[1]
        self.x_start = padding[0]
        self.x_step = (1 - 2 * padding[0]) / (self.line_count - 1)
        self.node_position = {}
        for i in range(self.line_count):
            node_list = self.nodes_by_lines[i]
            len_nodes = len(node_list)
            y_step = (1 - 2 * padding[1]) / len_nodes
            for idx, node in enumerate(node_list):
                self.node_position[node.node_id] = (
                    self.x_start + i * self.x_step,
                    self.y_end - idx * y_step,
                )

    def get_node_alignment_ellipse(self, padding: Tuple[float], shift=False) -> None:
        self.y_start, self.y_end = padding[1], 1 - padding[1]
        self.x_start = padding[0]
        self.x_step = (1 - 2 * padding[0]) / (self.line_count - 1)
        self.node_position = {}
        for i in range(self.line_count):
            node_list = self.nodes_by_lines[i]
            len_nodes = len(node_list)
            y_step = (1 - 2 * padding[1]) / len_nodes
            for idx, node in enumerate(node_list):
                px, py = self.x_start + i * self.x_step, self.y_end - idx * y_step
                if shift:
                    py -= 0.5 * y_step
                x_sub = (2 * (py - 0.5) / (self.y_end - self.y_start)) ** 2
                px -= (1 - x_sub) ** 0.5 * 0.05
                self.node_position[node.node_id] = (px, py)

    def draw_ghost_leg(self, check_point=False):
        self.get_node_alignment(self.padding)
        fig, ax = plt.subplots(figsize=(5, 5), constrained_layout=True)
        ax.patch.set_facecolor("white")
        ax.set(xlim=(0, 1), ylim=(0, 1), xticks=[], yticks=[])
        for i in range(self.line_count):
            x = self.x_start + i * self.x_step
            ax.plot([x, x], [self.y_start, self.y_end], color="black")

        for i in range(self.line_count):
            node_list: List[Node] = self.nodes_by_lines[i]
            for node in node_list:
                nx, ny = self.node_position[node.node_id]
                if node.is_endpoint:
                    if check_point:
                        circle = Circle(
                            xy=(nx, ny), radius=0.02, zorder=5, color="coral"
                        )
                        ax.add_patch(circle)
                    continue
                opponent = node.hori_after
                if self.line_tracks[node] < self.line_tracks[opponent]:
                    ox, oy = self.node_position[opponent.node_id]
                    ax.plot([nx, ox], [ny, oy], color="black")
                if check_point:
                    circle = Circle(
                        xy=(nx, ny), radius=0.02, zorder=5, color="cadetblue"
                    )
                    ax.add_patch(circle)

        return fig, ax

    def draw_ghost_leg_ellipse(self, check_point=False, shift=False):
        self.get_node_alignment_ellipse(self.padding, shift)
        fig, ax = plt.subplots(figsize=(5, 5), constrained_layout=True)
        ax.patch.set_facecolor("white")
        ax.set(xlim=(0, 1), ylim=(0, 1), xticks=[], yticks=[])
        for i in range(self.line_count):
            x = self.x_start + i * self.x_step
            ellipse = Ellipse(
                xy=(x, (self.y_end + self.y_start) / 2),
                width=0.1,
                height=self.y_start - self.y_end,
                edgecolor="slategray",
                fc="None",
                lw=1,
            )
            ax.add_patch(ellipse)

        for i in range(self.line_count):
            node_list: List[Node] = self.nodes_by_lines[i]
            for node in node_list:
                nx, ny = self.node_position[node.node_id]
                if node.is_endpoint:
                    if check_point:
                        circle = Circle(
                            xy=(nx, ny), radius=0.02, zorder=5, color="coral"
                        )
                        ax.add_patch(circle)
                    continue
                opponent = node.hori_after
                if self.line_tracks[node] < self.line_tracks[opponent]:
                    ox, oy = self.node_position[opponent.node_id]
                    ax.plot([nx, ox], [ny, oy], color="black")
                if check_point:
                    circle = Circle(
                        xy=(nx, ny), radius=0.02, zorder=5, color="cadetblue"
                    )
                    ax.add_patch(circle)

        return fig, ax
