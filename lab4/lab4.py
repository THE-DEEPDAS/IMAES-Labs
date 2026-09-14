# Reasoning Techniques
# Modus Ponens and Modus Tollens

def negate(literal):
    if literal.startswith("not "):
        return literal[4:]
    return "not " + literal


def is_negative(literal):
    return literal.startswith("not ")

# MODUS PONENS

def modus_ponens(facts, rules, justification):
    """
    Repeatedly apply Modus Ponens until no new fact can be derived.

    Rule:
        P -> Q
    Fact:
        P
    Therefore:
        Q
    """

    changed = True

    while changed:

        changed = False

        for rule_id, antecedents, consequent in rules:

            # Check whether ALL antecedents are known
            if all(a in facts for a in antecedents):

                # If consequent is new, add it
                if consequent not in facts:

                    facts.add(consequent)

                    # Save how this fact was derived
                    justification[consequent] = (
                        rule_id,
                        antecedents
                    )

                    print(
                        f"MP: {antecedents} "
                        f"--[{rule_id}]--> {consequent}"
                    )

                    changed = True

    return facts

# MODUS TOLLENS

def modus_tollens(facts, rules, justification):
    """
    For multiple antecedents:

        P AND R -> Q
        not Q

    we can only conclude:

        not P OR not R

    Unless all but one antecedent are already known true.
    """

    changed = True

    while changed:

        changed = False

        for rule_id, antecedents, consequent in rules:

            # We need NOT Q
            if negate(consequent) not in facts:
                continue

            if len(antecedents) == 1:

                new_fact = negate(antecedents[0])

                if new_fact not in facts:

                    facts.add(new_fact)

                    justification[new_fact] = (
                        "MT-" + rule_id,
                        [negate(consequent)]
                    )

                    print(
                        f"MT: {negate(consequent)} "
                        f"--[{rule_id}]--> {new_fact}"
                    )

                    changed = True

            # Multiple antecedents
            else:

                # Find antecedents already known to be true
                true_antecedents = [
                    a for a in antecedents
                    if a in facts
                ]

                # If all but one are true, the remaining one
                # must be false.
                if len(true_antecedents) == len(antecedents) - 1:

                    for a in antecedents:

                        if a not in facts:

                            new_fact = negate(a)

                            if new_fact not in facts:

                                facts.add(new_fact)

                                justification[new_fact] = (
                                    "MT-" + rule_id,
                                    [negate(consequent)]
                                    + true_antecedents
                                )

                                print(
                                    f"MT: {negate(consequent)} + "
                                    f"{true_antecedents} "
                                    f"--[{rule_id}]--> {new_fact}"
                                )

                                changed = True

                else:

                    # We cannot determine which antecedent is false.
                    # So store a pending disjunction.
                    pending = [
                        negate(a)
                        for a in antecedents
                        if a not in facts
                    ]

                    print(
                        f"MT pending conclusion: "
                        f"{' OR '.join(pending)}"
                    )

    return facts


def check_query(query, facts, rules):
    """
    Check whether a query is entailed.

    Also reject the two common invalid patterns:

    1. Affirming the consequent:
           P -> Q
           Q
           therefore P     INVALID

    2. Denying the antecedent:
           P -> Q
           not P
           therefore not Q INVALID
    """

    if query in facts:

        print(f"\nQuery: {query}")
        print("Result: ENTAILED")

        return True

    print(f"\nQuery: {query}")
    print("Result: NOT ENTAILED")

    return False


def print_justifications(facts, justification):

    print("\n--- JUSTIFICATION CHAINS ---")

    for fact in facts:

        if fact in justification:

            rule_id, premises = justification[fact]

            print(
                f"{fact} <- "
                f"{rule_id} using {premises}"
            )

        else:

            print(
                f"{fact} <- INPUT FACT"
            )


# EXERCISE 2 CONTRADICTION DETECTION

def find_contradictions(facts):

    contradictions = []

    for fact in facts:

        opposite = negate(fact)

        if opposite in facts:

            pair = tuple(sorted([fact, opposite]))

            if pair not in contradictions:

                contradictions.append(pair)

    return contradictions


def print_contradictions(facts, justification):

    contradictions = find_contradictions(facts)

    if not contradictions:

        print("\nKnowledge base is CONSISTENT.")

        return

    print("\nKnowledge base is INCONSISTENT!")

    for a, b in contradictions:

        print(f"\nContradiction: {a} AND {b}")

        print("Chain for", a)

        if a in justification:

            rule, premises = justification[a]

            print(
                f"  {a} <- {rule} using {premises}"
            )

        else:

            print("  INPUT FACT")

        print("Chain for", b)

        if b in justification:

            rule, premises = justification[b]

            print(
                f"  {b} <- {rule} using {premises}"
            )

        else:

            print("  INPUT FACT")


