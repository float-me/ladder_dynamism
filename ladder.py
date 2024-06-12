from typing import Self, Dict, List, Tuple

class Ladder:
    def __init__(self) -> None:
        self.nodes: Dict[int, 'Node'] = {}
        self.node_count: int = 0
        self.n: int = 0
        self.d: int = 0
        self._fix: bool = False
    
    def fix(self):
        self._fix = True
    
    def unfix(self):
        self._fix = False

    def dynamism(self):
        assert self._fix
        dyna_sum = 0
        for node in self.nodes.values():
            if not node.is_endpoint:
                dyna_sum += node.unpredictability
        return dyna_sum / self.d
    
    def add_cycle(self, *names: str) -> List['Node']:
        nodes = [Node(name, self) for name in names]
        Node.vert_cycle(*nodes)
        return nodes

    def insert_under(self, u: 'Node', v: 'Node', name1: str, name2: str) -> List['Node']:
        u_under, v_under = Node(name1, self), Node(name2, self)
        u.vert_connect(u_under)
        v.vert_connect(v_under)
        u_under.hori_connect(v_under)
        return [u_under, v_under]
        
class Node:
    def vert_cycle(*nodes: Self) -> None:
        size = len(nodes)
        for i in range(size - 1):
            nodes[i].vert_connect(nodes[i+1])
        
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

    @property
    def heuristic_after(self):
        after = self.vert_after
        if after.is_endpoint:
            return 0
        else:
            dyna = after.unpredictability
            after.solo()
            heuri1 = after.heuristic_after
            after.unsolo()
            after_h = after.hori_after
            after_h.solo()
            heuri2 = after_h.heuristic_after
            after_h.unsolo()
            return 1 + dyna * heuri1 + (1 - dyna) * heuri2

    @property
    def heuristic_before(self):
        before = self.vert_before
        if before.is_endpoint:
            return 0
        else:
            dyna = before.unpredictability
            before.solo()
            heuri1 = before.heuristic_before
            before.unsolo()
            before_h = before.hori_before
            before_h.solo()
            heuri2 = before_h.heuristic_before
            before_h.unsolo()
            return 1 + dyna * heuri1 + (1 - dyna) * heuri2

    @property
    def unpredictability(self):
        assert self.ladder.n > 0 and self.ladder.d > 0
        
        other = self.hori_after
        self.solo()
        heuri_a_bef = self.heuristic_before
        heuri_a_aft = self.heuristic_after
        self.unsolo()
        other.solo()
        heuri_b_bef = other.heuristic_before
        heuri_b_aft = other.heuristic_after
        other.unsolo()

        r = self.ladder.d / self.ladder.n
        dist = heuri_a_aft + heuri_b_bef - heuri_b_aft - heuri_a_bef

        return 1 - (r / (r + abs(dist)))

class StraightLadder(Ladder):
    def __init__(self, line_count: int, lines: List[int]) -> None:
        super().__init__()
        self.line_count = line_count
        self.line_tracks: Dict[Node, int] = {}
        self.nodes_by_lines: List[List[Node]] = [[Node(i, self)] for i in range(line_count)]
        for i, node in enumerate(self.nodes_by_lines):
            self.line_tracks[node[0]] = i
        for line in lines:
            u, v = self.nodes_by_lines[line][-1], self.nodes_by_lines[line + 1][-1]
            u_under, v_under = self.insert_under(u, v, f"under_{u.name}", f"under_{v.name}")
            self.nodes_by_lines[line].append(u_under)
            self.nodes_by_lines[line + 1].append(v_under)
            self.line_tracks[u_under] = line
            self.line_tracks[v_under] = line + 1
    
    def __getitem__(self, arg) -> Node:
        line, no = arg
        return self.nodes_by_lines[line][no]
    
    def twist(self, line, no1, no2):
        self[line, no1].twist(self[line, no2])