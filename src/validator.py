def is_valid_route(route, n, arcs):
    if len(route) != n + 1:
        return False

    if route[0] != 0 or route[-1] != 0:
        return False

    if set(route[:-1]) != set(range(n)):
        return False

    existing_arcs = {
        (arc["from"], arc["to"]) for arc in arcs
    }

    for i in range(len(route) - 1):
        if (route[i], route[i + 1]) not in existing_arcs:
            return False

    return True