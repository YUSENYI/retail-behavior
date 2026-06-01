# 数据库设计文档

## 1. 设计目标

数据库采用 MySQL 8.x，作为智能零售用户行为分析系统的核心数据源。设计目标：

- 持久化用户、商品、行为、订单、支付和审计数据。
- 支持行为链路追踪。
- 支持核心指标统计。
- 支持转化漏斗、商品热度、用户画像、智能推荐。
- 支持角色权限和操作日志审计。

## 2. 数据库命名

建议数据库名：

```sql
retail_behavior
```

字符集：

```sql
utf8mb4
```

排序规则：

```sql
utf8mb4_unicode_ci
```

## 3. 核心表清单

| 表名 | 说明 |
|---|---|
| `user_info` | 零售用户信息表 |
| `product_info` | 商品信息表 |
| `behavior_event` | 用户行为事件表 |
| `order_info` | 订单主表 |
| `order_detail` | 订单明细表 |
| `payment_record` | 支付记录表 |
| `sys_user` | 后台系统用户表 |
| `sys_role` | 后台角色表 |
| `sys_permission` | 权限点表 |
| `sys_role_permission` | 角色权限关联表 |
| `operation_log` | 操作日志表 |
| `metric_snapshot` | 指标快照表 |
| `user_profile_snapshot` | 用户画像快照表 |
| `user_segment_result` | 用户分群结果表 |
| `alert_record` | 告警记录表 |
| `recommendation_result` | 推荐结果表 |
| `report_task` | 报表任务表 |
| `report_snapshot` | 报表快照表 |

## 4. 表结构设计

### 4.1 user_info

零售用户信息表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `user_id` | varchar(64) PK | 用户 ID |
| `nickname` | varchar(64) | 昵称 |
| `phone_masked` | varchar(32) | 脱敏手机号 |
| `city` | varchar(64) | 城市 |
| `member_level` | varchar(32) | 会员等级 |
| `register_time` | datetime | 注册时间 |
| `status` | varchar(32) | 状态 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

索引：

- `idx_user_city(city)`
- `idx_user_member_level(member_level)`

### 4.2 product_info

商品信息表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `product_id` | varchar(64) PK | 商品 ID |
| `name` | varchar(128) | 商品名称 |
| `brand` | varchar(64) | 品牌 |
| `category` | varchar(64) | 类目 |
| `sku` | varchar(64) | SKU |
| `price` | decimal(12,2) | 售价 |
| `stock` | int | 库存 |
| `rating` | decimal(3,1) | 评分 |
| `image_url` | varchar(255) | 图片地址 |
| `description` | text | 商品介绍 |
| `status` | varchar(32) | 状态 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

索引：

- `idx_product_category(category)`
- `idx_product_brand(brand)`
- `idx_product_price(price)`

### 4.3 behavior_event

用户行为事件表，是系统最核心的数据表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint PK auto_increment | 主键 |
| `event_id` | varchar(128) | 前端事件 ID |
| `source_system` | varchar(64) | 来源系统 |
| `event_type` | varchar(32) | 行为类型 |
| `user_id` | varchar(64) | 用户 ID |
| `visitor_id` | varchar(64) | 访客 ID |
| `session_id` | varchar(128) | 会话 ID |
| `product_id` | varchar(64) | 商品 ID |
| `order_id` | varchar(64) | 订单 ID |
| `payment_id` | varchar(64) | 支付 ID |
| `channel_id` | varchar(64) | 渠道 |
| `search_keyword` | varchar(128) | 搜索词 |
| `occurred_at` | datetime | 行为发生时间 |
| `received_at` | datetime | 服务端接收时间 |
| `idempotency_state` | varchar(32) | 幂等状态 |
| `exclusion_reason` | varchar(255) | 排除原因 |
| `metadata_json` | json | 扩展字段 |

唯一约束：

- `uk_behavior_event(source_system, event_id)`

索引：

- `idx_behavior_user_time(user_id, occurred_at)`
- `idx_behavior_session_time(session_id, occurred_at)`
- `idx_behavior_product_type(product_id, event_type)`
- `idx_behavior_type_time(event_type, occurred_at)`
- `idx_behavior_channel_time(channel_id, occurred_at)`

### 4.4 order_info

