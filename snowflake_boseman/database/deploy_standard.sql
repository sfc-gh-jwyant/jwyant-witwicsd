-- ============================================================================
-- WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?
-- Deployment Script using Standard Tables (for reader/trial accounts)
-- ============================================================================

-- Use the existing database
USE DATABASE DEMO_WITWISBM;
USE SCHEMA GAME;

-- ============================================================================
-- REFERENCE DATA TABLES (Standard Tables)
-- ============================================================================

CREATE OR REPLACE TABLE locations (
    location_id VARCHAR PRIMARY KEY,
    city VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    continent VARCHAR NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    description VARCHAR,
    image_url VARCHAR
);

CREATE OR REPLACE TABLE landmarks (
    landmark_id VARCHAR PRIMARY KEY,
    location_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    landmark_type VARCHAR,
    clue_facts ARRAY,
    image_url VARCHAR
);

CREATE OR REPLACE TABLE suspects (
    suspect_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    hair_color VARCHAR,
    eye_color VARCHAR,
    hobby VARCHAR,
    vehicle VARCHAR,
    favorite_food VARCHAR,
    distinguishing_feature VARCHAR,
    mugshot_url VARCHAR
);

CREATE OR REPLACE TABLE clue_images (
    image_id VARCHAR PRIMARY KEY,
    clue_type VARCHAR NOT NULL,
    image_url VARCHAR NOT NULL,
    description VARCHAR
);

-- ============================================================================
-- GAME STATE TABLES
-- ============================================================================

CREATE OR REPLACE TABLE players (
    player_id VARCHAR PRIMARY KEY,
    snowflake_user VARCHAR NOT NULL,
    email VARCHAR,
    rank VARCHAR DEFAULT 'Rookie',
    cases_solved INT DEFAULT 0,
    total_score INT DEFAULT 0,
    ai_prompt_count INT DEFAULT 0,
    ai_token_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE cases (
    case_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    suspect_id VARCHAR NOT NULL,
    stolen_item VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    location_path ARRAY,
    status VARCHAR DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE case_progress (
    case_id VARCHAR PRIMARY KEY,
    current_location_id VARCHAR NOT NULL,
    suspect_location_idx INT DEFAULT 0,
    hours_remaining INT NOT NULL,
    clues_gathered ARRAY,
    locations_visited ARRAY,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE high_scores (
    score_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    completion_time_hours INT NOT NULL,
    locations_visited INT NOT NULL,
    score INT NOT NULL,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- TELEMETRY TABLES
-- ============================================================================

CREATE OR REPLACE TABLE game_sessions (
    session_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    ended_at TIMESTAMP,
    duration_seconds INT,
    cases_started INT DEFAULT 0,
    cases_completed INT DEFAULT 0
);

CREATE OR REPLACE TABLE game_events (
    event_id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR,
    event_type VARCHAR NOT NULL,
    event_data VARIANT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE TABLE case_analytics (
    case_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    outcome VARCHAR NOT NULL,
    total_locations_in_path INT,
    locations_visited INT,
    correct_travels INT,
    wrong_travels INT,
    clues_gathered INT,
    time_budget_hours INT,
    time_used_hours INT,
    ai_prompts INT DEFAULT 0,
    ai_tokens INT DEFAULT 0,
    ai_model VARCHAR,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE OR REPLACE TABLE friction_points (
    friction_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR NOT NULL,
    location_id VARCHAR NOT NULL,
    friction_type VARCHAR NOT NULL,
    attempts_at_location INT,
    time_spent_hours INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- ANALYTICS VIEWS
-- ============================================================================

CREATE OR REPLACE VIEW v_daily_active_users AS
SELECT DATE(started_at) as play_date, COUNT(DISTINCT player_id) as dau
FROM game_sessions 
GROUP BY 1 
ORDER BY 1;

CREATE OR REPLACE VIEW v_win_rate_by_difficulty AS
SELECT 
    difficulty,
    CASE difficulty
        WHEN 1 THEN 'SELECT * FROM clues'
        WHEN 2 THEN 'WITH (NOLOCK)'
        WHEN 3 THEN 'Foreign Key Violation'
        WHEN 4 THEN 'Deadlock Victim'
        WHEN 5 THEN 'Little Bobby Tables'
    END as difficulty_name,
    COUNT(*) as total_cases,
    SUM(CASE WHEN outcome = 'won' THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN outcome = 'won' THEN 1 ELSE 0 END) / COUNT(*) * 100, 1) as win_rate_pct
FROM case_analytics 
GROUP BY difficulty 
ORDER BY difficulty;

CREATE OR REPLACE VIEW v_leaderboard AS
SELECT 
    p.snowflake_user,
    p.rank,
    p.cases_solved,
    p.total_score,
    MAX(hs.score) as best_score,
    MIN(hs.completion_time_hours) as fastest_time
FROM players p
LEFT JOIN high_scores hs ON p.player_id = hs.player_id
GROUP BY 1, 2, 3, 4
ORDER BY p.total_score DESC;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Tables created successfully in DEMO_WITWISBM.GAME!' as status;
