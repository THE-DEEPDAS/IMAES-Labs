import random
import math
from collections import deque
import matplotlib.pyplot as plt

class TileWorld:
    def __init__(self, size=15, hole_prob=0.08, min_life=5, max_life=15,
                 world_speed=1, seed=42):
        self.size = size
        self.hole_prob = hole_prob
        self.min_life = min_life
        self.max_life = max_life
        self.world_speed = world_speed

        random.seed(seed)

        self.agent_pos = (size // 2, size // 2)
        self.holes = {}

        self.total_appeared = 0
        self.total_filled = 0

    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.size and 0 <= c < self.size

    def spawn_holes(self):
        for _ in range(self.world_speed):
            if random.random() < self.hole_prob:
                while True:
                    pos = (
                        random.randint(0, self.size - 1),
                        random.randint(0, self.size - 1)
                    )

                    if pos != self.agent_pos and pos not in self.holes:
                        break

                self.holes[pos] = random.randint(
                    self.min_life,
                    self.max_life
                )

                self.total_appeared += 1

    def advance(self):
        expired = []

        for pos in self.holes:
            self.holes[pos] -= 1

            if self.holes[pos] <= 0:
                expired.append(pos)

        for pos in expired:
            del self.holes[pos]

        self.spawn_holes()

    def move_agent(self, action):
        r, c = self.agent_pos

        if action == "UP":
            r -= 1
        elif action == "DOWN":
            r += 1
        elif action == "LEFT":
            c -= 1
        elif action == "RIGHT":
            c += 1

        new_pos = (r, c)

        if self.in_bounds(new_pos):
            self.agent_pos = new_pos

            if new_pos in self.holes:
                del self.holes[new_pos]
                self.total_filled += 1

    def percept(self):
        return {
            "agent_pos": self.agent_pos,
            "holes": dict(self.holes)
        }

    def effectiveness(self):
        if self.total_appeared == 0:
            return 0

        return self.total_filled / self.total_appeared


class BDIAgent:

    def __init__(self, world, gamma=1, commitment="single-minded"):

        self.world = world

        self.B = {}
        self.D = []
        self.I = None
        self.plan = deque()

        self.gamma = gamma
        self.steps_since_reconsider = 0

        self.commitment = commitment

        self.trace = []

    def brf(self, percept):
        self.B = percept.copy()

    def options(self):
        holes = self.B["holes"]
        self.D = list(holes.keys())

        return self.D

    def filter(self):

        if not self.D:
            return None

        agent_pos = self.B["agent_pos"]

        best = min(
            self.D,
            key=lambda p: abs(p[0] - agent_pos[0]) +
                          abs(p[1] - agent_pos[1])
        )

        return best

    def plan_for(self, target):

        if target is None:
            return deque()

        start = self.B["agent_pos"]

        q = deque([(start, [])])
        visited = {start}

        directions = [
            (-1, 0, "UP"),
            (1, 0, "DOWN"),
            (0, -1, "LEFT"),
            (0, 1, "RIGHT")
        ]

        while q:

            pos, path = q.popleft()

            if pos == target:
                return deque(path)

            for dr, dc, action in directions:

                nr = pos[0] + dr
                nc = pos[1] + dc

                nxt = (nr, nc)

                if self.world.in_bounds(nxt) and nxt not in visited:

                    visited.add(nxt)

                    q.append(
                        (
                            nxt,
                            path + [action]
                        )
                    )

        return deque()

    def achieved(self):

        if self.I is None:
            return False

        return self.I not in self.world.holes

    def achievable(self):

        if self.I is None:
            return False

        return self.I in self.world.holes

    def deliberate(self):

        self.options()

        if not self.D:
            self.I = None
            self.plan = deque()
            return

        new_I = self.filter()

        if new_I != self.I:

            if self.I is not None:
                self.trace.append(
                    f"SWITCH: {self.I} -> {new_I}"
                )
            else:
                self.trace.append(
                    f"COMMIT: {new_I}"
                )

            self.I = new_I
            self.plan = self.plan_for(self.I)

    def reconsider(self):

        self.steps_since_reconsider += 1

        if self.steps_since_reconsider < self.gamma:
            return

        self.steps_since_reconsider = 0

        self.world.advance()

        self.brf(self.world.percept())

        if self.I is not None and not self.achievable():

            self.trace.append(
                f"DROP: {self.I}"
            )

            self.I = None
            self.plan = deque()

            return

        old_I = self.I

        self.options()

        if self.D:

            new_I = self.filter()

            if new_I != old_I:

                self.trace.append(
                    f"SWITCH: {old_I} -> {new_I}"
                )

                self.I = new_I
                self.plan = self.plan_for(new_I)

    def run(self, steps=600):

        for t in range(steps):

            self.brf(self.world.percept())

            if self.achieved():

                self.trace.append(
                    f"ACHIEVED: {self.I}"
                )

                self.I = None
                self.plan = deque()

            if self.I is None or not self.plan:

                self.deliberate()

            if self.plan:

                action = self.plan.popleft()

                self.world.move_agent(action)

            self.world.advance()

            self.reconsider()

        return self.world.effectiveness()


world = TileWorld(
    size=15,
    hole_prob=0.08,
    world_speed=2,
    seed=42
)

agent = BDIAgent(
    world,
    gamma=4,
    commitment="single-minded"
)

effectiveness = agent.run(steps=600)

print("BDI TILEWORLD RESULT")
print()

print("Holes appeared :", world.total_appeared)
print("Holes filled   :", world.total_filled)
print("Effectiveness  :", effectiveness)

print("\nEVENT TRACE")

for event in agent.trace[:30]:
    print(event)

# ============================================================
# RESOURCE-BOUNDED TILEWORLD
# ============================================================

class ResourceWorld(TileWorld):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.charger = (0, 0)

        self.battery_capacity = 40
        self.battery = 40

        self.stranded_steps = 0

    def move_agent(self, action):

        # No battery
        if self.battery <= 0:

            self.stranded_steps += 1

            self.advance()

            return

        # Normal movement
        super().move_agent(action)

        self.battery -= 1

        # Recharge
        if self.agent_pos == self.charger:

            self.battery = self.battery_capacity


# ============================================================
# RESOURCE BDI AGENT
# ============================================================

class ResourceBDIAgent:

    def __init__(self, world):

        self.world = world

        self.B = {}
        self.D = []
        self.I = None
        self.plan = deque()

    # --------------------------------------------------------
    # BELIEF REVISION
    # --------------------------------------------------------

    def brf(self):

        self.B = self.world.percept()

        self.B["battery"] = self.world.battery

    # --------------------------------------------------------
    # MANHATTAN DISTANCE
    # --------------------------------------------------------

    def distance(self, a, b):

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # --------------------------------------------------------
    # OPTIONS
    # --------------------------------------------------------

    def options(self):

        self.D = []

        agent = self.world.agent_pos
        charger = self.world.charger
        battery = self.world.battery

        for hole in self.world.holes:

            trip = self.distance(agent, hole)

            return_trip = self.distance(
                hole,
                charger
            )

            required = trip + return_trip

            # fill-hole is applicable
            if battery >= required:

                self.D.append(hole)

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    def filter(self):

        if self.D:

            agent = self.world.agent_pos

            # Nearest feasible hole
            return min(
                self.D,
                key=lambda h: self.distance(agent, h)
            )

        # No feasible hole
        return "RECHARGE"

    # --------------------------------------------------------
    # PLAN
    # --------------------------------------------------------

    def plan_to(self, target):

        start = self.world.agent_pos

        q = deque([(start, [])])
        visited = {start}

        directions = [
            (-1, 0, "UP"),
            (1, 0, "DOWN"),
            (0, -1, "LEFT"),
            (0, 1, "RIGHT")
        ]

        while q:

            pos, path = q.popleft()

            if pos == target:
                return deque(path)

            for dr, dc, action in directions:

                nxt = (
                    pos[0] + dr,
                    pos[1] + dc
                )

                if (
                    self.world.in_bounds(nxt)
                    and nxt not in visited
                ):

                    visited.add(nxt)

                    q.append(
                        (
                            nxt,
                            path + [action]
                        )
                    )

        return deque()

    def plan_recharge(self):

        return self.plan_to(
            self.world.charger
        )

    # --------------------------------------------------------
    # DELIBERATE
    # --------------------------------------------------------

    def deliberate(self):

        self.brf()

        self.options()

        self.I = self.filter()

        if self.I == "RECHARGE":

            self.plan = self.plan_recharge()

        else:

            self.plan = self.plan_to(self.I)

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(self, steps=600):

        for _ in range(steps):

            self.brf()

            if (
                self.I is None
                or not self.plan
                or self.I not in self.world.holes
                and self.I != "RECHARGE"
            ):

                self.deliberate()

            if self.plan:

                action = self.plan.popleft()

                self.world.move_agent(action)

            else:

                # No movement possible
                self.world.advance()

        return (
            self.world.total_filled,
            self.world.stranded_steps
        )


# ============================================================
# BLIND BATTERY AGENT
# ============================================================

class BlindBatteryAgent:

    def __init__(self, world):

        self.world = world

    def distance(self, a, b):

        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_hole(self):

        if not self.world.holes:
            return None

        return min(
            self.world.holes,
            key=lambda h:
            self.distance(
                self.world.agent_pos,
                h
            )
        )

    def plan_to(self, target):

        start = self.world.agent_pos

        q = deque([(start, [])])
        visited = {start}

        directions = [
            (-1, 0, "UP"),
            (1, 0, "DOWN"),
            (0, -1, "LEFT"),
            (0, 1, "RIGHT")
        ]

        while q:

            pos, path = q.popleft()

            if pos == target:
                return deque(path)

            for dr, dc, action in directions:

                nxt = (
                    pos[0] + dr,
                    pos[1] + dc
                )

                if (
                    self.world.in_bounds(nxt)
                    and nxt not in visited
                ):

                    visited.add(nxt)

                    q.append(
                        (
                            nxt,
                            path + [action]
                        )
                    )

        return deque()

    def run(self, steps=600):

        plan = deque()

        for _ in range(steps):

            # Pick nearest hole
            if not plan:

                target = self.nearest_hole()

                if target is not None:

                    plan = self.plan_to(target)

            if plan:

                action = plan.popleft()

                self.world.move_agent(action)

            else:

                self.world.advance()

        return (
            self.world.total_filled,
            self.world.stranded_steps
        )


# ============================================================
# COMPARE BDI VS BLIND
# ============================================================

print("\nRESOURCE-BOUNDED COMPARISON")
print("=" * 50)


# BDI
world_bdi = ResourceWorld(
    size=15,
    hole_prob=0.08,
    world_speed=2,
    seed=42
)

bdi = ResourceBDIAgent(world_bdi)

filled_bdi, stranded_bdi = bdi.run(600)


# Blind
world_blind = ResourceWorld(
    size=15,
    hole_prob=0.08,
    world_speed=2,
    seed=42
)

blind = BlindBatteryAgent(world_blind)

filled_blind, stranded_blind = blind.run(600)


print("\nBDI Agent")
print("---------")
print("Holes filled    :", filled_bdi)
print("Stranded steps  :", stranded_bdi)


print("\nBlind Agent")
print("-----------")
print("Holes filled    :", filled_blind)
print("Stranded steps  :", stranded_blind)