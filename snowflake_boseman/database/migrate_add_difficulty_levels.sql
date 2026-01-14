-- Migration: Add difficulty_levels table
-- Run this if you have an existing database without this table

CREATE TABLE IF NOT EXISTS difficulty_levels (
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

-- All difficulties have 144 hours (6 days like original Carmen Sandiego)
-- Difficulty names inspired by Snowflake, database, and AI concepts
INSERT INTO difficulty_levels (difficulty_id, name, description, time_budget_hours, clue_clarity, min_locations, max_locations, red_herrings, decoy_destinations) VALUES
(1, 'XS Warehouse', 'Extra Small challenge - clues served instantly', 144, 'obvious', 3, 4, 0, 2),
(2, 'Query Queued', 'Your investigation has been queued behind 3 others', 144, 'clear', 4, 5, 1, 4),
(3, 'Schema Drift', 'The clues keep changing when you are not looking', 144, 'cryptic', 5, 7, 2, 6),
(4, 'Cortex Hallucinating', 'The AI is confident but probably wrong', 144, 'very_cryptic', 7, 9, 3, 8),
(5, 'DROP PRODUCTION CASCADE', 'Everything is on fire. Good luck.', 144, 'riddle', 9, 12, 4, 10);

-- Update the view to use the new table
CREATE OR REPLACE VIEW v_win_rate_by_difficulty AS
SELECT ca.difficulty,
    dl.name as difficulty_name,
    COUNT(*) as total_cases, SUM(CASE WHEN outcome = 'won' THEN 1 ELSE 0 END) as wins
FROM case_analytics ca
LEFT JOIN difficulty_levels dl ON ca.difficulty = dl.difficulty_id
GROUP BY ca.difficulty, dl.name 
ORDER BY ca.difficulty;

SELECT 'Migration complete: difficulty_levels table created and populated.' as status;
