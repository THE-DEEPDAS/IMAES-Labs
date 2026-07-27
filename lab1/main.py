from copy import deepcopy

# Base knowlege for the main experiment.
base_network = [
    ("animal", "has", "skin"),
    ("animal", "can", "breathe"),
    ("bird", "is-a", "animal"),
    ("bird", "has", "feathers"),
    ("bird", "can", "fly"),
    ("penguin", "is-a", "bird"),
    ("penguin", "cannot", "fly"),
]

base_frames = {
    "animal": {
        "ako": None,
        "slots": {
            "has": "skin",
            "can": "breathe",
        },
    },
    "bird": {
        "ako": "animal",
        "slots": {
            "has": "feathers",
            "can": "fly",
        },
    },
    "penguin": {
        "ako": "bird",
        "slots": {
            "can": "cannot fly",
        },
    },
}


def get_parents(network, concept):
    """Return all direct parents in the same order they appear in the network."""
    return [
        obj
        for subject, relation, obj in network
        if subject == concept and relation == "is-a"
    ]


def inheritance_chain(network, concept):
    """Return the concept and its ancestors from most specific to most general."""
    chain = []
    seen = set()
    current = concept

    while current and current not in seen:
        chain.append(current)
        seen.add(current)

        parents = get_parents(network, current)
        current = parents[0] if parents else None

    return chain


def query_network(network, concept, relation, seen=None):
    """Look up a relation with local exceptions first, then search parent concepts."""
    if seen is None:
        seen = set()

    if concept in seen:
        return "unknown"
    seen.add(concept)

    # Check the most specific concept first.
    if relation == "can":
        for subject, rel, obj in network:
            if subject == concept and rel == "cannot":
                return f"cannot {obj}"

    for subject, rel, obj in network:
        if subject == concept and rel == relation:
            return obj

    # If nothing is found locally, search the parents in the same order they were added.
    for parent in get_parents(network, concept):
        answer = query_network(network, parent, relation, seen)
        if answer != "unknown":
            return answer

    return "unknown"


def frame_parents(frame):
    """Normalize the 'ako' link to a list so single and multiple parents work."""
    ako = frame.get("ako")
    if not ako:
        return []
    if isinstance(ako, list):
        return ako
    return [ako]


def frame_lookup(frames, concept, slot, seen=None):
    """Look up a slot with local exceptions first, then follow the ako links."""
    if seen is None:
        seen = set()

    if concept in seen:
        return "unknown"
    seen.add(concept)

    frame = frames.get(concept)
    if not frame:
        return "unknown"

    slots = frame.get("slots", {})
    if slot in slots:
        return slots[slot]

    for parent in frame_parents(frame):
        answer = frame_lookup(frames, parent, slot, seen)
        if answer != "unknown":
            return answer

    return "unknown"


def show_queries(title, lookup, queries):
    print(f"\n{title}:")
    for label, concept, relation in queries:
        print(f"{label:<22} = {lookup(concept, relation)}")


def show_frame_queries(title, frames, queries):
    print(f"\n{title}:")
    for label, concept, slot in queries:
        print(f"{label:<22} = {frame_lookup(frames, concept, slot)}")


if __name__ == "__main__":
    # Main experiment: only one parent link is needed, and penguin shows the exception.
    main_network = deepcopy(base_network)
    main_frames = deepcopy(base_frames)

    print("Semantic network triples:")
    for triple in main_network:
        print(" ", triple)

    print("\nMain experiment:")
    print("penguin inheritance chain:")
    print(" -> ".join(inheritance_chain(main_network, "penguin")))
    show_queries(
        "Semantic network queries",
        lambda concept, relation: query_network(main_network, concept, relation),
        [
            ("bird can", "bird", "can"),
            ("bird has", "bird", "has"),
            ("penguin can", "penguin", "can"),
            ("penguin has", "penguin", "has"),
        ],
    )
    show_frame_queries(
        "Frame queries",
        main_frames,
        [
            ("bird can", "bird", "can"),
            ("bird has", "bird", "has"),
            ("penguin can", "penguin", "can"),
            ("penguin has", "penguin", "has"),
        ],
    )

    # Exercise 1: add ostrich as a bird that cannot fly and can run fast.
    ex1_network = deepcopy(base_network)
    ex1_network.extend(
        [
            ("ostrich", "is-a", "bird"),
            ("ostrich", "cannot", "fly"),
            ("ostrich", "runs", "fast"),
        ]
    )
    ex1_frames = deepcopy(base_frames)
    ex1_frames["ostrich"] = {
        "ako": "bird",
        "slots": {
            "can": "cannot fly",
            "runs": "fast",
        },
    }

    print("\nExercise 1:")
    print("ostrich inheritance chain:")
    print(" -> ".join(inheritance_chain(ex1_network, "ostrich")))
    show_queries(
        "Semantic network queries",
        lambda concept, relation: query_network(ex1_network, concept, relation),
        [
            ("ostrich can", "ostrich", "can"),
            ("ostrich has", "ostrich", "has"),
            ("ostrich runs", "ostrich", "runs"),
        ],
    )
    show_frame_queries(
        "Frame queries",
        ex1_frames,
        [
            ("ostrich can", "ostrich", "can"),
            ("ostrich has", "ostrich", "has"),
            ("ostrich runs", "ostrich", "runs"),
        ],
    )

    # Exercise 3: allow multiple parents and search them in the order they appear.
    ex3_network = deepcopy(base_network)
    ex3_network.extend(
        [
            ("runner", "is-a", "animal"),
            ("runner", "runs", "fast"),
            ("ostrich", "is-a", "bird"),
            ("ostrich", "is-a", "runner"),
            ("ostrich", "cannot", "fly"),
        ]
    )
    ex3_frames = deepcopy(base_frames)
    ex3_frames["runner"] = {
        "ako": "animal",
        "slots": {
            "runs": "fast",
        },
    }
    ex3_frames["ostrich"] = {
        "ako": ["bird", "runner"],
        "slots": {
            "can": "cannot fly",
        },
    }

    print("\nExercise 3:")
    print("ostrich direct parents:")
    print(", ".join(get_parents(ex3_network, "ostrich")))
    print("search order: depth-first, left-to-right")
    show_queries(
        "Semantic network queries",
        lambda concept, relation: query_network(ex3_network, concept, relation),
        [
            ("ostrich can", "ostrich", "can"),
            ("ostrich has", "ostrich", "has"),
            ("ostrich runs", "ostrich", "runs"),
        ],
    )
    show_frame_queries(
        "Frame queries",
        ex3_frames,
        [
            ("ostrich can", "ostrich", "can"),
            ("ostrich has", "ostrich", "has"),
            ("ostrich runs", "ostrich", "runs"),
        ],
    )
