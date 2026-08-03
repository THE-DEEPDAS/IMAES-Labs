import time
import random

# Rule Base
rules = [
    {
        "id": "R1",
        "conditions": ["has_fever", "has_cough"],
        "conclusion": "flu"
    },
    {
        "id": "R2",
        "conditions": ["flu", "body_pain"],
        "conclusion": "visit_doctor"
    },
    {
        "id": "R3",
        "conditions": ["has_headache"],
        "conclusion": "take_rest"
    },
    {
        "id": "R4",
        "conditions": ["flu"],
        "conclusion": "take_rest"
    },
    {
        "id": "R5",
        "conditions": ["NOT allergy"],
        "conclusion": "safe_to_take_medicine"
    }
]

# Function to find Conflict Set
def match_rules(rules, working_memory):

    conflict_set = []

    for rule in rules:

        conditions_met = True

        for condition in rule["conditions"]:

            # Exercise 2: Handle negated conditions
            if condition.startswith("NOT "):
                fact = condition[4:]
                if fact in working_memory:
                    conditions_met = False
                    break

            else:
                if condition not in working_memory:
                    conditions_met = False
                    break

        # Refractoriness
        conclusion_absent = rule["conclusion"] not in working_memory

        if conditions_met and conclusion_absent:
            conflict_set.append(rule)

    return conflict_set

# Exercise 1
# Add facts one by one and observe Conflict Set

print("EXERCISE 1 : Growing Working Memory")

working_memory = set()

facts_to_add = [
    "has_fever",
    "has_cough",
    "body_pain",
    "flu",
    "has_headache"
]

for fact in facts_to_add:

    working_memory.add(fact)

    print("\nAdded Fact ->", fact)
    print("Working Memory:", working_memory)

    conflict_set = match_rules(rules, working_memory)

    print("Conflict Set:")

    if conflict_set:
        for rule in conflict_set:
            print(f" {rule['id']} -> {rule['conclusion']}")
    else:
        print(" None")

# Exercise 2
# Negated Conditions

print("EXERCISE 2 : Negated Conditions")

working_memory = {
    "has_fever",
    "has_cough"
}

print("Working Memory:", working_memory)

conflict_set = match_rules(rules, working_memory)

print("Conflict Set:")

for rule in conflict_set:
    print(rule["id"], "->", rule["conclusion"])

print("\nAdding allergy...")

working_memory.add("allergy")

conflict_set = match_rules(rules, working_memory)

print("Working Memory:", working_memory)

print("Conflict Set:")

for rule in conflict_set:
    print(rule["id"], "->", rule["conclusion"])

# Exercise 3
# Measure Matching Time for 1000 Rules

print("\nEXERCISE 3 : Performance Test\n")

large_rules = []

possible_facts = [f"fact{i}" for i in range(50)]

for i in range(1000):

    conditions = random.sample(possible_facts, 3)

    large_rules.append(
        {
            "id": f"R{i}",
            "conditions": conditions,
            "conclusion": f"new_fact{i}"
        }
    )

large_working_memory = set(random.sample(possible_facts, 30))

start = time.perf_counter()

conflict_set = match_rules(large_rules, large_working_memory)

end = time.perf_counter()

print("Total Rules:", len(large_rules))
print("Applicable Rules:", len(conflict_set))
print("Matching Time:", (end - start) * 1000, "ms")

large_rules = []

possible_facts = [f"fact{i}" for i in range(50)]

for i in range(10000):

    conditions = random.sample(possible_facts, 3)

    large_rules.append(
        {
            "id": f"R{i}",
            "conditions": conditions,
            "conclusion": f"new_fact{i}"
        }
    )

large_working_memory = set(random.sample(possible_facts, 30))

start = time.perf_counter()

conflict_set = match_rules(large_rules, large_working_memory)

end = time.perf_counter()

print("\nTotal Rules:", len(large_rules))
print("Applicable Rules:", len(conflict_set))
print("Matching Time:", (end - start) * 1000, "ms")