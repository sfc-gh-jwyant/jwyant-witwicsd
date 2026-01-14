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
    ai_token_count INT DEFAULT 0,   -- Tracks total AI tokens used by this player
    ai_credits_used FLOAT DEFAULT 0.0,  -- Tracks total Snowflake credits used for AI
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE HYBRID TABLE high_scores (
    score_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    completion_time_hours INT NOT NULL,  -- Lower is better
    locations_visited INT NOT NULL,
    score INT NOT NULL,  -- Based on AI credits used (lower is better, like golf)
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    INDEX idx_high_scores_difficulty (difficulty),
    INDEX idx_high_scores_score (score ASC)  -- Lower scores are better
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
    ai_prompts INT DEFAULT 0,  -- Number of AI prompts used in this case
    ai_tokens INT DEFAULT 0,   -- Total tokens used in this case
    ai_credits FLOAT DEFAULT 0.0,  -- Credits used in this case
    ai_model VARCHAR,          -- Model used for this case
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    INDEX idx_analytics_difficulty (difficulty),
    INDEX idx_analytics_outcome (outcome)
);

-- ============================================================================
-- CONFIGURATION TABLES
-- ============================================================================

CREATE OR REPLACE HYBRID TABLE difficulty_levels (
    difficulty_id INT PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    time_budget_hours INT NOT NULL,
    clue_clarity VARCHAR NOT NULL,
    min_locations INT NOT NULL,
    max_locations INT NOT NULL,
    red_herrings INT NOT NULL,
    decoy_destinations INT NOT NULL
);

CREATE OR REPLACE HYBRID TABLE stolen_items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR NOT NULL,
    category VARCHAR
);

CREATE OR REPLACE HYBRID TABLE cortex_credit_rates (
    model_name VARCHAR PRIMARY KEY,
    input_rate FLOAT NOT NULL,  -- Credits per 1M input tokens
    output_rate FLOAT NOT NULL, -- Credits per 1M output tokens
    effective_date DATE NOT NULL
);
