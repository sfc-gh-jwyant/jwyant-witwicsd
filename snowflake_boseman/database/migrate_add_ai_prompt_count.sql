-- Migration: Add ai_prompt_count column to players table
-- Run this if you have an existing database without this column

ALTER TABLE players ADD COLUMN IF NOT EXISTS ai_prompt_count INT DEFAULT 0;

-- Update any NULL values to 0
UPDATE players SET ai_prompt_count = 0 WHERE ai_prompt_count IS NULL;
