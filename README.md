# 债权审查系统 (Debt Review System)

基于 LangGraph 的自动化破产债权审查解决方案。

## 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                        │
│                    deployed on Vercel                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                   deployed on Render                         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  API Routes │  │Task Runner  │  │  LangGraph Workflow │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │ Supabase │  │ DeepSeek │  │  Files   │
     │    DB    │  │   API    │  │ Storage  │
     └──────────┘  └──────────┘  └──────────┘
```

## 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **LangGraph** - 工作流编排
- **LangChain** - LLM 集成
- **DeepSeek** - LLM 提供商 (OpenAI 兼容接口)
- **Supabase** - PostgreSQL 数据库

### 前端
- **Vue 3** - 响应式 UI 框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式
- **Pinia** - 状态管理

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- npm 或 pnpm

### 后端启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API keys

# 启动服务
python api_server.py
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build
```

## 核心功能

### 1. 项目管理
- 创建破产项目
- 管理债权人信息
- 跟踪处理进度

### 2. 自动化审查
- 三阶段工作流：事实核查 → 债权分析 → 报告生成
- 异步后台处理
- 实时进度轮询

### 3. 利息计算
- 单利计算
- LPR 浮动利率
- 迟延履行利息
- 罚息/违约金

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/projects` | POST | 创建项目 |
| `/api/projects` | GET | 列出项目 |
| `/api/creditors` | POST | 添加债权人 |
| `/api/tasks` | POST | 提交审查任务 |
| `/api/tasks/{id}/status` | GET | 获取任务进度 |
| `/api/tools/calculate-interest` | POST | 利息计算 |

## 部署

### Render (后端)
1. Fork 本仓库
2. 在 Render 创建 Web Service
3. 连接 GitHub 仓库
4. 设置环境变量
5. 部署

### Vercel (前端)
1. 在 Vercel 导入项目
2. 设置 Root Directory 为 `frontend`
3. 配置环境变量 `VITE_API_URL`
4. 部署

## 环境变量

### 后端 (.env)
```
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_key
```

### 前端 (.env.production)
```
VITE_API_URL=https://your-backend.onrender.com
```

## 数据库设置

运行 `supabase/migrations/001_initial_schema.sql` 在 Supabase SQL Editor 中创建表结构。

## 开发说明

### 原型代码
原始 Claude Code 脚本已归档在 `backend/` 目录，包含：
- Agent 定义 (`.claude/agents/`)
- Skills 知识库 (`.claude/skills/`)
- 计算器脚本 (`universal_debt_calculator_cli.py`)
- 工作流控制器 (`债权处理工作流控制器.py`)

### 新架构
- `app/` - 重构后的应用代码
- `frontend/` - Vue 前端
- `supabase/` - 数据库迁移

## License

MIT
