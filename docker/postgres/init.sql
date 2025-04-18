-- Initialize HotLabel database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Publishers Table
CREATE TABLE IF NOT EXISTS publishers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id VARCHAR(20) NOT NULL UNIQUE,
    api_key VARCHAR(50) NOT NULL UNIQUE,
    company_name VARCHAR(100) NOT NULL,
    website_url VARCHAR(255) NOT NULL,
    contact_email VARCHAR(100) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    estimated_monthly_traffic INTEGER NOT NULL,
    integration_platform VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Publisher Configuration Table
CREATE TABLE IF NOT EXISTS publisher_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id UUID NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
    configuration_version INTEGER NOT NULL DEFAULT 1,
    appearance JSONB,
    behavior JSONB,
    task_preferences JSONB,
    rewards JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(36) NOT NULL UNIQUE,
    task_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    options JSONB,
    complexity_level INTEGER DEFAULT 1,
    is_golden_set BOOLEAN DEFAULT FALSE,
    expected_answer VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(36) NOT NULL UNIQUE,
    publisher_id UUID NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
    client_info JSONB,
    consent JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    expertise_level VARCHAR(20) DEFAULT 'beginner',
    task_preferences JSONB,
    language_proficiency JSONB,
    expertise_areas JSONB,
    max_complexity INTEGER DEFAULT 2,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task Assignments Table
CREATE TABLE IF NOT EXISTS task_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_completed BOOLEAN DEFAULT FALSE,
    UNIQUE (task_id, session_id)
);

-- Task Submissions Table
CREATE TABLE IF NOT EXISTS task_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    response JSONB NOT NULL,
    time_spent_ms INTEGER NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quality Validations Table
CREATE TABLE IF NOT EXISTS quality_validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    validation_id VARCHAR(36) NOT NULL UNIQUE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    quality_score NUMERIC(3,2) NOT NULL,
    validation_method VARCHAR(20) NOT NULL,
    issues_detected JSONB,
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Quality Reports Table
CREATE TABLE IF NOT EXISTS quality_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id VARCHAR(36) NOT NULL UNIQUE,
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL,
    details TEXT,
    status VARCHAR(20) DEFAULT 'received',
    reported_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Webhooks Table
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id VARCHAR(36) NOT NULL UNIQUE,
    publisher_id UUID NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
    endpoint_url VARCHAR(255) NOT NULL,
    secret_key VARCHAR(100) NOT NULL,
    events JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Webhook Events Table
CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_attempt_at TIMESTAMP WITH TIME ZONE
);

-- Statistics Table
CREATE TABLE IF NOT EXISTS publisher_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    publisher_id UUID NOT NULL REFERENCES publishers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    task_displays INTEGER DEFAULT 0,
    task_completions INTEGER DEFAULT 0,
    revenue NUMERIC(10,2) DEFAULT 0.0,
    unique_users INTEGER DEFAULT 0,
    returning_users INTEGER DEFAULT 0,
    UNIQUE (publisher_id, date)
);

-- Create indexes for performance
CREATE INDEX idx_task_assignments_session_id ON task_assignments(session_id);
CREATE INDEX idx_task_submissions_session_id ON task_submissions(session_id);
CREATE INDEX idx_task_submissions_task_id ON task_submissions(task_id);
CREATE INDEX idx_quality_validations_task_id ON quality_validations(task_id);
CREATE INDEX idx_publisher_statistics_date ON publisher_statistics(date);