订单主表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `order_id` | varchar(64) PK | 订单 ID |
| `user_id` | varchar(64) | 用户 ID |
| `session_id` | varchar(128) | 会话 ID |
| `total_amount` | decimal(12,2) | 订单金额 |
| `order_status` | varchar(32) | 订单状态 |
| `channel_id` | varchar(64) | 来源渠道 |
| `created_at` | datetime | 创建时间 |
| `paid_at` | datetime | 支付时间 |

索引：

- `idx_order_user_time(user_id, created_at)`
- `idx_order_status(order_status)`

### 4.5 order_detail

订单明细表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `detail_id` | bigint PK auto_increment | 明细 ID |
| `order_id` | varchar(64) | 订单 ID |
| `product_id` | varchar(64) | 商品 ID |
| `quantity` | int | 数量 |
| `unit_price` | decimal(12,2) | 单价 |
| `amount` | decimal(12,2) | 金额 |

索引：

- `idx_order_detail_order(order_id)`
- `idx_order_detail_product(product_id)`

### 4.6 payment_record

支付记录表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `payment_id` | varchar(64) PK | 支付 ID |
| `order_id` | varchar(64) | 订单 ID |
| `user_id` | varchar(64) | 用户 ID |
| `payment_amount` | decimal(12,2) | 支付金额 |
| `payment_method` | varchar(32) | 支付方式 |
| `payment_status` | varchar(32) | 支付状态 |
| `paid_at` | datetime | 支付时间 |

索引：

- `idx_payment_order(order_id)`
- `idx_payment_user_time(user_id, paid_at)`

### 4.7 sys_user

后台系统用户表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `sys_user_id` | varchar(64) PK | 系统用户 ID |
| `username` | varchar(64) | 登录名 |
| `display_name` | varchar(64) | 显示名 |
| `role_id` | varchar(64) | 角色 ID |
| `status` | varchar(32) | 状态 |
| `created_at` | datetime | 创建时间 |

说明：当前阶段可不实现密码加密和真实登录，后续再扩展 `password_hash`。

### 4.8 sys_role

后台角色表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `role_id` | varchar(64) PK | 角色 ID |
| `role_name` | varchar(64) | 角色名称 |
| `data_scope` | varchar(64) | 数据范围 |
| `description` | varchar(255) | 描述 |

### 4.9 sys_permission

权限点表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `permission_id` | varchar(64) PK | 权限 ID |
| `resource` | varchar(64) | 资源 |
| `action` | varchar(32) | 动作 |
| `description` | varchar(255) | 描述 |

### 4.10 sys_role_permission

角色权限关联表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint PK auto_increment | 主键 |
| `role_id` | varchar(64) | 角色 ID |
| `permission_id` | varchar(64) | 权限 ID |

唯一约束：

- `uk_role_permission(role_id, permission_id)`

### 4.11 operation_log

操作日志表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `log_id` | varchar(64) PK | 日志 ID |
| `actor_id` | varchar(64) | 操作者 |
| `actor_role` | varchar(64) | 操作者角色 |
| `action` | varchar(64) | 操作动作 |
| `resource_type` | varchar(64) | 资源类型 |
| `resource_id` | varchar(128) | 资源 ID |
| `result` | varchar(32) | 操作结果 |
| `reason` | varchar(255) | 失败原因 |
| `ip_address` | varchar(64) | IP 地址 |
| `created_at` | datetime | 操作时间 |

索引：

- `idx_operation_actor_time(actor_id, created_at)`
- `idx_operation_action(action)`

### 4.12 metric_snapshot

指标快照表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `snapshot_id` | varchar(64) PK | 快照 ID |
| `metric_key` | varchar(64) | 指标编码 |
| `metric_name` | varchar(64) | 指标名称 |
| `metric_value` | decimal(18,4) | 指标值 |
| `metric_unit` | varchar(32) | 单位 |
| `window_start` | datetime | 统计窗口开始 |
| `window_end` | datetime | 统计窗口结束 |
| `filter_json` | json | 筛选条件 |
| `validation_state` | varchar(32) | 校验状态 |
| `created_at` | datetime | 创建时间 |

### 4.13 user_profile_snapshot

用户画像快照表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `profile_id` | varchar(64) PK | 画像 ID |
| `user_id` | varchar(64) | 用户 ID |
| `value_level` | varchar(32) | 价值等级 |
| `intent_level` | varchar(32) | 购买意向 |
| `favorite_categories_json` | json | 偏好类目 |
| `price_band_json` | json | 价位偏好 |
| `active_score` | decimal(10,2) | 活跃分 |
| `profile_json` | json | 完整画像 |
| `created_at` | datetime | 创建时间 |

