-- Debt Review System - Initial Database Schema
-- Run this in Supabase SQL Editor

-- ============== Enable UUID Extension ==============
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============== Projects Table ==============
-- Represents a bankruptcy case/project
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

-- Index for faster lookups
CREATE INDEX idx_projects_name ON projects(name);
CREATE INDEX idx_projects_created_at ON projects(created_at DESC);

-- ============== Creditors Table ==============
-- Represents a creditor within a project
CREATE TABLE IF NOT EXISTS creditors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    batch_number INTEGER NOT NULL,
    creditor_number INTEGER NOT NULL,
    creditor_name VARCHAR(255) NOT NULL,

    -- Amounts
    declared_principal DECIMAL(18, 2),
    declared_interest DECIMAL(18, 2),
    declared_total DECIMAL(18, 2),
    confirmed_principal DECIMAL(18, 2),
    confirmed_interest DECIMAL(18, 2),
    confirmed_total DECIMAL(18, 2),

    -- Status tracking
    status VARCHAR(50) DEFAULT 'not_started',
    current_stage VARCHAR(50),
    current_round INTEGER DEFAULT 1,

    -- File paths
    materials_path TEXT,
    output_path TEXT,

    -- Metadata
    processing_config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint: one creditor per batch/number combo per project
    UNIQUE(project_id, batch_number, creditor_number)
);

-- Indexes
CREATE INDEX idx_creditors_project ON creditors(project_id);
CREATE INDEX idx_creditors_status ON creditors(status);
CREATE INDEX idx_creditors_batch ON creditors(project_id, batch_number);

-- ============== Tasks Table ==============
-- Represents an async processing task
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Task type and scope
    task_type VARCHAR(50) NOT NULL DEFAULT 'full_review',
    processing_mode VARCHAR(50) DEFAULT 'auto',

    -- Status tracking
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    current_stage VARCHAR(50) DEFAULT 'init',
    progress_percent INTEGER DEFAULT 0,

    -- Creditor tracking
    creditor_ids UUID[] NOT NULL DEFAULT '{}',
    creditors_total INTEGER DEFAULT 0,
    creditors_completed INTEGER DEFAULT 0,
    current_creditor_id UUID,
    current_creditor_name VARCHAR(255),

    -- Timing
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Error handling
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,

    -- Metadata
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);

-- ============== Task Logs Table ==============
-- Detailed logs for task execution (for debugging and audit)
CREATE TABLE IF NOT EXISTS task_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    creditor_id UUID REFERENCES creditors(id) ON DELETE SET NULL,

    -- Log details
    stage VARCHAR(50),
    level VARCHAR(20) DEFAULT 'info',  -- debug, info, warning, error
    message TEXT NOT NULL,
    details JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fetching logs by task
CREATE INDEX idx_task_logs_task ON task_logs(task_id, created_at DESC);

-- ============== Reports Table ==============
-- Generated reports for each creditor
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creditor_id UUID NOT NULL REFERENCES creditors(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

    -- Report info
    report_type VARCHAR(50) NOT NULL,  -- fact_check, analysis, final, calculation
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,

    -- Content (optional, for quick access)
    content_preview TEXT,

    -- Metadata
    round_number INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_reports_creditor ON reports(creditor_id);
CREATE INDEX idx_reports_type ON reports(report_type);

-- ============== Calculation Records Table ==============
-- Records of interest calculations (audit trail)
CREATE TABLE IF NOT EXISTS calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creditor_id UUID NOT NULL REFERENCES creditors(id) ON DELETE CASCADE,

    -- Calculation parameters
    calculation_type VARCHAR(50) NOT NULL,
    principal DECIMAL(18, 2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Rate info
    rate_type VARCHAR(50),  -- fixed, lpr_1y, lpr_5y
    rate_value DECIMAL(8, 4),
    multiplier DECIMAL(6, 4) DEFAULT 1.0,

    -- Results
    interest_amount DECIMAL(18, 2) NOT NULL,
    total_days INTEGER NOT NULL,

    -- Details (full calculation breakdown)
    calculation_details JSONB,
    excel_file_path TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_calculations_creditor ON calculations(creditor_id);

-- ============== Updated At Trigger ==============
-- Automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_creditors_updated_at
    BEFORE UPDATE ON creditors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============== Row Level Security (RLS) ==============
-- Enable RLS on all tables (for future auth integration)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE creditors ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculations ENABLE ROW LEVEL SECURITY;

-- For now, allow all operations (will add policies when auth is added)
CREATE POLICY "Allow all on projects" ON projects FOR ALL USING (true);
CREATE POLICY "Allow all on creditors" ON creditors FOR ALL USING (true);
CREATE POLICY "Allow all on tasks" ON tasks FOR ALL USING (true);
CREATE POLICY "Allow all on task_logs" ON task_logs FOR ALL USING (true);
CREATE POLICY "Allow all on reports" ON reports FOR ALL USING (true);
CREATE POLICY "Allow all on calculations" ON calculations FOR ALL USING (true);

-- ============== Comments ==============
COMMENT ON TABLE projects IS 'Bankruptcy projects/cases';
COMMENT ON TABLE creditors IS 'Creditors within a bankruptcy project';
COMMENT ON TABLE tasks IS 'Async processing tasks for debt review';
COMMENT ON TABLE task_logs IS 'Detailed execution logs for tasks';
COMMENT ON TABLE reports IS 'Generated report files';
COMMENT ON TABLE calculations IS 'Interest calculation records (audit trail)';
