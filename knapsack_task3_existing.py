import random
import time
from statistics import median

from knapsack_common import SEPARATOR, measure_exhaustive_search_time, print_case_data, print_exhaustive_result


COMPARISON_CASES = [
    {
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
    },
    {
        "name": "支配状態による限定が効く例",
        "capacity": 45,
        "items": [
            {"id": 1, "weight": 5, "value": 6},
            {"id": 2, "weight": 9, "value": 20},
            {"id": 3, "weight": 4, "value": 8},
            {"id": 4, "weight": 13, "value": 9},
            {"id": 5, "weight": 9, "value": 6},
            {"id": 6, "weight": 15, "value": 11},
            {"id": 7, "weight": 14, "value": 17},
            {"id": 8, "weight": 15, "value": 4},
            {"id": 9, "weight": 7, "value": 10},
            {"id": 10, "weight": 13, "value": 17},
            {"id": 11, "weight": 14, "value": 15},
            {"id": 12, "weight": 13, "value": 17},
        ],
    },
]

SIZE_LIST = [8, 10, 12, 14, 16, 18]
LARGE_SIZE_LIST = [20, 24, 28, 32, 36, 40, 60, 80, 100, 120, 140]
LARGE_SEED_LIST = [192, 193, 194, 195, 196]
LARGE_CASE_SETTINGS = {
    "seed": 192,
    "weight_min": 5,
    "weight_max": 20,
    "value_min": 5,
    "value_max": 25,
    "capacity_ratio": 0.45,
}


def create_size_case(
    item_count,
    seed=200,
    weight_min=1,
    weight_max=15,
    value_min=1,
    value_max=25,
    capacity_ratio=0.35,
):
    rng = random.Random(seed + item_count)
    items = []
    total_weight = 0

    for item_id in range(1, item_count + 1):
        weight = rng.randint(weight_min, weight_max)
        value = rng.randint(value_min, value_max)
        items.append({"id": item_id, "weight": weight, "value": value})
        total_weight += weight

    capacity = max(1, int(total_weight * capacity_ratio))
    return {
        "name": f"製品数 {item_count} 個の時間比較データ",
        "capacity": capacity,
        "items": items,
    }


def create_fixed_seed_case(
    item_count,
    seed,
    weight_min,
    weight_max,
    value_min,
    value_max,
    capacity_ratio,
    name,
):
    rng = random.Random(seed)
    items = []
    total_weight = 0

    for item_id in range(1, item_count + 1):
        weight = rng.randint(weight_min, weight_max)
        value = rng.randint(value_min, value_max)
        items.append({"id": item_id, "weight": weight, "value": value})
        total_weight += weight

    return {
        "name": name,
        "capacity": max(1, int(total_weight * capacity_ratio)),
        "items": items,
    }


def sort_items_for_search(items):
    return sorted(
        items,
        key=lambda item: (-item["value"] / item["weight"], -item["value"], item["weight"], item["id"]),
    )


def solve_by_branch_and_bound(items, capacity):
    ordered = sort_items_for_search(items)
    best_value = 0
    best_weight = 0
    best_ids = []
    node_count = 0

    def upper_bound(index, current_value, remaining_capacity):
        bound = float(current_value)
        for item in ordered[index:]:
            if item["weight"] <= remaining_capacity:
                remaining_capacity -= item["weight"]
                bound += item["value"]
            else:
                bound += item["value"] / item["weight"] * remaining_capacity
                break
        return bound

    def dfs(index, current_weight, current_value, chosen):
        nonlocal best_value, best_weight, best_ids, node_count
        node_count += 1

        if current_value > best_value:
            best_value = current_value
            best_weight = current_weight
            best_ids = chosen.copy()

        if index == len(ordered):
            return

        if upper_bound(index, current_value, capacity - current_weight) <= best_value:
            return

        item = ordered[index]
        if current_weight + item["weight"] <= capacity:
            chosen.append(item["id"])
            dfs(index + 1, current_weight + item["weight"], current_value + item["value"], chosen)
            chosen.pop()

        dfs(index + 1, current_weight, current_value, chosen)

    dfs(0, 0, 0, [])
    return sorted(best_ids), best_weight, best_value, node_count


def measure_branch_and_bound_time(items, capacity, trials=20):
    elapsed_list = []
    result = None

    for _ in range(trials):
        start_time = time.perf_counter()
        result = solve_by_branch_and_bound(items, capacity)
        elapsed_list.append((time.perf_counter() - start_time) * 1000)

    return result, median(elapsed_list)


def analyze_case(items, capacity):
    exhaustive_choices, exhaustive_ms = measure_exhaustive_search_time(items, capacity)
    branch_choice, branch_ms = measure_branch_and_bound_time(items, capacity)
    return {
        "exhaustive_choices": exhaustive_choices,
        "exhaustive_ms": exhaustive_ms,
        "branch_choice": branch_choice,
        "branch_ms": branch_ms,
        "gap": exhaustive_choices[0][2] - branch_choice[2],
    }


