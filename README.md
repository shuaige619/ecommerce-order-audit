# 电商订单导出审计

Use when 自媒体带货或电商订单 CSV 导出需要检查完全重复、同订单金额冲突、非法日期、缺失金额、币种和可汇总范围，尤其是保留订单编号与行级证据时。

`ecommerce-order-audit` · 原创 Skill · 内容版本 `3e708c97fab5`

## 适用场景

Use when 自媒体带货或电商订单 CSV 导出需要检查完全重复、同订单金额冲突、非法日期、缺失金额、币种和可汇总范围，尤其是保留订单编号与行级证据时。

## 安装与使用

```sh
git clone https://github.com/shuaige619/ecommerce-order-audit.git
cd ecommerce-order-audit
```

将此目录按宿主支持的方式登记为本地 Skill，或把 [SKILL.md](SKILL.md) 交给支持 Agent Skills 的助手读取。保留 `scripts/`、`references/` 等配套目录的相对位置；下载完成不代表宿主已加载。

需要能读取本地 Markdown 的 Agent 环境。其他工具与依赖以 SKILL.md 中的要求为准。

## 输入与输出

**输入：** 订单 CSV 和字段口径。

**输出：** cleaned.csv、issues.csv、report.md、result.json。

## 使用示例

```text
请使用 ecommerce-order-audit 核对订单数据，保留原表，单列重复、缺失和异常记录，并说明处理依据。
```

以上是调用示例，不是已完成业务运行的记录。

## 工作方式

执行步骤、判断规则和交付标准见 [SKILL.md](SKILL.md)。



## 验证与限制

本发布步骤核对文件结构、README、上传前后文件摘要；未在本步骤重新执行业务效果验证。

模型输出与业务事实需要结合具体材料核对；结构和上传检查不能替代业务效果测试。

## 来源与二创说明

由作者围绕本任务设计，发布包保留当前 Skill 与配套文件。

文件身份与发布标准版本记录在 [发布清单](skill-release.json) 中。问题反馈请附复现输入、期望结果及内容版本，并先移除私人数据。

## 许可证

以仓库随附的 LICENSE / NOTICE 为准；未附许可证的部分尚未授予额外使用许可，请联系作者。
