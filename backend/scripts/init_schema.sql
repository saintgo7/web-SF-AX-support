-- Initial migration script for AX Evaluation System
-- Create all required tables

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS answers CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS question_categories CASCADE;
DROP TABLE IF EXISTS experts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL DEFAULT 'APPLICANT' CHECK (role IN ('APPLICANT', 'EVALUATOR', 'OPERATOR', 'ADMIN')),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

-- Create experts table
CREATE TABLE experts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    degree_type VARCHAR(20) CHECK (degree_type IN ('PHD', 'MASTER', 'BACHELOR')),
    degree_field VARCHAR(100),
    career_years INTEGER,
    position VARCHAR(100),
    org_name VARCHAR(200),
    org_type VARCHAR(20) CHECK (org_type IN ('UNIVERSITY', 'COMPANY', 'RESEARCH', 'OTHER')),
    specialties JSONB,
    certifications JSONB,
    qualification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (qualification_status IN ('PENDING', 'QUALIFIED', 'DISQUALIFIED')),
    qualification_note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create question_categories table
CREATE TABLE question_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    weight INTEGER NOT NULL DEFAULT 10,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL,
    q_type VARCHAR(20) NOT NULL CHECK (q_type IN ('SINGLE', 'MULTIPLE', 'SHORT', 'ESSAY', 'FILE')),
    content TEXT NOT NULL,
    options JSONB,
    correct_answer JSONB,
    scoring_rubric JSONB,
    max_score INTEGER NOT NULL,
    difficulty VARCHAR(20) NOT NULL DEFAULT 'MEDIUM' CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')),
    target_specialties JSONB,
    explanation TEXT,
    display_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (category_id) REFERENCES question_categories(id) ON DELETE RESTRICT
);

-- Create answers table
CREATE TABLE answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    expert_id UUID NOT NULL,
    question_id UUID NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    response_data JSONB NOT NULL,
    score FLOAT,
    max_score INTEGER NOT NULL,
    is_correct BOOLEAN,
    grader_id UUID,
    grader_comment TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'SUBMITTED', 'GRADED', 'REVIEWED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    FOREIGN KEY (expert_id) REFERENCES experts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (grader_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX idx_experts_user_id ON experts(user_id);
CREATE INDEX idx_questions_category_id ON questions(category_id);
CREATE INDEX idx_questions_q_type ON questions(q_type);
CREATE INDEX idx_answers_expert_id ON answers(expert_id);
CREATE INDEX idx_answers_question_id ON answers(question_id);
CREATE INDEX idx_answers_status ON answers(status);

-- Create sequence for version management
CREATE SEQUENCE answer_version_seq
START 1
INCREMENT 1;

-- Add constraint to ensure max_score is positive
ALTER TABLE questions ADD CONSTRAINT chk_questions_max_score CHECK (max_score > 0);
ALTER TABLE answers ADD CONSTRAINT chk_answers_max_score CHECK (max_score > 0);

-- Add constraint to ensure score is within valid range
ALTER TABLE answers ADD CONSTRAINT chk_answers_score CHECK (
    score IS NULL OR (score >= 0 AND score <= max_score)
);