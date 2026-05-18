import time


TASK1_CASE = {
    "name": "課題1の表1データ",
    "capacity": 25,
    "items": [
        {"id": 1, "weight": 3, "value": 3},
        {"id": 2, "weight": 5, "value": 7},
        {"id": 3, "weight": 4, "value": 6},
        {"id": 4, "weight": 2, "value": 3},
        {"id": 5, "weight": 10, "value": 13},
        {"id": 6, "weight": 7, "value": 9},
        {"id": 7, "weight": 1, "value": 2},
        {"id": 8, "weight": 5, "value": 6},
    ],
}


TASK2_CASES = [
    {
        "name": "欲張り法が失敗する小さい例",
        "capacity": 50,
        "items": [
            {"id": 1, "weight": 10, "value": 60},
            {"id": 2, "weight": 20, "value": 100},
            {"id": 3, "weight": 30, "value": 120},
        ],
    },
    {
        "name": "16製品の比較用データ",
        "capacity": 44,
        "items": [
            {"id": 1, "weight": 11, "value": 2},
            {"id": 2, "weight": 13, "value": 17},
            {"id": 3, "weight": 2, "value": 17},
            {"id": 4, "weight": 4, "value": 13},
            {"id": 5, "weight": 6, "value": 17},
            {"id": 6, "weight": 5, "value": 19},
            {"id": 7, "weight": 3, "value": 20},
            {"id": 8, "weight": 5, "value": 4},
            {"id": 9, "weight": 5, "value": 14},
            {"id": 10, "weight": 6, "value": 9},
            {"id": 11, "weight": 14, "value": 4},
            {"id": 12, "weight": 13, "value": 11},
            {"id": 13, "weight": 15, "value": 10},
            {"id": 14, "weight": 1, "value": 19},
            {"id": 15, "weight": 10, "value": 7},
            {"id": 16, "weight": 15, "value": 3},
        ],
    },
]


def solve_by_exhaustive_search(items, capacity):
    best_value = -1
    best_choices = []

    # 各ビット列を 1 つの組み合わせとして扱い、全通りを試す。
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
    # 利得/容量の高い順に並べ、入るものから順に採用する。
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


def get_repeat_count(item_count):
    if item_count <= 4:
        return 5000
    if item_count <= 8:
        return 1000
    if item_count <= 12:
        return 100
    return 1


def measure_execution_time(solver, items, capacity):
    repeat_count = get_repeat_count(len(items))
    start_time = time.perf_counter()
    result = None

    for _ in range(repeat_count):
        result = solver(items, capacity)

    elapsed_ms = (time.perf_counter() - start_time) * 1000 / repeat_count
    return result, elapsed_ms


def print_case_data(items, capacity):
    ids = [item["id"] for item in items]
    weights = [item["weight"] for item in items]
    values = [item["value"] for item in items]

    print("容量制約:", capacity)
    print("製品ID:", ids)
    print("製品容量一覧:", weights)
    print("利得一覧:", values)


def print_exhaustive_result(best_choices, elapsed_ms):
    print("[完全列挙法]")
    for index, (ids, weight, value) in enumerate(best_choices, start=1):
        print(f"最適解{index} =", ids)
        print("使用容量 =", weight)
        print("利得 =", value)
    print("時間 =", f"{elapsed_ms:.3f}", "ms")


def print_greedy_result(greedy_choice, elapsed_ms):
    ids, weight, value = greedy_choice

    print("[欲張り法]")
    print("解 =", ids)
    print("使用容量 =", weight)
    print("利得 =", value)
    print("時間 =", f"{elapsed_ms:.3f}", "ms")


def print_comparison(best_choices, greedy_choice):
    best_value = best_choices[0][2]
    greedy_value = greedy_choice[2]
    gap = best_value - greedy_value

    print("[比較]")
    print("利得差 =", gap)
    if gap == 0:
        print("判定 = 欲張り法でも最適解に到達")
    else:
        print("判定 = 欲張り法は最適解に到達していない")


def run_case(case):
    print("==================================================")
    print("ケース:", case["name"])
    print_case_data(case["items"], case["capacity"])
    print()

    best_choices, exhaustive_ms = measure_execution_time(
        solve_by_exhaustive_search, case["items"], case["capacity"]
    )
    greedy_choice, greedy_ms = measure_execution_time(
        solve_by_greedy_ratio, case["items"], case["capacity"]
    )

    print_exhaustive_result(best_choices, exhaustive_ms)
    print()
    print_greedy_result(greedy_choice, greedy_ms)
    print()
    print_comparison(best_choices, greedy_choice)
    print()


def run_task1_demo():
    run_case(TASK1_CASE)


def run_task2_demo():
    for case in TASK2_CASES:
        run_case(case)


def run_all_demos():
    run_task1_demo()
    run_task2_demo()


if __name__ == "__main__":
    run_all_demos()
