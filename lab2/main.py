# Each rule has:
#   id          -> Rule identifier
#   conditions  -> IF part
#   conclusion  -> THEN part

# The Conflict Set is simply the list of rules whose conditions are satisfied and whose conclusion is not already present in Working Memory

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
    }
]

# Working Memory (Current Facts)

working_memory = {
    "has_fever",
    "has_cough",
    "body_pain"
}

print("Working Memory:")
print(working_memory)

# Match Phase

conflict_set = []

for rule in rules:

    # Check if all conditions are satisfied for the rule to be applicable
    conditions_met = all(
        condition in working_memory
        for condition in rule["conditions"]
    )

    # Do not fire if conclusion already exists
    conclusion_absent = rule["conclusion"] not in working_memory

    if conditions_met and conclusion_absent:
        conflict_set.append(rule)

print("\nApplicable Rules (Conflict Set):")

if conflict_set:
    for rule in conflict_set:
        print(f"{rule['id']} : IF {rule['conditions']} THEN {rule['conclusion']}")
else:
    print("No applicable rules.")