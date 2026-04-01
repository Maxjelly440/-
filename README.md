# 库存分析模型

这是一个可直接运行的库存分析模型（Python），用于给每个 SKU 计算：

- **ABC 分类**（按年消耗金额累计占比）
- **安全库存**（Safety Stock）
- **再订货点**（Reorder Point, ROP）
- **经济订货量**（EOQ）

## 使用方法

```bash
python3 inventory_model.py sample_inventory.csv -o result.csv
```

## 输入字段

CSV 至少需要这些列：

- `sku`: 物料编码
- `annual_demand`: 年需求量（件）
- `unit_cost`: 单位成本（元）
- `lead_time_days`: 提前期（天）
- `demand_std_daily`: 日需求标准差
- `order_cost`: 单次订货成本（元）
- `holding_rate`: 年持有成本率（如 `0.2`）
- `service_level`: 服务水平（如 `0.95`）

## 模型公式

- 年消耗金额：`annual_demand * unit_cost`
- 安全库存：`z(service_level) * demand_std_daily * sqrt(lead_time_days)`
- 再订货点：`(annual_demand / 365) * lead_time_days + safety_stock`
- EOQ：`sqrt((2 * annual_demand * order_cost) / (unit_cost * holding_rate))`

> 说明：`z(service_level)` 使用正态分布分位数计算。
