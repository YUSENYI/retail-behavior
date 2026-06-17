# API 接口文档

## 1. 文档说明

本文档描述智能零售用户行为分析系统当前后端 API。接口基准来自 `shared/contracts/openapi.yaml`，实际实现位于 `backend/src/api/routes/`，前端调用封装位于 `frontend/src/services/`。

当前系统采用前后端分离架构：

- API 根路径：`/api`
- 本地后端地址：`http://127.0.0.1:8000`
- 本地前端地址：`http://127.0.0.1:5173`
- 前端开发代理：`/api` 代理到 `http://127.0.0.1:8000`
- 数据格式：请求和响应均使用 JSON，导出文件响应返回可下载 URI

## 2. 通用约定

### 2.1 请求头

前端会根据登录身份在 `localStorage.retail-auth` 中保存角色信息，并在请求中自动携带以下请求头：

| 请求头 | 说明 | 示例 |
| --- | --- | --- |
| `x-actor-id` | 当前操作者 ID | `admin001` |
| `x-role` | 当前操作者角色 | `administrator` |
| `x-data-scope` | 当前数据范围 | `all` |
| `content-type` | POST/PATCH 请求体类型 | `application/json` |

OpenAPI 合约预留了 `bearerAuth`，当前演示实现主要使用上述角色请求头完成权限和审计模拟。

### 2.2 角色枚举

| 角色值 | 中文名称 | 典型权限 |
| --- | --- | --- |
| `administrator` | 系统管理员 | 全量查看、报表导出、审计、系统重置 |
| `operations_manager` | 运营经理 | 运营分析、预警处理、报表导出 |
| `analyst` | 数据分析师 | 行为、漏斗、画像、推荐、报表分析 |
| `customer_service_viewer` | 客服主管 | 行为路径、画像、预警查看和处理 |
| `read_only_viewer` | 只读查看员 | 汇总、漏斗、商品热度、报表查看 |

### 2.3 时间与分页参数

部分合约接口支持以下通用查询参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `startTime` | string(date-time) | 是 | 查询开始时间，ISO 8601 格式 |
| `endTime` | string(date-time) | 是 | 查询结束时间，ISO 8601 格式 |
| `page` | integer | 否 | 页码，默认 `1` |
| `pageSize` | integer | 否 | 每页数量，默认 `50`，最大 `200` |
| `productId` | string | 否 | 商品 ID |
| `userId` | string | 否 | 用户 ID |
| `visitorId` | string | 否 | 游客 ID |
| `sessionId` | string | 否 | 会话 ID |
| `channelId` | string | 否 | 渠道 ID |
| `segmentId` | string | 否 | 分群 ID |

说明：当前演示路由中部分筛选参数尚未完全落到后端过滤逻辑，前端会对部分视图做二次筛选。正式联调和验收以 `shared/contracts/openapi.yaml` 的字段约束为准。

### 2.4 通用错误响应

```json
{
  "code": "FORBIDDEN",
  "message": "Caller is not allowed to access this resource or data scope"
}
```

常见状态码：

| 状态码 | 说明 |
| --- | --- |
| `200` | 查询或更新成功 |
| `202` | 行为事件或报表导出请求已接受 |
| `400` | 请求参数或请求体校验失败 |
| `403` | 角色权限或数据范围不允许 |

## 3. 行为事件接口

### 3.1 批量采集行为事件

- 方法：`POST`
- 路径：`/api/events/behavior`
- 用途：采集浏览、点击、搜索、收藏、加购、下单、支付等行为事件。
- 前端封装：`behaviorApi.ingest(events)`

请求体：

```json
{
  "events": [
    {
      "eventId": "evt-20260605-0001",
      "sourceSystem": "frontend",
      "eventType": "browse",
      "userId": "user001",
      "visitorId": "visitor001",
      "sessionId": "session-demo-001",
      "productId": "SKU-001",
      "channelId": "recommendation",
      "occurredAt": "2026-06-05T09:30:00+08:00",
      "metadata": {
        "productName": "云感缓震跑鞋 01",
        "category": "鞋服",
        "price": 272
      }
    }
  ]
}
```

