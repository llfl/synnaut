# Synnaut

> 基于 OpenClaw 的任务型多 Agent 编排系统。  
> 设计模型：有界递归、显式任务卡、文件化控制平面。

## Synnaut 是什么

Synnaut 将 OpenClaw 组织成一个适合长任务、多任务和可恢复执行的多 Agent 运行时。

它不把全部上下文压在单一聊天会话里，而是拆成四层：

- 一个常驻控制 Agent，也就是大副
- 面向任务的领航员 Agent
- 短生命周期的水手 Agent
- 文件化的任务状态、交接快照与复盘记录

这样做的结果是：系统可以并行推进多个任务，可以安全切换焦点，也可以在 session 失效后从文件状态中恢复任务，而不是依赖对话记忆。

## 运行根目录约定

Synnaut 只有一个规范运行根目录：也就是包含 `openclaw.json` 的 OpenClaw 配置目录。

- `fleet/` 位于这个 OpenClaw 根目录下
- 所有 `workspace-*` 目录也位于这个 OpenClaw 根目录下
- 像 `fleet/bin/taskbus.py` 这样的路径，一律相对于 OpenClaw 根目录解释
- 绝不能把 `fleet/` 理解成 `workspace-main/` 或其他 agent workspace 内部的局部目录

规范布局是：

```text
<OPENCLAW_HOME>/
  openclaw.json
  fleet/
  workspace-main/
  workspace-pilot-*/
  workspace-worker-*/
```

如果 `<OPENCLAW_HOME>` 下缺少 `fleet/bin/taskbus.py` 或 `fleet/registry/`，就说明舰队尚未正确安装或初始化完成，此时大副不得静默进入执行阶段。

## 为什么这样设计

OpenClaw 原生擅长 Agent 路由与 sub-agent 执行，但仅靠“能 spawn agent”还不足以支撑稳定编排。Synnaut 补上的是控制层：

- 执行前先注册任务
- 用确定性的 Agent 拓扑约束递归
- 将状态持久化到聊天之外
- 为任务切换提供可读的恢复文件
- 为完成后的归档和复盘保留结构化记录

这让系统在跨 session、跨任务运行时仍然可审计、可恢复、可追踪。

## 架构

```text
Human Operator (船长)
    |
    v
main (大副)
    |
    +-- fleet/bin/taskbus.py
    |      create / list / show / switch / update / archive
    |
    +-- pilot-general   (通用领航员 / 通用编排)
    +-- pilot-research  (研究领航员 / 研究编排)
    +-- pilot-build     (构建领航员 / 构建编排)
             |
             +-- worker-drive  (轮机手 / 实现与交付)
             +-- worker-guard  (机械师 / 测试与校验)
             +-- worker-sense  (瞭望手 / 检索与分析)
```

### Agent 分层

| 层级 | Agent ID | 展示角色 | 责任 |
|------|----------|----------|------|
| 控制平面 | `main` | 大副 | 接收用户请求、创建任务、选择领航员、跟踪状态、汇总输出 |
| 任务编排 | `pilot-general` | 通用领航员 | 处理混合型或边界不清的任务拆解 |
| 任务编排 | `pilot-research` | 研究领航员 | 处理研究、比较、资料收集、分析类任务 |
| 任务编排 | `pilot-build` | 构建领航员 | 处理实现、修改、构建、验证闭环类任务 |
| 执行层 | `worker-drive` | 轮机手 | 负责实现、编辑、构建、交付具体结果 |
| 执行层 | `worker-guard` | 机械师 | 负责审查、测试、验证、约束检查 |
| 执行层 | `worker-sense` | 瞭望手 | 负责搜索、抓取、阅读、分析信息 |

### 有界递归

Synnaut 使用显式的两跳拓扑：

- `main` 只能拉起领航员
- 领航员只能拉起水手
- 水手不能继续向下拉起 Agent

这条约束通过 [`openclaw.json`](openclaw.json) 中的 `allowAgents` 实现。

## 执行链路

每个任务都走同一条控制链路。

### 1. 任务入口

用户把请求发给 `main`。系统先判断这个请求属于哪一类：

- 新任务
- 对已有任务的追问
- 切换任务
- 完成任务或归档任务

### 2. 任务注册

在任何领航员被拉起之前，`main` 会先通过 [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py) 把任务写入文件化控制平面。

这一步会创建：

- `fleet/registry/tasks.json` 中的任务索引
- `fleet/registry/active.md` 中的活动任务摘要
- `fleet/tasks/<TASK_ID>/` 下的一整组任务文件
- 完整的任务卡、上下文、计划、决策、交接、复盘与状态文件

这意味着任务卡是真实的单一真相源，而不是某一段对话的残留上下文。

对于新任务，`taskbus.py create` 是唯一合法入口。只有它成功返回之后，才允许拉起领航员。

### 3. 领航员分派

`main` 根据任务类型选择一个领航员：

- 实现型任务走 `pilot-build`
- 研究型任务走 `pilot-research`
- 混合型或不明确任务走 `pilot-general`

领航员接收到的是显式任务上下文，而不是隐式继承的聊天记忆。

### 4. 水手执行

如果领航员需要并行子任务，它可以按需拉起水手：

- `worker-drive`，也就是轮机手，负责实现
- `worker-guard`，也就是机械师，负责审查和验证
- `worker-sense`，也就是瞭望手，负责检索和分析

水手是叶子节点，只返回聚焦结果，不拥有任务主状态。

### 5. 结果汇总

领航员将水手的结果汇总成任务级结论，再返回给 `main`。  
任务主状态仍然只由 `main` 更新。

### 6. 切换与恢复

如果用户切换到另一个任务，Synnaut 可以：

