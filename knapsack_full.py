from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Item:
    id: int
    weight: int
    value: int

    @property
    def ratio(self) -> float:
        return self.value / self.weight


@dataclass
class Solution:
    algorithm: str
    value: int
    weight: int
    item_ids: list[int]
    elapsed_ms: float
    optimal: bool | None = None


def get_predefined_cases() -> dict[str, tuple[int, list[Item]]]:
    # 授業でそのまま使える例と、欲張り法の弱点を示す例を用意する。
    return {
        "task1": (
            25,
            [
                Item(1, 3, 3),
                Item(2, 5, 7),
                Item(3, 4, 6),
                Item(4, 2, 3),
                Item(5, 10, 13),
                Item(6, 7, 9),
                Item(7, 1, 2),
                Item(8, 5, 6),
            ],
        ),
        "greedy_bad": (
            50,
            [
                Item(1, 10, 60),
                Item(2, 20, 100),
                Item(3, 30, 120),
            ],
        ),
    }


def sort_items_by_value_density(items: list[Item]) -> list[Item]:
    # 欲張り法と分岐限定法では、利得/容量の高い順に並べる。
    return sorted(items, key=lambda item: (-item.ratio, -item.value, item.weight, item.id))


def solve_by_exhaustive_search(items: list[Item], capacity: int) -> Solution:
    started = time.perf_counter()
    best_value = -1
    best_weight = 0
    best_ids: list[int] = []

    # 0 から 2^n - 1 までのビット列を、各製品を入れる/入れないの組み合わせとして使う。
    for mask in range(1 << len(items)):
        weight = 0
        value = 0
        chosen: list[int] = []

        for i, item in enumerate(items):
            if mask >> i & 1:
                weight += item.weight
                value += item.value
                chosen.append(item.id)

        # 資料の説明に合わせて、まず組み合わせ全体の容量と利得を計算してから制約を判定する。
        if weight > capacity:
            continue

        if value > best_value:
            best_value = value
            best_weight = weight
            best_ids = chosen

    elapsed_ms = (time.perf_counter() - started) * 1000
    return Solution("exhaustive_search", best_value, best_weight, best_ids, elapsed_ms)


def solve_by_greedy_ratio(items: list[Item], capacity: int) -> Solution:
    started = time.perf_counter()
    chosen: list[int] = []
    weight = 0
    value = 0

    # 利得/容量が高い製品から、入る限り順に採用する。
    for item in sort_items_by_value_density(items):
        if weight + item.weight <= capacity:
            chosen.append(item.id)
            weight += item.weight
            value += item.value

    elapsed_ms = (time.perf_counter() - started) * 1000
    return Solution("greedy_ratio", value, weight, sorted(chosen), elapsed_ms)


def solve_by_branch_and_bound(items: list[Item], capacity: int) -> Solution:
    ordered = sort_items_by_value_density(items)
    started = time.perf_counter()
    best_value = 0
    best_weight = 0
    best_ids: list[int] = []

    def upper_bound(index: int, current_value: int, remaining_capacity: int) -> float:
        # 残りを「分数ナップサック」として詰めたと仮定し、この枝で到達可能な上限値を見積もる。
        bound = float(current_value)
        for item in ordered[index:]:
            if item.weight <= remaining_capacity:
                remaining_capacity -= item.weight
                bound += item.value
            else:
                bound += item.ratio * remaining_capacity
                break
        return bound

    def dfs(index: int, current_weight: int, current_value: int, chosen: list[int]) -> None:
        nonlocal best_value, best_weight, best_ids

        if current_value > best_value:
            best_value = current_value
            best_weight = current_weight
            best_ids = chosen.copy()

        if index == len(ordered):
            return

        # 上限を見ても今の最良解を超えられない枝は探索しない。
        if upper_bound(index, current_value, capacity - current_weight) <= best_value:
            return

        item = ordered[index]
        # まず「その製品を入れる」分岐を試す。
        if current_weight + item.weight <= capacity:
            chosen.append(item.id)
            dfs(index + 1, current_weight + item.weight, current_value + item.value, chosen)
            chosen.pop()

        # 次に「その製品を入れない」分岐を試す。
        dfs(index + 1, current_weight, current_value, chosen)

    dfs(0, 0, 0, [])
    elapsed_ms = (time.perf_counter() - started) * 1000
    return Solution("branch_and_bound", best_value, best_weight, sorted(best_ids), elapsed_ms)


def load_problem_case(case_name: str | None, json_path: str | None) -> tuple[int, list[Item]]:
    if json_path:
        # JSON から読み込めるようにしておくと、実験用データを差し替えやすい。
        raw = json.loads(Path(json_path).read_text())
        items = [Item(item["id"], item["weight"], item["value"]) for item in raw["items"]]
        return raw["capacity"], items

    cases = get_predefined_cases()
    if case_name not in cases:
        raise SystemExit(f"unknown case: {case_name}")
    return cases[case_name]


