-- ============================================
-- 暖洋洋 (Nuanyangyang) 数据库Schema
-- 多租户架构设计
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS nuanyangyang
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE nuanyangyang;

-- ============================================
-- 1. 租户管理表
-- ============================================

-- 组织/机构表（多租户的核心）
CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,  -- 组织代码，用于标识
    type VARCHAR(50) NOT NULL,  -- 'nursing_home', 'hospital', 'community', 'family'
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'suspended', 'inactive'
    settings JSONB,  -- 组织级别配置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP  -- 软删除
);

CREATE INDEX idx_organizations_code ON organizations(code);
CREATE INDEX idx_organizations_status ON organizations(status);

-- 组织管理员表
CREATE TABLE organization_admins (
    admin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',  -- 'super_admin', 'admin', 'manager'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

CREATE INDEX idx_org_admins_org ON organization_admins(organization_id);
CREATE INDEX idx_org_admins_email ON organization_admins(email);

-- ============================================
-- 2. 用户表（老年人）
-- ============================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),  -- 租户隔离
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    preferred_language VARCHAR(5) DEFAULT 'zh',
    dialect VARCHAR(20),
    voice_gender VARCHAR(10) DEFAULT 'female',
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'inactive', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP  -- 软删除
);

-- 租户隔离索引（关键！）
CREATE INDEX idx_users_org ON users(organization_id, user_id);
CREATE INDEX idx_users_status ON users(organization_id, status);

-- ============================================
-- 3. 用户档案表
-- ============================================

CREATE TABLE user_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),  -- 冗余，加速查询
    family_members JSONB,  -- {"children": [...], "spouse": {...}}
    interests JSONB,  -- ["园艺", "下棋", "听戏"]
    medical_history JSONB,  -- {"conditions": [...], "allergies": [...]}
    medications JSONB,  -- [{"name": "...", "dosage": "..."}]
    emergency_contacts JSONB,  -- [{"name": "...", "phone": "..."}]
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profiles_user ON user_profiles(organization_id, user_id);

-- ============================================
-- 4. 对话记录表
-- ============================================

CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),  -- 租户隔离
    language VARCHAR(5) NOT NULL,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    emotion_score FLOAT,  -- 情绪分数 0-100
    sentiment VARCHAR(20),  -- 'positive', 'neutral', 'negative'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 租户隔离 + 时间范围查询优化
CREATE INDEX idx_conversations_org_user ON conversations(organization_id, user_id, created_at DESC);
CREATE INDEX idx_conversations_created ON conversations(created_at);

-- 分区表（按月分区，提升查询性能）
-- PostgreSQL 10+ 支持
-- CREATE TABLE conversations_2024_01 PARTITION OF conversations
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ============================================
-- 5. 健康记录表
-- ============================================

CREATE TABLE health_records (
    record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),  -- 租户隔离
    record_type VARCHAR(50) NOT NULL,  -- 'sleep', 'pain', 'appetite', 'mood', 'activity'
    value JSONB NOT NULL,  -- {"quality": 3, "duration": 7, "notes": "..."}
    severity VARCHAR(20),  -- 'mild', 'moderate', 'severe'
    extracted_from_conversation_id UUID REFERENCES conversations(conversation_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_org_user ON health_records(organization_id, user_id, created_at DESC);
CREATE INDEX idx_health_type ON health_records(organization_id, record_type, created_at DESC);

-- ============================================
-- 6. 健康预警表
-- ============================================

CREATE TABLE health_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),  -- 租户隔离
    alert_level VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'critical'
    alert_type VARCHAR(50) NOT NULL,  -- 'symptom', 'behavior', 'emotion'
    title VARCHAR(200) NOT NULL,
    description TEXT,
    related_data JSONB,  -- 相关的健康数据
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES organization_admins(admin_id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_org_status ON health_alerts(organization_id, is_resolved, created_at DESC);
CREATE INDEX idx_alerts_level ON health_alerts(organization_id, alert_level, created_at DESC);

-- ============================================
-- 7. 审计日志表（合规性）
-- ============================================

CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    user_id UUID REFERENCES users(user_id),
    admin_id UUID REFERENCES organization_admins(admin_id),
    action VARCHAR(100) NOT NULL,  -- 'login', 'view_profile', 'export_data'
    resource_type VARCHAR(50),  -- 'user', 'conversation', 'health_record'
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_org ON audit_logs(organization_id, created_at DESC);
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at DESC);