核心字段：

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `eventId` | string | 是 | 行为事件唯一 ID，用于幂等去重 |
| `sourceSystem` | string | 是 | 来源系统 |
| `eventType` | enum | 是 | 行为类型 |
| `userId` | string | 否 | 已登录用户 ID |
| `visitorId` | string | 否 | 匿名游客 ID |
| `sessionId` | string | 是 | 会话 ID |
| `productId` | string | 否 | 商品 ID |
| `orderId` | string | 否 | 订单 ID |
| `paymentId` | string | 否 | 支付 ID |
| `channelId` | string | 是 | 渠道 ID |
| `searchKeyword` | string | 否 | 搜索关键词 |
| `occurredAt` | string(date-time) | 是 | 业务发生时间 |
| `metadata` | object | 否 | 商品名、类目、价格、数量等扩展信息 |

行为类型枚举：

| 值 | 中文含义 |
| --- | --- |
| `browse` | 浏览 |
| `click` | 点击 |
| `search` | 搜索 |
| `favorite` | 收藏 |
| `cart_add` | 加购 |
| `order_submit` | 提交订单 |
| `payment_attempt` | 发起支付 |
| `payment_success` | 支付成功 |

成功响应：

```json
{
  "acceptedCount": 1,
  "duplicateCount": 0,
  "invalidCount": 0,
  "delayedCount": 0,
  "quarantinedCount": 0,
  "results": [
    {
      "eventId": "evt-20260605-0001",
      "state": "accepted"
    }
  ]
}
```

幂等状态：

| 值 | 说明 |
| --- | --- |
| `accepted` | 已接受并参与分析 |
| `duplicate` | 重复事件，不重复计数 |
| `invalid` | 字段或业务规则不合法 |
| `delayed` | 延迟到达事件 |
| `quarantined` | 异常隔离，不进入有效指标 |

### 3.2 查询行为明细

- 方法：`GET`
- 路径：`/api/behavior/events`
- 用途：查询行为事件明细，用于行为明细表和路径分析。
- 前端封装：`behaviorApi.list()`

合约查询参数：

| 参数 | 说明 |
| --- | --- |
| `startTime` / `endTime` | 按行为发生时间筛选 |
| `productId` | 按商品筛选 |
| `userId` / `visitorId` | 按用户或游客筛选 |
| `sessionId` | 按会话筛选 |
| `channelId` | 按渠道筛选 |
| `eventType` | 按行为类型筛选 |
| `page` / `pageSize` | 分页 |

响应字段：

| 字段 | 说明 |
| --- | --- |
| `items` | 行为事件列表 |
| `page` | 当前页码 |
| `pageSize` | 每页数量 |
| `total` | 总记录数 |
| `freshnessAt` | 数据新鲜度时间 |

当前前端直接按数组兼容展示，后端演示实现可能返回事件数组；合约目标响应为分页对象。

### 3.3 查询用户行为路径

- 方法：`GET`
- 路径：`/api/behavior/journeys/{subjectId}`
- 用途：按用户或游客查询从访问、浏览、点击、加购、下单到支付的时间线。
- 前端封装：`behaviorApi.journey(subjectId)`

路径参数：

| 参数 | 说明 |
| --- | --- |
| `subjectId` | 用户 ID 或游客 ID |

合约查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `subjectType` | 是 | `user` 或 `visitor` |
| `startTime` | 是 | 查询开始时间 |
| `endTime` | 是 | 查询结束时间 |

响应核心字段：

| 字段 | 说明 |
| --- | --- |
| `subjectId` | 查询对象 ID |
| `subjectType` | 查询对象类型 |
| `events` | 按时间排序的行为事件 |
| `freshnessAt` | 数据新鲜度时间 |

## 4. 分析指标接口

### 4.1 查询行为汇总指标

- 方法：`GET`
- 路径：`/api/analytics/behavior-summary`
- 用途：查询运营总览核心指标、来源分布和搜索关键词。
- 前端封装：`analyticsApi.summary()`

支持参数：`startTime`、`endTime`、`productId`、`channelId`、`segmentId`。