# FIND SMALLEST INPUT FACT REMOVAL

def consistent_after_removing(input_facts, rules, removed):

    """
    Remove one input fact, run inference again,
    and check whether contradiction still exists.
    """

    facts = set(input_facts)

    facts.remove(removed)

    justification = {}

    # Run inference again
    modus_ponens(
        facts,
        rules,
        justification
    )

    modus_tollens(
        facts,
        rules,
        justification
    )

    return len(find_contradictions(facts)) == 0


def find_smallest_removal(input_facts, rules):

    """
    Try removing each input fact.

    If removing one fact restores consistency,
    that is the smallest possible removal.
    """

    for fact in input_facts:

        if consistent_after_removing(
            input_facts,
            rules,
            fact
        ):

            return [fact]

    return []


print("CORE ALGORITHM")

rules = [
    ("R1", ["rain"], "wet"),
    ("R2", ["wet"], "slippery"),
    ("R3", ["slippery"], "accident")
]

facts = {
    "rain"
}

justification = {}


print("\nInitial facts:")
print(facts)

print("\n--- MODUS PONENS ---")

modus_ponens(
    facts,
    rules,
    justification
)


print("\nFacts after Modus Ponens:")
print(facts)


print("\n--- MODUS TOLLENS ---")

# Add negative observation
facts.add("not accident")

print("\nAdded observation: not accident")

modus_tollens(
    facts,
    rules,
    justification
)


print("\nFinal facts:")
print(facts)

print_justifications(
    facts,
    justification
)

print("\n\n" + "=" * 60)
print("UNSOUND INFERENCE PATTERNS")
print("=" * 60)


print("""
1. Affirming the consequent:

   P -> Q
   Q
   Therefore P

   INVALID because Q can have another cause.

2. Denying the antecedent:

   P -> Q
   not P
   Therefore not Q

   INVALID because Q may still be true for another reason.
""")


facts2 = {"wet"}

check_query(
    "rain",
    facts2,
    rules
)

facts3 = {"not rain"}

check_query(
    "not wet",
    facts3,
    rules
)


print("\n\n" + "=" * 60)
print("EXERCISE 1")
print("=" * 60)


exercise1_rules = [

    # A AND B AND C -> D
    ("R4", ["A", "B", "C"], "D")
]


exercise1_facts = {
    "not D"
}


exercise1_justification = {}


print("\nRule:")
print("A AND B AND C -> D")

print("\nInitial fact:")
print("not D")


print("\nApplying Modus Tollens:")

modus_tollens(
    exercise1_facts,
    exercise1_rules,
    exercise1_justification
)


print("\nNo definite negative antecedent can be concluded yet.")

print("""
The correct pending conclusion is:

not A OR not B OR not C
""")


# ------------------------------------------------------------
# Add facts one at a time
# ------------------------------------------------------------

print("\nAdding A...")

exercise1_facts.add("A")

modus_tollens(
    exercise1_facts,
    exercise1_rules,
    exercise1_justification
)


print("\nAdding B...")

exercise1_facts.add("B")

modus_tollens(
    exercise1_facts,
    exercise1_rules,
    exercise1_justification
)


print("\nNow A and B are known to be true.")

print("""
Therefore, from:

A AND B AND C -> D
not D
A
B

we can conclude:

not C
""")


# ============================================================
# EXERCISE 2
# CONTRADICTION
# ============================================================

print("\n\n" + "=" * 60)
print("EXERCISE 2")
print("=" * 60)


exercise2_rules = [

    # A -> B
    ("R5", ["A"], "B"),

    # B -> not C
    ("R6", ["B"], "not C")
]


exercise2_facts = {
    "A",
    "C"
}


exercise2_justification = {}


print("\nInitial facts:")
print(exercise2_facts)


print("\nRules:")
print("A -> B")
print("B -> not C")


print("\nApplying Modus Ponens:")

modus_ponens(
    exercise2_facts,
    exercise2_rules,
    exercise2_justification
)


print("\nFinal facts:")
print(exercise2_facts)


# ------------------------------------------------------------
# Detect contradiction
# ------------------------------------------------------------

print_contradictions(
    exercise2_facts,
    exercise2_justification
)


# ------------------------------------------------------------
# Find smallest input fact whose removal fixes it
# ------------------------------------------------------------

removal = find_smallest_removal(
    exercise2_facts & {"A", "C"},
    exercise2_rules
)


print("\nSmallest input fact removal:")

if removal:

    print(
        "Remove:",
        removal
    )

else:

    print(
        "No single input fact restores consistency."
    )
