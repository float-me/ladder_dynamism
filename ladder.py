from typing import Self, Dict, List, Tuple, Callable


def uniform_P(_):
    return 0.5


class Ladder:
    def __init__(self) -> None:
        self.nodes: Dict[int, "Node"] = {}
        self.node_count: int = 0
        self.n: int = 0
        self.d: int = 0
        self._fix: bool = False

    def fix(self):
        assert self.d > 0
        assert self.n > 0
        self._fix = True
        self.r = 0.5 * self.d / self.n

    def unfix(self):
        self._fix = False

    def add_cycle(self, *names: str) -> List["Node"]:
        nodes = [Node(name, self) for name in names]
        Node.vert_cycle(*nodes)
        return nodes

    def insert_under(
        self, u: "Node", v: "Node", name1: str, name2: str
    ) -> List["Node"]:
        u_under, v_under = Node(name1, self), Node(name2, self)
        u.vert_connect(u_under)
        v.vert_connect(v_under)
        u_under.hori_connect(v_under)
        return [u_under, v_under]

    def get_unpred(self, P: Callable[[Self], float]):
        assert self._fix
        result_dict = {}
        for node_id, node in self.nodes.items():
            if node.is_endpoint:
                continue
            result_dict[node_id] = node.unpredictability_once(P)

        def P_new(node: "Node"):
            return result_dict[node.node_id]

        return P_new

    def get_unpred_steps(self, steps: int):
        assert self._fix
        P = uniform_P
        for _ in range(steps):
            P = self.get_unpred(P)

        return P

    def dynamism(self, steps: int):
        assert self._fix
        P = self.get_unpred_steps(steps)

        dyna_sum = 0
        for node in self.nodes.values():
            if not node.is_endpoint:
                dyna_sum += node.unpredictability_once(P)
        return dyna_sum / self.d

    def dynamisms(self, steps: int):
        assert self._fix
        P = uniform_P
        dyna_sums = []
        for _ in range(steps):
            P = self.get_unpred(P)
            dyna_sum = 0
            for node in self.nodes.values():
                if not node.is_endpoint:
                    dyna_sum += node.unpredictability_once(P)
            dyna_sums.append(dyna_sum / self.d)

        return dyna_sums


class Node:
    def vert_cycle(*nodes: Self) -> None:
        size = len(nodes)
        for i in range(size - 1):
            nodes[i].vert_connect(nodes[i + 1])

    def __init__(self, name, ladder: Ladder) -> None:
        self.name = name
        self.ladder = ladder

        self.node_id = ladder.node_count
        ladder.node_count += 1

        self.hori_before_id = self.node_id
        self.hori_after_id = self.node_id
        self.vert_before_id = self.node_id
        self.vert_after_id = self.node_id

        ladder.nodes[self.node_id] = self
        ladder.n += 1
        self.soloed_before_id = -1

    def __str__(self) -> str:
        return f"Node({self.name})"

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self):
        return hash(self.node_id)

    def hori_connect(self, other: Self):
        # ladder of self and other should be same
        after = self.hori_after
        before = other.hori_before

        if not self.ladder._fix:
            s = set([self, other, after, before])
            for node in s:
                if node.is_endpoint:
                    self.ladder.n -= 1
                else:
                    self.ladder.d -= 1

        self.hori_after_id = other.node_id
        other.hori_before_id = self.node_id
        after.hori_before_id = before.node_id
        before.hori_after_id = after.node_id

        if not self.ladder._fix:
            s = set([self, other, after, before])
            for node in s:
                if node.is_endpoint:
                    self.ladder.n += 1
                else:
                    self.ladder.d += 1

    def twist(self, other: Self):
        after = other.hori_after
        self.hori_connect(after)
        after.hori_connect(self)

    def vert_connect(self, other: Self):
        after = self.vert_after
        before = other.vert_before
        self.vert_after_id = other.node_id
        other.vert_before_id = self.node_id
        after.vert_before_id = before.node_id
        before.vert_after_id = after.node_id

    @property
    def is_endpoint(self):
        return self.hori_before_id == self.node_id

    @property
    def hori_after(self):
        return self.ladder.nodes[self.hori_after_id]

    @property
    def hori_before(self):
        return self.ladder.nodes[self.hori_before_id]

    @property
    def vert_after(self):
        return self.ladder.nodes[self.vert_after_id]

    @property
    def vert_before(self):
        return self.ladder.nodes[self.vert_before_id]

    def solo(self):
        before, after = self.hori_before, self.hori_after
        before.hori_connect(after)
        self.soloed_before_id = before.node_id

    def unsolo(self):
        before = self.ladder.nodes[self.soloed_before_id]
        before.hori_connect(self)
        self.soloed_before_id = -1

    def fold(self, P: Callable[[Self], float]):
        assert self.is_endpoint
        assert self.ladder._fix

        va = self.vert_after
        if va.is_endpoint:
            return 0

        hva = va.hori_after
        p = P(va)
        result = 1
        va.solo()
        result += p * va.fold(P)
        va.unsolo()
        hva.solo()
        result += (1 - p) * hva.fold(P)
        hva.unsolo()

        return result

    def fold_invert(self, P: Callable[[Self], float]):
        assert self.is_endpoint
        assert self.ladder._fix

        va = self.vert_before
        if va.is_endpoint:
            return 0

        hva = va.hori_before
        p = P(va)
        result = 1
        va.solo()
        result += p * va.fold_invert(P)
        va.unsolo()
        hva.solo()
        result += (1 - p) * hva.fold_invert(P)
        hva.unsolo()

        return result

    def unpredictability_once(self, P: Callable[[Self], float]):
        assert self.ladder._fix
        assert not self.is_endpoint

        ha = self.hori_after
        self.solo()
        A = self.fold_invert(P)
        B = self.fold(P)
        self.unsolo()
        ha.solo()
        C = ha.fold_invert(P)
        D = ha.fold(P)
        ha.unsolo()

        Delta = abs(A + D - B - C)
        return 1 - (self.ladder.r / (self.ladder.r + Delta))


class StraightLadder(Ladder):
    def __init__(self, line_count: int, lines: List[int]) -> None:
        super().__init__()
        self.line_count = line_count
        self.line_tracks: Dict[Node, int] = {}
        self.nodes_by_lines: List[List[Node]] = [
            [Node(i, self)] for i in range(line_count)
        ]
        for i, node in enumerate(self.nodes_by_lines):
            self.line_tracks[node[0]] = i
        for line in lines:
            u, v = self.nodes_by_lines[line][-1], self.nodes_by_lines[line + 1][-1]
            u_under, v_under = self.insert_under(
                u, v, f"under_{u.name}", f"under_{v.name}"
            )
            self.nodes_by_lines[line].append(u_under)
            self.nodes_by_lines[line + 1].append(v_under)
            self.line_tracks[u_under] = line
            self.line_tracks[v_under] = line + 1

    def __getitem__(self, arg) -> Node:
        line, no = arg
        return self.nodes_by_lines[line][no]

    def twist(self, line, no1, no2):
        self[line, no1].twist(self[line, no2])
