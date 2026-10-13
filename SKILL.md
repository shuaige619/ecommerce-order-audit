---
name: ecommerce-order-audit
description: Use when 自媒体带货或电商订单 CSV 导出需要检查完全重复、同订单金额冲突、非法日期、缺失金额、币种和可汇总范围，尤其是保留订单编号与行级证据时。
---

# 电商订单导出审计

读取用户输入 CSV、指标范围和指定输出目录，确认该表是一行一订单或订单快照。脚本列合同为 `order_id,date,channel,amount,currency,status`。列名不符先列映射和待确认，不猜字段；确认后另存规范输入，保留原文件。Shopify 多商品订单明细不能直接当订单重复处理，也不能填充每行订单总额后相加；粒度未明先说明缺口。

读取本技能的 [审计脚本](scripts/audit_orders.py)，用本机 Python 调用：`python3 "<技能目录>/scripts/audit_orders.py" --input "<CSV绝对路径>" --out "<用户输出目录>"`。路径来自实际输入。工具不可用、脚本缺失、解析失败或目录拒绝时报告真实错误；不编造已生成文件，不擅自改用户目录或覆盖旧文件。

脚本负责确定计算：订单编号按文本保留前导零；全字段相同才为完全重复；同 ID 不同金额或其他关键值的所有行隔离待确认。无效日期、缺失/非数值金额列问题，不能改成零。合法 USD 等币种独立汇总，不因非 CNY 判错；不换汇、不猜退款状态、不推算营收。读回脚本结果再写报告，不重写脚本生成的 JSON、清理表或问题表。

交付 UTF-8 `report.md`、`result.json`、`cleaned.csv`、`issues.csv`。后三项由脚本产生。JSON 顶层含 `skill`（本技能名）、`source_ids`（全部原始行）、`input_rows`（整数）与四个数组：exact_duplicates 条目含 kept_source_id/duplicate_source_id/order_id；conflicts 含 order_id/source_ids/differing_fields/rows；issues 含 source_id/order_id/row_number/code/field/value；aggregates 含 currency/amount/order_count/source_ids，amount 为数字，仅可信 paid。cleaned.csv 仅收可信 paid，保留原列和 source_id/row_number；issues.csv 逐问题行。行级来源为“订单ID@文件名:CSV物理行号”，首数据行为第 2 行。

报告列输入覆盖、重复/冲突、异常处置和各币种可靠 paid 合计，说明排除口径与待确认。不把全部订单金额称为已收款或净收入。回读四文件，核对 JSON 可解析、来源与行数对应、报告数字等于脚本结果；最终提供真实路径。只审计本地文件，不更新店铺或财务系统。
