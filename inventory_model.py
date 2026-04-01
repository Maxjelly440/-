#!/usr/bin/env python3
"""库存分析模型

功能：
1) ABC 分类（按年消耗金额）
2) 安全库存与再订货点（ROP）
3) EOQ 经济订货量

输入：CSV，至少包含以下列：
- sku: 物料编码
- annual_demand: 年需求量（件）
- unit_cost: 单位成本（元）
- lead_time_days: 采购提前期（天）
- demand_std_daily: 日需求标准差
- order_cost: 每次订货成本（元）
- holding_rate: 年持有成本率（如 0.2）
- service_level: 服务水平（如 0.95）
"""

from __future__ import annotations

import argparse
import csv
import math
from statistics import NormalDist
from typing import Dict, List


def z_score(service_level: float) -> float:
    service_level = min(max(service_level, 0.5), 0.9999)
    return NormalDist().inv_cdf(service_level)


def abc_classification(records: List[Dict[str, float]]) -> None:
    for r in records:
        r["annual_consumption_value"] = r["annual_demand"] * r["unit_cost"]

    total_value = sum(r["annual_consumption_value"] for r in records) or 1.0
    records.sort(key=lambda x: x["annual_consumption_value"], reverse=True)

    cum = 0.0
    for r in records:
        cum += r["annual_consumption_value"]
        ratio = cum / total_value
        if ratio <= 0.8:
            r["abc"] = "A"
        elif ratio <= 0.95:
            r["abc"] = "B"
        else:
            r["abc"] = "C"


def compute_metrics(records: List[Dict[str, float]]) -> None:
    for r in records:
        d = r["annual_demand"]
        lt = r["lead_time_days"]
        sigma_d = r["demand_std_daily"]
        s = r["order_cost"]
        c = r["unit_cost"]
        h_rate = r["holding_rate"]
        sl = r["service_level"]

        daily_demand = d / 365.0
        z = z_score(sl)
        safety_stock = z * sigma_d * math.sqrt(max(lt, 0.0))
        rop = daily_demand * lt + safety_stock

        h = c * h_rate
        eoq = math.sqrt((2 * d * s) / h) if h > 0 else 0.0

        r["daily_demand"] = daily_demand
        r["z"] = z
        r["safety_stock"] = safety_stock
        r["reorder_point"] = rop
        r["eoq"] = eoq


def load_csv(path: str) -> List[Dict[str, float]]:
    rows: List[Dict[str, float]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            rows.append(
                {
                    "sku": raw["sku"],
                    "annual_demand": float(raw["annual_demand"]),
                    "unit_cost": float(raw["unit_cost"]),
                    "lead_time_days": float(raw["lead_time_days"]),
                    "demand_std_daily": float(raw["demand_std_daily"]),
                    "order_cost": float(raw["order_cost"]),
                    "holding_rate": float(raw["holding_rate"]),
                    "service_level": float(raw["service_level"]),
                }
            )
    return rows


def save_csv(path: str, records: List[Dict[str, float]]) -> None:
    fieldnames = [
        "sku",
        "annual_demand",
        "unit_cost",
        "annual_consumption_value",
        "abc",
        "daily_demand",
        "z",
        "safety_stock",
        "reorder_point",
        "eoq",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow({k: round(r[k], 4) if isinstance(r[k], float) else r[k] for k in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser(description="库存分析模型")
    parser.add_argument("input_csv", help="输入 CSV")
    parser.add_argument("-o", "--output", default="inventory_analysis_output.csv", help="输出 CSV")
    args = parser.parse_args()

    records = load_csv(args.input_csv)
    compute_metrics(records)
    abc_classification(records)
    save_csv(args.output, records)

    print(f"分析完成：{len(records)} 条 SKU，输出文件 {args.output}")


if __name__ == "__main__":
    main()
