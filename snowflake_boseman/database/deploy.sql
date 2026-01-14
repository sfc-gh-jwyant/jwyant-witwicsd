-- ============================================================================
-- WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?
-- Deployment Script for DEMO_WITWISBM Database (Hybrid Tables)
-- ============================================================================

-- Create and use the database
CREATE DATABASE IF NOT EXISTS DEMO_WITWISBM;
USE DATABASE DEMO_WITWISBM;

-- Create schema
CREATE SCHEMA IF NOT EXISTS GAME;
USE SCHEMA GAME;

-- ============================================================================
-- REFERENCE DATA TABLES (Hybrid Tables)
-- ============================================================================

CREATE OR REPLACE HYBRID TABLE locations (
    location_id VARCHAR PRIMARY KEY,
    city VARCHAR NOT NULL,
    country VARCHAR NOT NULL,
    continent VARCHAR NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    description VARCHAR,
    image_url VARCHAR
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
    mugshot_url VARCHAR
);

-- ============================================================================
-- GAME STATE TABLES
-- ============================================================================

CREATE OR REPLACE HYBRID TABLE players (
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

CREATE OR REPLACE HYBRID TABLE high_scores (
    score_id VARCHAR PRIMARY KEY,
    player_id VARCHAR NOT NULL,
    case_id VARCHAR NOT NULL,
    difficulty INT NOT NULL,
    completion_time_hours INT NOT NULL,
    locations_visited INT NOT NULL,
    score INT NOT NULL,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

CREATE OR REPLACE HYBRID TABLE case_analytics (
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
    input_rate FLOAT NOT NULL,
    output_rate FLOAT NOT NULL,
    effective_date DATE NOT NULL
);

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

SELECT 'Database DEMO_WITWISBM schema created successfully!' as status;
