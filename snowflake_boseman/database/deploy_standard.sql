-- ============================================================================
-- WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?
-- Deployment Script using Standard Tables (for reader/trial accounts)
-- ============================================================================

-- Use the existing database
USE DATABASE DEMO_WITWISBM;
USE SCHEMA GAME;

-- ============================================================================
-- REFERENCE DATA TABLES
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
    ai_credits_used FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
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
    ai_credits FLOAT DEFAULT 0.0,
    ai_model VARCHAR,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE OR REPLACE TABLE difficulty_levels (
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

CREATE OR REPLACE TABLE stolen_items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR NOT NULL,
    category VARCHAR
);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Tables created successfully in DEMO_WITWISBM.GAME!' as status;