def generate_random_problem_case(size: int, seed: int, capacity_ratio: float) -> tuple[int, list[Item]]:
    # 課題2の比較実験用に、再現可能な乱数データを作る。
    rng = random.Random(seed)
    items: list[Item] = []
    total_weight = 0
    for i in range(1, size + 1):
        weight = rng.randint(1, 20)
        value = rng.randint(1, 30)
        items.append(Item(i, weight, value))
        total_weight += weight

    capacity = max(1, int(total_weight * capacity_ratio))
    return capacity, items


def annotate_optimal_solutions(results: list[Solution]) -> None:
    # 完全列挙法の値を基準にして、他の手法が最適解に一致したかを付与する。
    optimum = None
    for result in results:
        if result.algorithm == "exhaustive_search":
            optimum = result.value
            break
    if optimum is None:
        return

    for result in results:
        result.optimal = result.value == optimum


def get_algorithm_label(algorithm: str) -> str:
    labels = {
        "exhaustive_search": "完全列挙法",
        "greedy_ratio": "欲張り法",
        "branch_and_bound": "分岐限定法",
    }
    return labels.get(algorithm, algorithm)


def display_problem_case(items: list[Item], capacity: int) -> None:
    print("容量 =", capacity)
    print("製品 容量 利得 利得/容量")
    for item in items:
        print(f"{item.id:>2} {item.weight:>6} {item.value:>5} {item.ratio:>5.2f}")
    print()


def display_solutions(results: list[Solution]) -> None:
    print("アルゴリズム       利得   容量   製品               時間ms   最適")
    for result in results:
        optimal = "-" if result.optimal is None else ("はい" if result.optimal else "いいえ")
        algorithm_label = get_algorithm_label(result.algorithm)
        print(
            f"{algorithm_label:<18} {result.value:>5} {result.weight:>6} "
            f"{str(result.item_ids):<18} {result.elapsed_ms:>8.3f}  {optimal}"
        )


def solve_problem_case(capacity: int, items: list[Item], skip_exhaustive_search: bool) -> list[Solution]:
    results: list[Solution] = []
    # 完全列挙法は最適値の基準として使うが、製品数が大きいと重いので省略可能にしている。
    if not skip_exhaustive_search:
        results.append(solve_by_exhaustive_search(items, capacity))
    results.append(solve_by_greedy_ratio(items, capacity))
    results.append(solve_by_branch_and_bound(items, capacity))
    annotate_optimal_solutions(results)
    return results


def handle_solve_command(args: argparse.Namespace) -> None:
    capacity, items = load_problem_case(args.case, args.json)
    display_problem_case(items, capacity)
    results = solve_problem_case(capacity, items, skip_exhaustive_search=args.skip_bruteforce)
    display_solutions(results)


def handle_experiment_command(args: argparse.Namespace) -> None:
    rows: list[dict[str, str | int | float]] = []

    print("製品数 試行 容量 欲張り法利得 最適利得 差 欲張り法ms 分岐限定法ms")
    for size in args.sizes:
        for trial in range(args.trials):
            capacity, items = generate_random_problem_case(
                size, args.seed + size * 1000 + trial, args.capacity_ratio
            )
            # 比較実験では、完全列挙法を最適値の基準として扱う。
            exhaustive = solve_by_exhaustive_search(items, capacity)
            greedy = solve_by_greedy_ratio(items, capacity)
            branch = solve_by_branch_and_bound(items, capacity)

            gap = exhaustive.value - greedy.value
            print(
                f"{size:>4} {trial:>5} {capacity:>8} {greedy.value:>12} "
                f"{exhaustive.value:>7} {gap:>3} {greedy.elapsed_ms:>9.3f} {branch.elapsed_ms:>6.3f}"
            )

            rows.append(
                {
                    "size": size,
                    "trial": trial,
                    "capacity": capacity,
                    "greedy_value": greedy.value,
                    "optimum": exhaustive.value,
                    "gap": gap,
                    "greedy_ms": round(greedy.elapsed_ms, 3),
                    "branch_and_bound_ms": round(branch.elapsed_ms, 3),
                }
            )

    if args.csv:
        with Path(args.csv).open("w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print()
        print("CSVを書き出しました:", args.csv)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="0-1 knapsack playground")
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="solve one case")
    solve_parser.add_argument("--case", default="task1", choices=sorted(get_predefined_cases().keys()))
    solve_parser.add_argument("--json", help="load case from JSON file")
    solve_parser.add_argument("--skip-bruteforce", action="store_true")
    solve_parser.set_defaults(func=handle_solve_command)

    experiment_parser = subparsers.add_parser("experiment", help="run random experiments")
    experiment_parser.add_argument("--sizes", nargs="+", type=int, default=[8, 12, 16])
    experiment_parser.add_argument("--trials", type=int, default=3)
    experiment_parser.add_argument("--seed", type=int, default=42)
    experiment_parser.add_argument("--capacity-ratio", type=float, default=0.4)
    experiment_parser.add_argument("--csv", help="write experiment rows to CSV")
    experiment_parser.set_defaults(func=handle_experiment_command)

    return parser


def run_cli() -> None:
    args = build_argument_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    run_cli()
