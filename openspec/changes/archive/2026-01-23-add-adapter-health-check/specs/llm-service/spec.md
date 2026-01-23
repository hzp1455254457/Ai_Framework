# llm-service Specification Delta

## MODIFIED Requirements

### Requirement: Adapter Health Check
系统 SHALL 提供适配器健康检查功能，检测适配器可用性并支持自动故障转移。

**Rationale**: 在生产环境中，需要监控适配器状态，确保服务可用性，并在适配器故障时自动切换到可用适配器。

#### Scenario: Check Adapter Health Status
**Given** 系统已配置多个 LLM 适配器
**When** 系统执行适配器健康检查
**Then** 系统应：
1. 对每个适配器执行健康检查（轻量级 API 调用）
2. 返回适配器的健康状态（HEALTHY、UNHEALTHY、UNKNOWN）
3. 记录健康检查结果和时间戳
4. 在健康检查失败时记录错误信息

#### Scenario: Automatic Failover on Adapter Failure
**Given** 系统配置了多个 LLM 适配器，其中一个适配器不可用
**When** 用户发送 LLM 请求
**Then** 系统应：
1. 检测到主适配器不可用
2. 自动切换到可用的备用适配器
3. 使用备用适配器处理请求
4. 记录故障转移事件

#### Scenario: Query Adapter Health via API
**Given** 健康检查 API 已部署
**When** 用户发送 GET 请求到 `/api/health/adapters`
**Then** 系统应：
1. 执行所有适配器的健康检查
2. 返回所有适配器的健康状态
3. 返回健康检查结果和时间戳
4. 支持按服务类型过滤（LLM、Vision 等）

#### Scenario: Handle Health Check Timeout
**Given** 适配器健康检查已配置超时时间
**When** 健康检查请求超时
**Then** 系统应：
1. 检测到超时
2. 将适配器标记为 UNHEALTHY
3. 记录超时错误
4. 不阻塞其他适配器的健康检查

#### Scenario: Configure Health Check Interval
**Given** 用户需要配置健康检查间隔
**When** 用户在配置文件中设置健康检查间隔
**Then** 系统应：
1. 读取并应用健康检查间隔配置
2. 按配置的间隔执行健康检查
3. 支持不同环境的不同配置（开发/生产）