def print_branch_result(branch_choice, elapsed_ms):
    ids, weight, value, node_count = branch_choice
    print("[既存の分枝限定法]")
    print("解 =", ids)
    print("使用容量 =", weight)
    print("利得 =", value)
    print("探索ノード数 =", node_count)
    print("時間 =", f"{elapsed_ms:.3f}", "ms")


def print_comparison(gap):
    print("[比較]")
    print("利得差 =", gap)
    if gap == 0:
        print("判定 = 既存の分枝限定法でも最適解に到達")
    else:
        print("判定 = 既存の分枝限定法は最適解に到達していない")


def print_case_report(case_name, items, capacity, analysis, show_items):
    print(SEPARATOR)
    print("ケース:", case_name)
    print_case_data(items, capacity, show_items)
    print()
    print_exhaustive_result(analysis["exhaustive_choices"], analysis["exhaustive_ms"])
    print()
    print_branch_result(analysis["branch_choice"], analysis["branch_ms"])
    print()
    print_comparison(analysis["gap"])
    print()


def run_case(case, show_items):
    analysis = analyze_case(case["items"], case["capacity"])
    print_case_report(case["name"], case["items"], case["capacity"], analysis, show_items=show_items)
    return {
        "item_count": len(case["items"]),
        "capacity": case["capacity"],
        "exhaustive_ms": analysis["exhaustive_ms"],
        "branch_ms": analysis["branch_ms"],
        "node_count": analysis["branch_choice"][3],
        "gap": analysis["gap"],
    }


def print_time_summary(summary_rows):
    print(SEPARATOR)
    print("製品数と実行時間のまとめ")
    print("製品数 容量制約 完全列挙法ms 分枝限定法ms 探索ノード数 利得差")
    for row in summary_rows:
        print(
            f"{row['item_count']:>4} {row['capacity']:>8} "
            f"{row['exhaustive_ms']:>12.3f} {row['branch_ms']:>12.3f} "
            f"{row['node_count']:>12} {row['gap']:>6}"
        )


def print_large_time_summary(summary_rows):
    print(SEPARATOR)
    print("大きいデータの平均実行時間まとめ")
    print("各製品数で 5 ケースを作成し、各ケースの時間中央値を平均")
    print("製品数 平均容量 分枝限定法ms 平均探索ノード数")
    for row in summary_rows:
        print(
            f"{row['item_count']:>4} {row['capacity']:>8.1f} "
            f"{row['branch_ms']:>12.3f} {row['node_count']:>16.1f}"
        )


def run_behavior_comparison():
    print("具体例での比較")
    for case in COMPARISON_CASES:
        run_case(case, show_items=True)


def run_size_comparison():
    print("製品数と実行時間の比較")
    summary_rows = []
    for item_count in SIZE_LIST:
        case = create_size_case(item_count)
        analysis = analyze_case(case["items"], case["capacity"])
        summary_rows.append(
            {
                "item_count": item_count,
                "capacity": case["capacity"],
                "exhaustive_ms": analysis["exhaustive_ms"],
                "branch_ms": analysis["branch_ms"],
                "node_count": analysis["branch_choice"][3],
                "gap": analysis["gap"],
            }
        )
    print_time_summary(summary_rows)


def run_large_size_comparison():
    print("大きいデータでの追加実験")
    summary_rows = []
    for item_count in LARGE_SIZE_LIST:
        capacity_sum = 0.0
        branch_ms_sum = 0.0
        node_count_sum = 0.0

        for seed in LARGE_SEED_LIST:
            case = create_fixed_seed_case(
                item_count,
                seed,
                weight_min=LARGE_CASE_SETTINGS["weight_min"],
                weight_max=LARGE_CASE_SETTINGS["weight_max"],
                value_min=LARGE_CASE_SETTINGS["value_min"],
                value_max=LARGE_CASE_SETTINGS["value_max"],
                capacity_ratio=LARGE_CASE_SETTINGS["capacity_ratio"],
                name=f"{item_count}製品の追加実験データ",
            )
            branch_choice, branch_ms = measure_branch_and_bound_time(case["items"], case["capacity"], trials=10)
            capacity_sum += case["capacity"]
            branch_ms_sum += branch_ms
            node_count_sum += branch_choice[3]

        summary_rows.append(
            {
                "item_count": item_count,
                "capacity": capacity_sum / len(LARGE_SEED_LIST),
                "branch_ms": branch_ms_sum / len(LARGE_SEED_LIST),
                "node_count": node_count_sum / len(LARGE_SEED_LIST),
            }
        )
    print_large_time_summary(summary_rows)


def run_task3_existing():
    run_behavior_comparison()
    run_size_comparison()
    run_large_size_comparison()


if __name__ == "__main__":
    run_task3_existing()
