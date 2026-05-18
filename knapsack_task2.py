import random
from knapsack_common import SEPARATOR, analyze_case, print_case_report


COMPARISON_CASES = [
    {
        "name": "欲張り法が最適解に到達する例",
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
        "name": "欲張り法が失敗する小さい例",
        "capacity": 50,
        "items": [
            {"id": 1, "weight": 10, "value": 60},
            {"id": 2, "weight": 20, "value": 100},
            {"id": 3, "weight": 30, "value": 120},
        ],
    },
]

SIZE_LIST = [8, 10, 12, 14, 16, 18]
def create_size_case(item_count, seed=100):
    rng = random.Random(seed + item_count)
    items = []
    total_weight = 0

    for item_id in range(1, item_count + 1):
        weight = rng.randint(1, 15)
        value = rng.randint(1, 25)
        items.append({"id": item_id, "weight": weight, "value": value})
        total_weight += weight

    capacity = max(1, int(total_weight * 0.35))
    return {
        "name": f"製品数 {item_count} 個の時間比較データ",
        "capacity": capacity,
        "items": items,
    }

def run_case(case, show_items):
    analysis = analyze_case(case["items"], case["capacity"], include_timing=True)
    print_case_report(case["name"], case["items"], case["capacity"], analysis, show_items=show_items)
    return {
        "item_count": len(case["items"]),
        "capacity": case["capacity"],
        "exhaustive_ms": analysis["exhaustive_ms"],
        "greedy_ms": analysis["greedy_ms"],
        "gap": analysis["gap"],
    }


def print_time_summary(summary_rows):
    print(SEPARATOR)
    print("製品数と実行時間のまとめ")
    print("製品数 容量制約 完全列挙法ms 欲張り法ms 利得差")
    for row in summary_rows:
        print(
            f"{row['item_count']:>4} {row['capacity']:>8} "
            f"{row['exhaustive_ms']:>12.3f} {row['greedy_ms']:>10.3f} {row['gap']:>6}"
        )


def run_behavior_comparison():
    print("成功例と失敗例の比較")
    for case in COMPARISON_CASES:
        run_case(case, show_items=True)


def run_size_comparison():
    print("製品数と実行時間の比較")
    summary_rows = []
    for item_count in SIZE_LIST:
        case = create_size_case(item_count)
        analysis = analyze_case(case["items"], case["capacity"], include_timing=True)
        summary_rows.append(
            {
                "item_count": item_count,
                "capacity": case["capacity"],
                "exhaustive_ms": analysis["exhaustive_ms"],
                "greedy_ms": analysis["greedy_ms"],
                "gap": analysis["gap"],
            }
        )
    print_time_summary(summary_rows)


def run_task2():
    run_behavior_comparison()
    run_size_comparison()


if __name__ == "__main__":
    run_task2()