响应示例：

```json
{
  "metrics": [
    {
      "key": "visits",
      "name": "访问量",
      "value": 1200,
      "unit": "count",
      "metricVersion": "v1",
      "freshnessAt": "2026-06-05T09:35:00+08:00",
      "validationState": "valid"
    }
  ],
  "filters": {},
  "freshnessAt": "2026-06-05T09:35:00+08:00"
}
```

指标单位：

| 单位 | 说明 |
| --- | --- |
| `count` | 次数或人数 |
| `amount` | 金额 |
| `percent` | 百分比 |
| `seconds` | 时长 |
| `rank` | 排名 |

### 4.2 查询转化漏斗

- 方法：`GET`
- 路径：`/api/analytics/funnel`
- 用途：查询浏览、点击、加购、下单、支付之间的转化与流失。
- 前端封装：`analyticsApi.funnel()`

支持参数：`startTime`、`endTime`、`productId`、`channelId`、`segmentId`。

响应字段：

| 字段 | 说明 |
| --- | --- |
| `stages` | 漏斗阶段列表 |
| `biggestDropoffStage` | 最大流失阶段 |
| `freshnessAt` | 数据新鲜度时间 |

阶段字段：

| 字段 | 说明 |
| --- | --- |
| `stage` | `browse`、`click`、`cart`、`order`、`payment` |
| `enteredCount` | 进入该阶段数量 |
| `convertedCount` | 转入下一阶段数量 |
| `dropoffCount` | 流失数量 |
| `conversionRate` | 转化率，范围 0 到 100 |
| `dropoffRate` | 流失率，范围 0 到 100 |

### 4.3 查询商品热度排行

- 方法：`GET`
- 路径：`/api/analytics/product-heat`
- 用途：按行为热度或转化率查询商品排行。
- 前端封装：`analyticsApi.productHeat(rankBy)`

查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `rankBy` | 是 | 排序口径 |
| `startTime` / `endTime` | 合约必填 | 时间范围 |
| `channelId` | 否 | 渠道 |
| `page` / `pageSize` | 否 | 分页 |

`rankBy` 枚举：

| 值 | 中文含义 |
| --- | --- |
| `browse` | 浏览排行 |
| `click` | 点击排行 |
| `cart_add` | 加购排行 |
| `favorite` | 收藏排行 |
| `purchase` | 购买排行 |
| `conversion_rate` | 转化率排行 |

响应字段：

| 字段 | 说明 |
| --- | --- |
| `productId` | 商品 ID |
| `productName` | 商品名称 |
| `rank` | 排名 |
| `value` | 当前排行口径的数值 |
| `unit` | 单位 |
| `conversionRate` | 转化率 |

## 5. 用户画像与分群接口

### 5.1 查询用户画像

- 方法：`GET`
- 路径：`/api/profiles/{userId}`
- 用途：查询单个用户的脱敏画像。

响应字段：

| 字段 | 说明 |
| --- | --- |
| `userId` | 用户 ID |
| `maskedUser` | 脱敏用户信息 |
| `consumptionLevel` | 消费能力：`low`、`medium`、`high`、`very_high` |
| `interestTags` | 兴趣标签 |
| `activityLevel` | 活跃度：`low`、`medium`、`high` |
| `valueGrade` | 价值等级：`low`、`medium`、`high`、`strategic` |
| `updatedAt` | 画像更新时间 |

### 5.2 查询用户分群

- 方法：`GET`
- 路径：`/api/segments`
- 用途：查询系统已识别的用户分群。

分群类型：

| 值 | 中文含义 |
| --- | --- |
| `high_value` | 高价值用户 |
| `potential` | 潜力用户 |
| `new_user` | 新用户 |
| `price_sensitive` | 价格敏感用户 |
| `silent` | 沉默用户 |
| `churn_risk` | 流失风险用户 |

### 5.3 查询分群用户

- 方法：`GET`
- 路径：`/api/segments/{segmentId}/users`
- 用途：查询某个分群下的用户列表。

响应字段：

