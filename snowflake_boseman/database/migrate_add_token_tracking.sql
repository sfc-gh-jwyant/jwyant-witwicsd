-- Migration: Add AI token tracking columns
-- Run this if you have an existing database without these columns

-- Add ai_token_count to players table
ALTER TABLE players ADD COLUMN IF NOT EXISTS ai_token_count INT DEFAULT 0;
UPDATE players SET ai_token_count = 0 WHERE ai_token_count IS NULL;

-- Add AI tracking columns to case_analytics table
ALTER TABLE case_analytics ADD COLUMN IF NOT EXISTS ai_prompts INT DEFAULT 0;
ALTER TABLE case_analytics ADD COLUMN IF NOT EXISTS ai_tokens INT DEFAULT 0;
ALTER TABLE case_analytics ADD COLUMN IF NOT EXISTS ai_model VARCHAR;

UPDATE case_analytics SET ai_prompts = 0 WHERE ai_prompts IS NULL;
UPDATE case_analytics SET ai_tokens = 0 WHERE ai_tokens IS NULL;
