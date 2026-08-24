# ============================================================
# EXERCISE 1
# BOLDNESS AGAINST DYNAMISM
# ============================================================

def run_experiment(gamma, world_speed, seeds=25):

    results = []

    for seed in range(seeds):

        world = TileWorld(
            size=15,
            hole_prob=0.08,
            world_speed=world_speed,
            seed=seed
        )

        # "bold" = never reconsider during a plan
        if gamma == "bold":
            actual_gamma = 10**9
        else:
            actual_gamma = gamma

        agent = BDIAgent(
            world,
            gamma=actual_gamma
        )

        effectiveness = agent.run(steps=600)

        results.append(effectiveness)

    return sum(results) / len(results)


gammas = [1, 2, 4, 8, "bold"]
speeds = [1, 2, 4, 8]

results = {}

for speed in speeds:

    results[speed] = {}

    for gamma in gammas:

        avg = run_experiment(
            gamma,
            speed,
            seeds=25
        )

        results[speed][gamma] = avg

        print(
            f"Speed={speed}, "
            f"Gamma={gamma}, "
            f"Effectiveness={avg:.4f}"
        )


# ============================================================
# PRINT TABLE
# ============================================================

print("\n\nRESULT TABLE")
print("=" * 60)

print(
    f"{'Speed':<10}"
    f"{'γ=1':<12}"
    f"{'γ=2':<12}"
    f"{'γ=4':<12}"
    f"{'γ=8':<12}"
    f"{'Bold':<12}"
)

for speed in speeds:

    print(
        f"{speed:<10}"
        f"{results[speed][1]:<12.4f}"
        f"{results[speed][2]:<12.4f}"
        f"{results[speed][4]:<12.4f}"
        f"{results[speed][8]:<12.4f}"
        f"{results[speed]['bold']:<12.4f}"
    )


# ============================================================
# FIND BEST GAMMA
# ============================================================

print("\nBEST GAMMA AT EACH WORLD SPEED")
print("=" * 45)

best_gamma = {}

for speed in speeds:

    best = max(
        results[speed],
        key=results[speed].get
    )

    best_gamma[speed] = best

    print(
        f"World speed {speed} -> "
        f"Best gamma = {best}, "
        f"Effectiveness = {results[speed][best]:.4f}"
    )


# ============================================================
# PLOT
# ============================================================

for gamma in gammas:

    y = [
        results[speed][gamma]
        for speed in speeds
    ]

    plt.plot(
        speeds,
        y,
        marker="o",
        label=f"γ={gamma}"
    )

plt.xlabel("World ticks per agent action")
plt.ylabel("Average effectiveness")
plt.title("BDI Commitment: Boldness vs Dynamism")

plt.xticks(speeds)
plt.grid(True)
plt.legend()

plt.show()