- 继续使用现存的 live session
- 或从 `STATUS.json` 与 `HANDOFF.md` 恢复任务上下文

这样多任务运行就不需要把单一聊天线程当成唯一记忆体。

### 7. 复盘与归档

任务完成后，系统会记录 review 信号、保留最终交接快照，并将任务归档，以便后续审计和复用。

## 文件化控制平面

Synnaut 将编排状态保存在磁盘，而不只保存在 prompt 中。

### 核心文件

| 路径 | 用途 |
|------|------|
| [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py) | 任务状态变更与任务脚手架生成 |
| [`fleet/bin/dashboard.py`](fleet/bin/dashboard.py) | 只读的终端状态面板 |
| [`fleet/registry/tasks.json`](fleet/registry/tasks.json) | 全局机器可读任务索引 |
| [`fleet/registry/active.md`](fleet/registry/active.md) | 面向人的活动任务摘要 |
| `fleet/tasks/<TASK_ID>/TASK.md` | 显式任务卡 |
| `fleet/tasks/<TASK_ID>/STATUS.json` | 当前机器可读任务状态 |
| `fleet/tasks/<TASK_ID>/HANDOFF.md` | 用于切换和恢复的交接快照 |
| `fleet/tasks/<TASK_ID>/REVIEW.md` | 结果复盘与经验事件记录 |

### 状态模型

```text
NEW -> RUNNING -> WAITING_USER / BLOCKED / SYNTHESIZING -> DONE / FAILED -> ARCHIVED
```

只有 `main` 能推进任务主状态。领航员可以建议状态变化，但不直接控制全局注册表。

## 任务切换模型

Synnaut 支持两种切换方式：

- 线程绑定切换：当运行通道支持持久绑定 session 时
- 软切换：由 `main` 基于任务记录和恢复文件重新路由后续工作

这让设计可以适配不同通道、不同 session 模型，而不是绑定在单一运行环境里。

## 推荐运行边界

当前仓库采用比较保守的运行策略：

- 最多 3 个活动领航员，作为编排策略
- 每个领航员最多 2 个水手，作为编排策略
- 水手超时为 900 秒，来自 OpenClaw sub-agent 默认配置
- Session 归档窗口为 120 分钟，来自 OpenClaw sub-agent 默认配置

前两项属于 prompt 和控制逻辑约束，后两项属于 [`openclaw.json`](openclaw.json) 中的运行时默认值。

## 先落账后执行规则

大副的运行节奏必须是：

```text
Receive -> Write -> Act -> Write -> Report
```

对于每一个新任务，第一段 `Write` 必须先在 `<OPENCLAW_HOME>/fleet` 下落完这三类文件：

- `fleet/registry/tasks.json`
- `fleet/tasks/T-xxx/TASK.md`
- `fleet/registry/active.md`

如果这些文件还没有写出来，那么这个任务就不能被视为已经正式进入执行。

## Study Cases

### Case 1：带 Review Gate 的功能实现

请求：  
“实现一套新的认证流程。”

链路：

1. `main` 创建任务卡并分配 `pilot-build`
2. `pilot-build` 拉起 `worker-drive`，也就是轮机手，完成功能实现
3. `pilot-build` 拉起 `worker-guard`，也就是机械师，做审查与验证
4. 领航员汇总结果并返回结构化报告
5. `main` 更新任务状态并向用户汇报

意义：  
实现与验证由不同 Agent 承担，避免“谁写代码谁直接放行”的耦合。

### Case 2：供应商或 API 方案调研

请求：  
“调研三个 API 提供方，并给出推荐。”

链路：

1. `main` 创建任务并分配 `pilot-research`
2. `pilot-research` 拉起 `worker-sense`，也就是瞭望手，收集、比较、分析信息
3. 如有需要，再由 `worker-guard`，也就是机械师，做交叉验证
4. 领航员产出带权衡的结构化建议
5. `main` 记录结论和下一步

意义：  
资料收集、事实验证、最终建议拆成不同阶段，减少拍脑袋式研究输出。

### Case 3：多任务并行与安全切换

请求：

- “启动 release 分支的构建任务。”
- “另外调查一下 sandbox 启动失败的原因。”
- “切回 release 任务。”

链路：

1. `main` 为两个请求分别创建任务记录
2. 每个任务拥有自己的领航员 session 和状态文件
3. 切换焦点时不会覆盖另一个任务的上下文
4. 如果某个领航员 session 失效，`main` 可以从 `HANDOFF.md` 与 `STATUS.json` 恢复

意义：  
系统把多任务视为一等公民，而不是把所有事情硬塞进一条线性对话。

## 运行说明

Sandbox 在安装时默认关闭，需要显式开启：

```bash
python install.py --sandbox
```

这样设计是有意的。Sandbox 依赖可用的容器运行时以及可用的 `openclaw-sandbox` 镜像；如果默认开启，会导致一部分环境安装后直接失败。

## 仓库入口

- [`README.md`](README.md)：英文版对外设计说明
- [`openclaw.json`](openclaw.json)：OpenClaw Agent 拓扑和工具权限
- [`install.py`](install.py)：将 Synnaut 合并进现有 OpenClaw 环境的安装脚本
- [`workspace-main/AGENTS.md`](workspace-main/AGENTS.md)：`main` 的控制平面行为定义
- [`fleet/bin/taskbus.py`](fleet/bin/taskbus.py)：任务状态机入口
- [`fleet/bin/dashboard.py`](fleet/bin/dashboard.py)：面向操作者的终端面板

## 设计原则

- 显式状态比会话记忆更可靠。
- 编排职责和执行职责应该分离。
- 并行应该有边界，而不是默认无限递归。
- 任务切换应该依赖文件恢复，而不是依赖“希望上下文还在”。
- 复盘产物和执行产物同样重要。
