from knapsack_common import analyze_case, print_case_report


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


def run_task1():
    analysis = analyze_case(TASK1_CASE["items"], TASK1_CASE["capacity"], include_timing=False)
    print_case_report(
        TASK1_CASE["name"],
        TASK1_CASE["items"],
        TASK1_CASE["capacity"],
        analysis,
        show_items=True,
        show_comparison=False,
    )


if __name__ == "__main__":
    run_task1()