-- ============================================
-- 8. 向量数据库元数据表（Qdrant同步）
-- ============================================

CREATE TABLE vector_embeddings_meta (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(organization_id),
    user_id UUID NOT NULL REFERENCES users(user_id),
    conversation_id UUID REFERENCES conversations(conversation_id),
    qdrant_point_id UUID NOT NULL,  -- Qdrant中的point ID
    collection_name VARCHAR(100) NOT NULL,  -- 'conversations_zh', 'conversations_nl'
    embedding_model VARCHAR(50) NOT NULL,  -- 'bge-m3', 'openai'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vector_meta_org ON vector_embeddings_meta(organization_id, user_id);

-- ============================================
-- 9. 系统配置表
-- ============================================

CREATE TABLE system_settings (
    setting_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(organization_id),  -- NULL表示全局设置
    key VARCHAR(100) NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(organization_id, key)
);

-- ============================================
-- 10. Row Level Security (RLS) 策略
-- PostgreSQL 9.5+ 支持
-- ============================================

-- 启用RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE health_alerts ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能访问自己组织的数据
CREATE POLICY org_isolation_policy ON users
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY org_isolation_policy ON conversations
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY org_isolation_policy ON health_records
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

CREATE POLICY org_isolation_policy ON health_alerts
    USING (organization_id = current_setting('app.current_organization_id')::UUID);

-- ============================================
-- 11. 视图（便捷查询）
-- ============================================

-- 用户健康概览视图
CREATE VIEW user_health_overview AS
SELECT 
    u.user_id,
    u.organization_id,
    u.name,
    u.age,
    COUNT(DISTINCT c.conversation_id) as total_conversations,
    COUNT(DISTINCT hr.record_id) as total_health_records,
    COUNT(DISTINCT CASE WHEN ha.is_resolved = FALSE THEN ha.alert_id END) as active_alerts,
    MAX(c.created_at) as last_conversation_at,
    MAX(hr.created_at) as last_health_record_at
FROM users u
LEFT JOIN conversations c ON u.user_id = c.user_id
LEFT JOIN health_records hr ON u.user_id = hr.user_id
LEFT JOIN health_alerts ha ON u.user_id = ha.user_id
GROUP BY u.user_id, u.organization_id, u.name, u.age;

-- ============================================
-- 12. 函数（业务逻辑）
-- ============================================

-- 设置当前组织上下文（用于RLS）
CREATE OR REPLACE FUNCTION set_current_organization(org_id UUID)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_organization_id', org_id::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql;

-- 软删除函数
CREATE OR REPLACE FUNCTION soft_delete_user(p_user_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE users 
    SET deleted_at = CURRENT_TIMESTAMP, status = 'archived'
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 13. 触发器（自动化）
-- ============================================

-- 更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 14. 示例数据
-- ============================================

-- 插入示例组织
INSERT INTO organizations (name, code, type, settings) VALUES
('阳光养老院', 'SUNSHINE_NH', 'nursing_home', '{"max_users": 100, "features": ["chat", "health_monitor"]}'),
('爱心社区', 'LOVE_COMMUNITY', 'community', '{"max_users": 500, "features": ["chat"]}');

-- 插入示例管理员
INSERT INTO organization_admins (organization_id, email, name, password_hash, role)
SELECT organization_id, 'admin@sunshine.com', '张管理员', 'hashed_password', 'admin'
FROM organizations WHERE code = 'SUNSHINE_NH';

-- 插入示例用户
INSERT INTO users (organization_id, name, age, gender, preferred_language)
SELECT organization_id, '王奶奶', 75, 'female', 'zh'
FROM organizations WHERE code = 'SUNSHINE_NH';

-- ============================================
-- 15. 性能优化建议
-- ============================================

-- 定期清理旧数据（保留策略）
-- DELETE FROM conversations WHERE created_at < NOW() - INTERVAL '2 years';

-- 定期VACUUM和ANALYZE
-- VACUUM ANALYZE conversations;
-- VACUUM ANALYZE health_records;

-- 监控慢查询
-- SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

-- ============================================
-- 16. 备份与恢复
-- ============================================

-- 备份单个组织的数据
-- pg_dump -h localhost -U postgres -d nuanyangyang \
--   --table=users --table=conversations --table=health_records \
--   --where="organization_id='xxx-xxx-xxx'" > org_backup.sql

-- 恢复
-- psql -h localhost -U postgres -d nuanyangyang < org_backup.sql
