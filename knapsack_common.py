import time
from statistics import median


SEPARATOR = "=" * 50


def solve_by_exhaustive_search(items, capacity):
    best_value = -1
    best_choices = []

    for mask in range(1 << len(items)):
        weight = 0
        value = 0
        chosen = []

        for i, item in enumerate(items):
            if mask >> i & 1:
                weight += item["weight"]
                value += item["value"]
                chosen.append(item["id"])

        if weight > capacity:
            continue

        if value > best_value:
            best_value = value
            best_choices = [(chosen, weight, value)]
        elif value == best_value:
            best_choices.append((chosen, weight, value))

    return best_choices


def solve_by_greedy_ratio(items, capacity):
    order = sorted(
        items,
        key=lambda item: (-item["value"] / item["weight"], -item["value"], item["weight"], item["id"]),
    )

    chosen = []
    weight = 0
    value = 0
    for item in order:
        if weight + item["weight"] <= capacity:
            chosen.append(item["id"])
            weight += item["weight"]
            value += item["value"]

    return sorted(chosen), weight, value


def measure_exhaustive_search_time(items, capacity, trials=3):
    elapsed_list = []
    result = None

    for _ in range(trials):
        start_time = time.perf_counter()
        result = solve_by_exhaustive_search(items, capacity)
        elapsed_list.append((time.perf_counter() - start_time) * 1000)

    return result, median(elapsed_list)


def measure_greedy_time(items, capacity, repeat=1000):
    start_time = time.perf_counter()
    result = None

    for _ in range(repeat):
        result = solve_by_greedy_ratio(items, capacity)

    elapsed_ms = (time.perf_counter() - start_time) * 1000 / repeat
    return result, elapsed_ms


def analyze_case(items, capacity, include_timing):
    if include_timing:
        exhaustive_choices, exhaustive_ms = measure_exhaustive_search_time(items, capacity)
        greedy_choice, greedy_ms = measure_greedy_time(items, capacity)
    else:
        exhaustive_choices = solve_by_exhaustive_search(items, capacity)
        greedy_choice = solve_by_greedy_ratio(items, capacity)
        exhaustive_ms = None
        greedy_ms = None

    return {
        "exhaustive_choices": exhaustive_choices,
        "greedy_choice": greedy_choice,
        "exhaustive_ms": exhaustive_ms,
        "greedy_ms": greedy_ms,
        "gap": exhaustive_choices[0][2] - greedy_choice[2],
    }


def print_case_data(items, capacity, show_items):
    if show_items:
        ids = [item["id"] for item in items]
        weights = [item["weight"] for item in items]
        values = [item["value"] for item in items]

        print("容量制約:", capacity)
        print("製品ID:", ids)
        print("製品容量一覧:", weights)
        print("利得一覧:", values)
        return

    print("製品数:", len(items))
    print("容量制約:", capacity)


def print_exhaustive_result(exhaustive_choices, elapsed_ms=None):
    print("[完全列挙法]")
    for index, (ids, weight, value) in enumerate(exhaustive_choices, start=1):
        print(f"最適解{index} =", ids)
        print("使用容量 =", weight)
        print("利得 =", value)
    if elapsed_ms is not None:
        print("時間 =", f"{elapsed_ms:.3f}", "ms")


def print_greedy_result(greedy_choice, elapsed_ms=None):
    ids, weight, value = greedy_choice

    print("[欲張り法]")
    print("解 =", ids)
    print("使用容量 =", weight)
    print("利得 =", value)
    if elapsed_ms is not None:
        print("時間 =", f"{elapsed_ms:.3f}", "ms")


def print_comparison(gap):
    print("[比較]")
    print("利得差 =", gap)
    if gap == 0:
        print("判定 = 欲張り法でも最適解に到達")
    else:
        print("判定 = 欲張り法は最適解に到達していない")


def print_case_report(case_name, items, capacity, analysis, show_items, show_comparison=True):
    print(SEPARATOR)
    print("ケース:", case_name)
    print_case_data(items, capacity, show_items)
    print()

    print_exhaustive_result(analysis["exhaustive_choices"], analysis["exhaustive_ms"])
    print()
    print_greedy_result(analysis["greedy_choice"], analysis["greedy_ms"])
    if show_comparison:
        print()
        print_comparison(analysis["gap"])
    print()