### 4.14 user_segment_result

用户分群结果表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint PK auto_increment | 主键 |
| `user_id` | varchar(64) | 用户 ID |
| `segment_type` | varchar(64) | 分群类型 |
| `score` | decimal(10,2) | 分群得分 |
| `reason` | varchar(255) | 分群原因 |
| `created_at` | datetime | 创建时间 |

### 4.15 alert_record

告警记录表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `alert_id` | varchar(64) PK | 告警 ID |
| `alert_type` | varchar(64) | 告警类型 |
| `severity` | varchar(32) | 严重级别 |
| `status` | varchar(32) | 状态 |
| `trigger_reason` | varchar(255) | 触发原因 |
| `metric_name` | varchar(64) | 相关指标 |
| `metric_value` | decimal(18,4) | 指标值 |
| `threshold_value` | decimal(18,4) | 阈值 |
| `created_at` | datetime | 创建时间 |
| `handled_at` | datetime | 处理时间 |

### 4.16 recommendation_result

推荐结果表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `recommendation_id` | varchar(64) PK | 推荐 ID |
| `user_id` | varchar(64) | 用户 ID |
| `product_id` | varchar(64) | 商品 ID |
| `score` | decimal(10,2) | 推荐分 |
| `basis_json` | json | 推荐依据 |
| `created_at` | datetime | 创建时间 |

### 4.17 report_task

报表任务表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | varchar(64) PK | 任务 ID |
| `report_type` | varchar(64) | 报表类型 |
| `created_by` | varchar(64) | 创建人 |
| `filters_json` | json | 筛选条件 |
| `status` | varchar(32) | 状态 |
| `file_path` | varchar(255) | 文件路径 |
| `created_at` | datetime | 创建时间 |
| `finished_at` | datetime | 完成时间 |

### 4.18 report_snapshot

报表快照表。

| 字段 | 类型 | 说明 |
|---|---|---|
| `snapshot_id` | varchar(64) PK | 快照 ID |
| `task_id` | varchar(64) | 任务 ID |
| `report_type` | varchar(64) | 报表类型 |
| `content_json` | json | 报表内容 |
| `masking_state` | varchar(32) | 脱敏状态 |
| `created_at` | datetime | 创建时间 |

## 5. 关键关系

- 一个用户可以产生多条行为事件。
- 一个商品可以被多条行为事件引用。
- 一个用户可以创建多个订单。
- 一个订单包含多条订单明细。
- 一个订单对应一条或多条支付记录。
- 一个后台用户绑定一个角色。
- 一个角色拥有多个权限。
- 一个用户可以有多个画像快照、分群结果和推荐结果。

## 6. 第一阶段 DDL 示例

```sql
CREATE TABLE behavior_event (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_id VARCHAR(128) NOT NULL,
  source_system VARCHAR(64) NOT NULL,
  event_type VARCHAR(32) NOT NULL,
  user_id VARCHAR(64),
  visitor_id VARCHAR(64),
  session_id VARCHAR(128) NOT NULL,
  product_id VARCHAR(64),
  order_id VARCHAR(64),
  payment_id VARCHAR(64),
  channel_id VARCHAR(64) NOT NULL,
  search_keyword VARCHAR(128),
  occurred_at DATETIME NOT NULL,
  received_at DATETIME NOT NULL,
  idempotency_state VARCHAR(32) NOT NULL DEFAULT 'accepted',
  exclusion_reason VARCHAR(255),
  metadata_json JSON,
  UNIQUE KEY uk_behavior_event (source_system, event_id),
  KEY idx_behavior_user_time (user_id, occurred_at),
  KEY idx_behavior_session_time (session_id, occurred_at),
  KEY idx_behavior_product_type (product_id, event_type),
  KEY idx_behavior_type_time (event_type, occurred_at),
  KEY idx_behavior_channel_time (channel_id, occurred_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 7. 暂不实施项

以下内容后续增强，不作为当前阶段实现范围：

- MySQL 分区表
- 分库分表
- 千万级压测
- 历史数据冷热分层
- HTTPS
- bcrypt 密码加密
- 生产级安全基线
