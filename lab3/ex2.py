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