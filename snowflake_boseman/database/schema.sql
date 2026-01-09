-- ============================================================================
-- WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?
-- Database Schema for Snowflake Hybrid Tables
-- ============================================================================

-- ============================================================================
-- REFERENCE DATA TABLES (seeded once)
-- ============================================================================

CREATE OR REPLACE HYBRID TABLE locations (
    location_id VARCHAR PRIMARY KEY,
    city VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    continent VARCHAR NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    description VARCHAR,
    image_url VARCHAR  -- Location scene art (full background)
);

CREATE OR REPLACE HYBRID TABLE landmarks (
    landmark_id VARCHAR PRIMARY KEY,
    location_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    landmark_type VARCHAR,
    clue_facts ARRAY,  -- JSON array of facts for clue generation
    image_url VARCHAR,  -- Landmark art (200x150px)
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE OR REPLACE HYBRID TABLE suspects (
    suspect_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    hair_color VARCHAR,
    eye_color VARCHAR,
    hobby VARCHAR,
    vehicle VARCHAR,
    favorite_food VARCHAR,
    distinguishing_feature VARCHAR,
    mugshot_url VARCHAR  -- Suspect portrait art (150x200px)
);

CREATE OR REPLACE HYBRID TABLE clue_images (
    image_id VARCHAR PRIMARY KEY,
    clue_type VARCHAR NOT NULL,  -- 'destination', 'suspect', 'item'
    image_url VARCHAR NOT NULL,  -- Clue art (100x100px)
    description VARCHAR
);

-- ============================================================================
-- GAME STATE TABLES
-- ============================================================================

CREATE OR REPLACE HYBRID TABLE players (
    player_id VARCHAR PRIMARY KEY,  -- Uses CURRENT_USER() from Snowflake session
    snowflake_user VARCHAR NOT NULL,  -- CURRENT_USER()
    email VARCHAR,  -- Available via SSO/SAML claims if configured
    rank VARCHAR DEFAULT 'Rookie',
    cases_solved INT DEFAULT 0,
    total_score INT DEFAULT 0,
    ai_prompt_count INT DEFAULT 0,  -- Tracks total AI prompts used by this player
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE HYBRID TABLE cases (
    case_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    suspect_id VARCHAR NOT NULL,
    stolen_item VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    location_path ARRAY,  -- Ordered list of location_ids
    status VARCHAR DEFAULT 'active',  -- 'active', 'won', 'lost'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id)
);

CREATE OR REPLACE HYBRID TABLE case_progress (
    case_id VARCHAR PRIMARY KEY,
    current_location_id VARCHAR NOT NULL,
    suspect_location_idx INT DEFAULT 0,
    hours_remaining INT NOT NULL,
    clues_gathered ARRAY,  -- Collected clue texts
    locations_visited ARRAY,  -- Visited location_ids
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    FOREIGN KEY (current_location_id) REFERENCES locations(location_id)
);

CREATE OR REPLACE HYBRID TABLE high_scores (
    score_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    completion_time_hours INT NOT NULL,  -- Lower is better
    locations_visited INT NOT NULL,
    score INT NOT NULL,  -- Calculated: (time_budget - completion_time) * difficulty_multiplier
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    INDEX idx_high_scores_difficulty (difficulty),
    INDEX idx_high_scores_score (score DESC)
);

-- ============================================================================
-- TELEMETRY TABLES (Analytics)
-- ============================================================================

-- Track play sessions for engagement metrics
CREATE OR REPLACE HYBRID TABLE game_sessions (
    session_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    ended_at TIMESTAMP,
    duration_seconds INT,
    cases_started INT DEFAULT 0,
    cases_completed INT DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Granular event log for funnel analysis
CREATE OR REPLACE HYBRID TABLE game_events (
    event_id VARCHAR PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR,
    event_type VARCHAR NOT NULL,  -- See event types in documentation
    event_data VARIANT,  -- JSON payload with context
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id),
    INDEX idx_events_player (player_id),
    INDEX idx_events_type (event_type),
    INDEX idx_events_time (created_at)
);

-- Aggregated case outcomes for success/failure analysis
CREATE OR REPLACE HYBRID TABLE case_analytics (
    case_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    outcome VARCHAR NOT NULL,  -- 'won', 'lost_time', 'lost_wrong_arrest', 'abandoned'
    total_locations_in_path INT,
    locations_visited INT,
    correct_travels INT,  -- Traveled to correct next location
    wrong_travels INT,  -- Traveled to wrong location
    clues_gathered INT,
    time_budget_hours INT,
    time_used_hours INT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    INDEX idx_analytics_difficulty (difficulty),
    INDEX idx_analytics_outcome (outcome)
);

-- Track where players get stuck (friction points)
CREATE OR REPLACE HYBRID TABLE friction_points (
    friction_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR NOT NULL,
    location_id VARCHAR NOT NULL,
    friction_type VARCHAR NOT NULL,  -- 'repeated_wrong_travel', 'time_expired_here', 'abandoned_here'
    attempts_at_location INT,
    time_spent_hours INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    INDEX idx_friction_location (location_id),
    INDEX idx_friction_type (friction_type)
);

-- ============================================================================
-- ANALYTICS VIEWS (for dashboards)
-- ============================================================================

-- Daily active users
CREATE OR REPLACE VIEW v_daily_active_users AS
SELECT DATE(started_at) as play_date, COUNT(DISTINCT player_id) as dau
FROM game_sessions 
GROUP BY 1 
ORDER BY 1;

-- Win rate by difficulty
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

-- Top friction locations
CREATE OR REPLACE VIEW v_friction_hotspots AS
SELECT 
    l.city, 
    l.country, 
    f.friction_type, 
    COUNT(*) as occurrences
FROM friction_points f
JOIN locations l ON f.location_id = l.location_id
GROUP BY 1, 2, 3 
ORDER BY occurrences DESC 
LIMIT 20;

-- Leaderboard
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