| 字段 | 说明 |
| --- | --- |
| `items` | 分群成员 |
| `userId` | 用户 ID |
| `maskedUser` | 脱敏用户信息 |
| `reason` | 入群原因 |
| `score` | 分群评分 |
| `page` / `pageSize` / `total` | 分页信息 |

### 5.4 查询购买意向用户

- 方法：`GET`
- 路径：`/api/purchase-intent/users`
- 用途：识别高、中、低购买意向或加购未支付用户。

查询参数：

| 参数 | 说明 |
| --- | --- |
| `intentLevel` | `high`、`medium`、`low`、`cart_unpaid` |
| `productId` | 商品 ID |
| `page` / `pageSize` | 分页 |

## 6. 预警与推荐接口

### 6.1 查询预警列表

- 方法：`GET`
- 路径：`/api/alerts`
- 用途：查询低活跃、流失风险、转化异常和行为数据异常预警。
- 前端封装：`alertRecommendationApi.alerts()`

查询参数：

| 参数 | 说明 |
| --- | --- |
| `alertType` | 预警类型 |
| `status` | 预警状态 |
| `startTime` / `endTime` | 创建时间范围 |

预警类型：

| 值 | 中文含义 |
| --- | --- |
| `low_activity` | 低活跃提醒 |
| `churn_risk` | 流失风险预警 |
| `conversion_anomaly` | 转化异常预警 |
| `behavior_data_anomaly` | 行为数据异常 |

预警状态：

| 值 | 中文含义 |
| --- | --- |
| `new` | 新建 |
| `acknowledged` | 已确认 |
| `processing` | 处理中 |
| `resolved` | 已解决 |
| `ignored` | 已忽略 |

### 6.2 更新预警状态

- 方法：`PATCH`
- 路径：`/api/alerts/{alertId}`
- 用途：更新预警处理状态。

请求体：

```json
{
  "status": "acknowledged",
  "reason": "运营已确认并跟进"
}
```

当前演示路由也兼容 `?status=acknowledged` 形式。

### 6.3 查询推荐分析

- 方法：`GET`
- 路径：`/api/recommendations/analysis`
- 用途：查询面向用户或分群的推荐结果与推荐理由。
- 前端封装：`alertRecommendationApi.recommendations()`

查询参数：

| 参数 | 说明 |
| --- | --- |
| `userId` | 用户 ID |
| `segmentId` | 分群 ID |
| `basisType` | 推荐依据 |

推荐依据：

| 值 | 中文含义 |
| --- | --- |
| `browse_history` | 浏览历史 |
| `purchase_history` | 购买历史 |
| `similar_users` | 相似用户 |
| `user_profile` | 用户画像 |

## 7. 报表与审计接口

### 7.1 查询报表列表

- 方法：`GET`
- 路径：`/api/reports`
- 用途：查询当前角色可见的报表。
- 前端封装：`reportApi.reports()`

查询参数：

| 参数 | 说明 |
| --- | --- |
| `reportType` | 报表类型 |
| `startTime` / `endTime` | 报表创建或统计时间范围 |

报表类型：

| 值 | 中文含义 |
| --- | --- |
| `behavior_detail` | 用户行为明细 |
| `product_analysis` | 商品分析报表 |
| `funnel` | 转化漏斗报表 |
| `user_profile` | 用户画像报表 |
| `user_segment` | 用户分群报表 |
| `sales_conversion` | 销售转化报表 |
| `operation_effect` | 运营效果报表 |

### 7.2 创建报表导出

- 方法：`POST`
- 路径：`/api/reports/{reportType}/exports`
- 用途：创建授权报表导出任务。
- 前端封装：`reportApi.exportReport(reportType, filters)`

请求体：

```json
{
  "filters": {
    "startTime": "2026-06-05T00:00:00+08:00",
    "endTime": "2026-06-05T23:59:59+08:00",
    "channelId": "recommendation"
  },
  "reason": "每日运营复盘"
}
```

响应字段：

