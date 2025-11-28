-- =====================================================
-- Supabase 完整数据库初始化脚本
-- 项目: Debt Review System
-- 如果表已存在会跳过，可以安全重复执行
-- =====================================================

-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============== 1. Projects 表 ==============
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    debtor_name VARCHAR(255) NOT NULL,
    bankruptcy_date DATE NOT NULL,
    interest_stop_date DATE NOT NULL,
    description TEXT,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);

-- ============== 2. Creditors 表 ==============
CREATE TABLE IF NOT EXISTS creditors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    batch_number INTEGER NOT NULL,
    creditor_number INTEGER NOT NULL,
    creditor_name VARCHAR(255) NOT NULL,
    declared_principal DECIMAL(18, 2),
    declared_interest DECIMAL(18, 2),
    declared_total DECIMAL(18, 2),
    confirmed_principal DECIMAL(18, 2),
    confirmed_interest DECIMAL(18, 2),
    confirmed_total DECIMAL(18, 2),
    status VARCHAR(50) DEFAULT 'not_started',
    current_stage VARCHAR(50),
    current_round INTEGER DEFAULT 1,
    materials_path TEXT,
    output_path TEXT,
    processing_config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(project_id, batch_number, creditor_number)
);

CREATE INDEX IF NOT EXISTS idx_creditors_project ON creditors(project_id);
CREATE INDEX IF NOT EXISTS idx_creditors_status ON creditors(status);
CREATE INDEX IF NOT EXISTS idx_creditors_batch ON creditors(project_id, batch_number);

-- ============== 3. Tasks 表 ==============
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    task_type VARCHAR(50) NOT NULL DEFAULT 'full_review',
    processing_mode VARCHAR(50) DEFAULT 'auto',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_stage VARCHAR(50) DEFAULT 'init',
    progress_percent INTEGER DEFAULT 0,
    creditor_ids UUID[] NOT NULL DEFAULT '{}',
    creditors_total INTEGER DEFAULT 0,
    creditors_completed INTEGER DEFAULT 0,
    current_creditor_id UUID,
    current_creditor_name VARCHAR(255),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- ============== 4. Task Logs 表 ==============
CREATE TABLE IF NOT EXISTS task_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    creditor_id UUID REFERENCES creditors(id) ON DELETE SET NULL,
    stage VARCHAR(50),
    level VARCHAR(20) DEFAULT 'info',
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_task_logs_task ON task_logs(task_id, created_at DESC);

-- ============== 5. Reports 表 ==============
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creditor_id UUID NOT NULL REFERENCES creditors(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    report_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    content_preview TEXT,
    content TEXT,
    round_number INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_creditor ON reports(creditor_id);
CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type);

-- ============== 6. Calculations 表 ==============
CREATE TABLE IF NOT EXISTS calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creditor_id UUID NOT NULL REFERENCES creditors(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    calculation_type VARCHAR(50) NOT NULL,
    principal DECIMAL(18, 2) NOT NULL,
    interest DECIMAL(18, 2) NOT NULL,
    total DECIMAL(18, 2) NOT NULL,
    start_date DATE,
    end_date DATE,
    rate_type VARCHAR(50),
    rate_value DECIMAL(8, 4),
    multiplier DECIMAL(6, 4) DEFAULT 1.0,
    total_days INTEGER,
    parameters JSONB,
    result JSONB,
    calculation_details JSONB,
    excel_file_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_calculations_creditor ON calculations(creditor_id);
CREATE INDEX IF NOT EXISTS idx_calculations_task ON calculations(task_id);

-- ============== 7. 更新时间触发器 ==============
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 创建触发器（如果不存在则创建）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_projects_updated_at') THEN
        CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_creditors_updated_at') THEN
        CREATE TRIGGER update_creditors_updated_at BEFORE UPDATE ON creditors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_tasks_updated_at') THEN
        CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END $$;

-- ============== 8. 启用 RLS ==============
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE creditors ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculations ENABLE ROW LEVEL SECURITY;

-- 创建策略（允许所有操作）
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all on projects') THEN
        CREATE POLICY "Allow all on projects" ON projects FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all on creditors') THEN
        CREATE POLICY "Allow all on creditors" ON creditors FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all on tasks') THEN
        CREATE POLICY "Allow all on tasks" ON tasks FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all on task_logs') THEN
        CREATE POLICY "Allow all on task_logs" ON task_logs FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all on reports') THEN
        CREATE POLICY "Allow all on reports" ON reports FOR ALL USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Allow all on calculations') THEN
        CREATE POLICY "Allow all on calculations" ON calculations FOR ALL USING (true);
    END IF;
END $$;

-- =====================================================
-- 执行完成！
-- 如果看到 "Success. No rows returned" 表示执行成功
-- =====================================================
