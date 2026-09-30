import random
from itertools import permutations

def centralized(agents, tasks, cost):
    best_cost = float("inf")
    best_assignment = None
    evaluated = 0

    # Try every possible assignment
    for p in permutations(range(len(tasks)), len(agents)):
        total = 0

        for i in range(len(agents)):
            total += cost[i][p[i]]

        evaluated += 1

        if total < best_cost:
            best_cost = total
            best_assignment = p

    # One report from every agent + one instruction to every agent
    messages = 2 * len(agents)

    return best_assignment, best_cost, evaluated, messages

def decentralized(agents, tasks, cost):
    free_agents = list(range(len(agents)))
    free_tasks = list(range(len(tasks)))

    assignment = {}
    messages = 0
    rounds = 0
    all_bids = []

    while free_agents and free_tasks:
        rounds += 1
        bids = []

        # Every free agent chooses its cheapest free task
        for a in free_agents:
            best_task = min(
                free_tasks,
                key=lambda t: (cost[a][t], t)
            )

            bids.append((a, best_task, cost[a][best_task]))

            # Broadcast to all other agents
            messages += len(free_agents) - 1

        all_bids.append(bids)

        # Resolve conflicts
        winners = {}

        for a, t, c in bids:
            if t not in winners:
                winners[t] = (a, c)
            else:
                old_a, old_c = winners[t]

                if (c, a) < (old_c, old_a):
                    winners[t] = (a, c)

        # Commit winners
        for t, (a, c) in winners.items():
            assignment[a] = t

        # Remove assigned agents and tasks
        winning_agents = [a for a, t in assignment.items()]
        winning_tasks = list(assignment.values())

        free_agents = [
            a for a in free_agents
            if a not in winning_agents
        ]

        free_tasks = [
            t for t in free_tasks
            if t not in winning_tasks
        ]

    total_cost = 0

    for a, t in assignment.items():
        total_cost += cost[a][t]

    return assignment, total_cost, messages, rounds, all_bids

def print_matrix(cost):
    print("\nCost Matrix")
    print("       ", end="")

    for j in range(len(cost[0])):
        print(f"T{j+1:4}", end="")
    print()

    for i in range(len(cost)):
        print(f"A{i+1}     ", end="")

        for x in cost[i]:
            print(f"{x:4}", end="")
        print()


def print_assignment(assignment):
    if isinstance(assignment, tuple):
        for a, t in enumerate(assignment):
            print(f"A{a+1} -> T{t+1}")
    else:
        for a, t in sorted(assignment.items()):
            print(f"A{a+1} -> T{t+1}")

agents = [(0, 0), (2, 1), (5, 2), (6, 6)]
tasks = [(1, 1), (3, 4), (5, 5), (7, 2)]

cost = []

for a in agents:
    row = []

    for t in tasks:
        distance = abs(a[0] - t[0]) + abs(a[1] - t[1])
        row.append(distance)

    cost.append(row)


print("ALGORITHM 1 - CENTRALIZED ALLOCATION")

print_matrix(cost)

assignment, total, evaluated, messages = centralized(
    agents, tasks, cost
)

print("\nAssignment:")
print_assignment(assignment)

print("Total Cost:", total)
print("Assignments Evaluated:", evaluated)
print("Messages:", messages)


print("\n" + "=" * 60)
print("ALGORITHM 2 - DECENTRALIZED ALLOCATION")


assignment2, total2, messages2, rounds, bids = decentralized(
    agents, tasks, cost
)

print_matrix(cost)

print("\nBids in each round:")

for r, round_bids in enumerate(bids, 1):
    print(f"\nRound {r}:")

    for a, t, c in round_bids:
        print(f"A{a+1} bids for T{t+1} (cost = {c})")

print("\nFinal Assignment:")
print_assignment(assignment2)

print("Total Cost:", total2)
print("Messages:", messages2)
print("Rounds:", rounds)

# EXERCISE 1 RANDOM INSTANCES: 3 TO 8 AGENTS/TASKS

print("\n" + "=" * 60)
print("EXERCISE 1 - RANDOM INSTANCES")


random.seed(10)

instances = 5

print(
    "\nSize | Optimal | Decentralized | "
    "Central Msg | Decentralized Msg | Evaluated | Excess %"
)
print("-" * 80)

for n in range(3, 9):

    optimal_sum = 0
    decentralized_sum = 0
    central_msg_sum = 0
    decentralized_msg_sum = 0
    evaluated_sum = 0

    for k in range(instances):

        agents_r = []

        tasks_r = []

        for i in range(n):
            agents_r.append((
                random.randint(0, 20),
                random.randint(0, 20)
            ))

            tasks_r.append((
                random.randint(0, 20),
                random.randint(0, 20)
            ))

        cost_r = []

        for a in agents_r:
            row = []

            for t in tasks_r:
                row.append(
                    abs(a[0] - t[0]) +
                    abs(a[1] - t[1])
                )

            cost_r.append(row)

        # Centralized
        _, opt, evaluated, msg1 = centralized(
            agents_r, tasks_r, cost_r
        )

        # Decentralized
        _, dec, msg2, _, _ = decentralized(
            agents_r, tasks_r, cost_r
        )

        optimal_sum += opt
        decentralized_sum += dec
        central_msg_sum += msg1
        decentralized_msg_sum += msg2
        evaluated_sum += evaluated

    optimal_avg = optimal_sum / instances
    decentralized_avg = decentralized_sum / instances
    central_msg_avg = central_msg_sum / instances
    decentralized_msg_avg = decentralized_msg_sum / instances
    evaluated_avg = evaluated_sum / instances

    excess = (
        (decentralized_avg - optimal_avg)
        / optimal_avg
        * 100
    )

    print(
        f"{n:4} | "
        f"{optimal_avg:7.2f} | "
        f"{decentralized_avg:13.2f} | "
        f"{central_msg_avg:11.2f} | "
        f"{decentralized_msg_avg:18.2f} | "
        f"{evaluated_avg:9.0f} | "
        f"{excess:7.2f}%"
    )


# EXERCISE 2 - REMOVE ONE AGENT
print("\n")
print("EXERCISE 2 - REMOVE ONE AGENT")


# Remove the last agent
remaining_agents = agents[:-1]

remaining_cost = []

for a in remaining_agents:
    row = []

    for t in tasks:
        row.append(
            abs(a[0] - t[0]) +
            abs(a[1] - t[1])
        )

    remaining_cost.append(row)


print("\nAfter removing A4:")

print_matrix(remaining_cost)


# Centralized with one less agent
assignment3, total3, evaluated3, messages3 = centralized(
    remaining_agents,
    tasks,
    remaining_cost
)

print("\nCentralized Allocation:")
print_assignment(assignment3)

print("Total Cost:", total3)
served = list(assignment3)

for t in range(len(tasks)):
    if t not in served:
        print("Unserved Task: T" + str(t + 1))


# Decentralized with one less agent
assignment4, total4, messages4, rounds4, bids4 = decentralized(
    remaining_agents,
    tasks,
    remaining_cost
)

print("\nDecentralized Allocation:")
print_assignment(assignment4)

print("Total Cost:", total4)

served = list(assignment3)

for t in range(len(tasks)):
    if t not in served:
        print("Unserved Task: T" + str(t + 1))