| 字段 | 说明 |
| --- | --- |
| `reportId` | 报表 ID |
| `reportType` | 报表类型 |
| `status` | `ready`、`queued`、`failed`、`expired` |
| `sensitiveDataState` | `masked`、`unmasked_authorized`、`not_applicable` |
| `exportUri` | 导出文件地址 |
| `createdAt` | 创建时间 |
| `freshnessAt` | 数据新鲜度时间 |

权限说明：

- 具备导出权限的角色可以生成导出文件。
- 无导出权限的角色会返回 `403`。
- 敏感字段默认脱敏，敏感数据访问和导出会写入审计日志。

### 7.3 查询审计日志

- 方法：`GET`
- 路径：`/api/audit-logs`
- 用途：查询登录、查询、导出、预警处理、系统重置等审计记录。
- 前端封装：`reportApi.auditLogs()`

响应字段：

| 字段 | 说明 |
| --- | --- |
| `auditId` | 审计记录 ID |
| `actorId` | 操作者 ID |
| `actorRole` | 操作者角色 |
| `action` | 操作动作 |
| `resourceType` | 资源类型 |
| `resourceId` | 资源 ID |
| `result` | `success`、`denied`、`failed` |
| `reason` | 操作原因或失败原因 |
| `createdAt` | 记录时间 |

## 8. 系统管理接口

### 8.1 重置系统演示数据

- 方法：`POST`
- 路径：`/api/system/reset`
- 用途：清空行为事件、指标快照、画像、分群、预警、推荐、报表和审计日志，用于演示环境重新开始。

成功响应：

```json
{
  "status": "reset",
  "cleared": [
    "behavior_events",
    "audit_logs",
    "metric_snapshots",
    "funnel_stage_snapshots",
    "users",
    "visitors",
    "channels",
    "sessions",
    "products",
    "orders",
    "payments",
    "profiles",
    "segments",
    "alerts",
    "recommendations",
    "reports"
  ]
}
```

注意：该接口仅供开发和演示环境使用，生产环境应增加强鉴权、二次确认和操作审批。

## 9. 接口联调示例

### 9.1 采集单条浏览行为

```bash
curl -X POST "http://127.0.0.1:8000/api/events/behavior" \
  -H "content-type: application/json" \
  -H "x-actor-id: admin001" \
  -H "x-role: administrator" \
  -H "x-data-scope: all" \
  -d '{
    "events": [
      {
        "eventId": "evt-demo-browse-001",
        "sourceSystem": "frontend",
        "eventType": "browse",
        "userId": "user001",
        "sessionId": "session-demo-001",
        "productId": "SKU-001",
        "channelId": "recommendation",
        "occurredAt": "2026-06-05T09:30:00+08:00",
        "metadata": {
          "productName": "云感缓震跑鞋 01",
          "category": "鞋服",
          "price": 272
        }
      }
    ]
  }'
```

### 9.2 查询核心指标

```bash
curl "http://127.0.0.1:8000/api/analytics/behavior-summary" \
  -H "x-actor-id: ops001" \
  -H "x-role: operations_manager" \
  -H "x-data-scope: all"
```

### 9.3 导出行为明细报表

```bash
curl -X POST "http://127.0.0.1:8000/api/reports/behavior_detail/exports" \
  -H "content-type: application/json" \
  -H "x-actor-id: admin001" \
  -H "x-role: administrator" \
  -H "x-data-scope: all" \
  -d '{
    "filters": {
      "startTime": "2026-06-05T00:00:00+08:00",
      "endTime": "2026-06-05T23:59:59+08:00"
    },
    "reason": "演示导出"
  }'
```

## 10. 验收关注点

1. 行为采集必须按 `eventId` 幂等去重，重复事件不能重复计入指标。
2. 访问、浏览、点击、加购、下单、支付路径需要可追溯到用户、会话、商品、订单和支付。
3. 所有报表、导出、画像、分群、预警、推荐和审计接口需要校验角色和数据范围。
4. 手机、邮箱、地址、支付标识等敏感字段默认脱敏。
5. 指标不能出现负数，转化率和流失率必须在 0 到 100 之间。
6. 核心指标响应需要带 `freshnessAt`，正常运营场景目标新鲜度为 5 分钟内。
