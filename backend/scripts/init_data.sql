-- Initial data seeding script
-- Insert default data for the AX Evaluation System

-- Insert default question categories
INSERT INTO question_categories (name, description, weight, display_order, is_active) VALUES
('기본소양', '지원자의 기본 소양과 인성 평가 항목', 20, 1, true),
('전문지식', '전공 분야의 지식과 이해도 평가 항목', 30, 2, true),
('문제해결력', '문제 해결 능력과 창의성 평가 항목', 25, 3, true),
('협업능력', '팀워크와 커뮤니케이션 능력 평가 항목', 15, 4, true),
('성장잠재력', '미래 성장 가능성과 동기 부여 평가 항목', 10, 5, true);

-- Insert sample questions
INSERT INTO questions (category_id, q_type, content, options, correct_answer, max_score, difficulty, target_specialties, display_order, is_active) VALUES
-- 기본소양 질문
(
    (SELECT id FROM question_categories WHERE name = '기본소양'),
    'SINGLE',
    '개인의 가장 중요한 가치관은 무엇이라고 생각하십니까?',
    '["정직함", "성실함", "창의성", "책임감", "협력"]',
    '{"value": "책임감"}',
    10,
    'MEDIUM',
    '["GENERAL"]',
    1,
    true
),
(
    (SELECT id FROM question_categories WHERE name = '기본소양'),
    'ESSAY',
    '지원자가 경험한 가장 어려운 상황과 그것을 어떻게 극복했는지 설명해 주십시오.',
    null,
    null,
    20,
    'HARD',
    '["GENERAL"]',
    2,
    true
),

-- 전문지식 질문
(
    (SELECT id FROM question_categories WHERE name = '전문지식'),
    'MULTIPLE',
    '다음 중 머신러닝의 주요 특징으로 올바른 것들을 모두 선택하십시오.',
    '["데이터 기반 학습", "규칙 기반 시스템", "패턴 인식", "명시적인 프로그래밍", "일반화 능력"]',
    '{"value": ["데이터 기반 학습", "패턴 인식", "일반화 능력"]}',
    15,
    'MEDIUM',
    '["ML", "DL"]',
    1,
    true
),
(
    (SELECT id FROM question_categories WHERE name = '전문지식'),
    'SHORT',
    'REST API의 기본적인 동작 원리를 간략히 설명해 주십시오.',
    null,
    null,
    10,
    'EASY',
    '["GENERAL"]',
    2,
    true
),

-- 문제해결력 질문
(
    (SELECT id FROM question_categories WHERE name = '문제해결력'),
    'ESSAY',
    '주어진 시간과 자원이 제한된 상황에서 어떻게 효과적으로 문제를 해결하려고 하는지 구체적인 사례를 들어 설명해 주십시오.',
    null,
    null,
    25,
    'HARD',
    '["GENERAL"]',
    1,
    true
),

-- 협업능력 질문
(
    (SELECT id FROM question_categories WHERE name = '협업능력'),
    'ESSAY',
    '팀 내에서 의견이 엇갈렸을 때 어떻게 대화하고 합의를 도출하는지 경험을 바탕으로 설명해 주십시오.',
    null,
    null,
    20,
    'MEDIUM',
    '["GENERAL"]',
    1,
    true
),

-- 성장잠재력 질문
(
    (SELECT id FROM question_categories WHERE name = '성장잠재력'),
    'ESSAY',
    '미래 5년간 어떻게 성장하고 싶은지, 그 구체적인 계획을 포함하여 설명해 주십시오.',
    null,
    null,
    15,
    'MEDIUM',
    '["GENERAL"]',
    1,
    true
);

-- Create admin user (password: admin1234)
INSERT INTO users (email, password_hash, name, role, status) VALUES
(
    'admin@example.com',
    '$2b$12$Xd6FF9dvVeznnEFMt5Cs0Ox2.8SaZFI9TqB3zTkTmwnvYmBr1x8tW',  -- hash for 'admin1234'
    '관리자',
    'ADMIN',
    'ACTIVE'
);

-- Create sample expert account (password: expert1234)
INSERT INTO users (email, password_hash, name, role, status) VALUES
(
    'expert@example.com',
    '$2b$12$kFu1v029k58cjFAbWTtbvOu177PyZFtZzEW.vlpRtb54/cmheTKJa',  -- hash for 'expert1234'
    '전문가',
    'EVALUATOR',
    'ACTIVE'
);

-- Link expert to user record
INSERT INTO experts (user_id, degree_type, degree_field, career_years, position, org_name, org_type, qualification_status) VALUES
(
    (SELECT id FROM users WHERE email = 'expert@example.com'),
    'PHD',
    '컴퓨터 과학',
    10,
    '수석 연구원',
    'AI 연구소',
    'RESEARCH',
    'QUALIFIED'
);

-- Create sample applicant users
INSERT INTO users (email, password_hash, name, role, status) VALUES
(
    'applicant1@example.com',
    '$2b$12$GuiA24XSq00eN64evz0PDONTIDhsCUowDJHXH.Z0Yo6.aTR8ZX6JC',  -- hash for 'applicant1234'
    '지원자1',
    'APPLICANT',
    'ACTIVE'
),
(
    'applicant2@example.com',
    '$2b$12$GuiA24XSq00eN64evz0PDONTIDhsCUowDJHXH.Z0Yo6.aTR8ZX6JC',  -- hash for 'applicant1234'
    '지원자2',
    'APPLICANT',
    'ACTIVE'
);

-- Grant all privileges to admin user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Refresh materialized views if any
REFRESH MATERIALIZED VIEW IF EXISTS;