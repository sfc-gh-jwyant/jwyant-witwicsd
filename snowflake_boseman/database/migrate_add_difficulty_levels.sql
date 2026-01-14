-- Migration: Add difficulty_levels table
-- Run this if you have an existing database without this table

-- Create the difficulty_levels table
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

-- Insert difficulty levels (use MERGE to avoid duplicates)
MERGE INTO difficulty_levels d
USING (
    SELECT 1 as difficulty_id, 'SELECT * FROM clues' as name, 'All clues visible, lots of time' as description, 72 as time_budget_hours, 'obvious' as clue_clarity, 3 as min_locations, 4 as max_locations, 0 as red_herrings, 2 as decoy_destinations
    UNION ALL SELECT 2, 'WITH (NOLOCK)', 'Clear hints, moderate challenge', 48, 'clear', 4, 5, 1, 3
    UNION ALL SELECT 3, 'Foreign Key Violation', 'Cryptic clues, tighter deadline', 36, 'cryptic', 5, 7, 2, 5
    UNION ALL SELECT 4, 'Deadlock Victim', 'Very cryptic, time pressure', 24, 'very_cryptic', 6, 8, 3, 7
    UNION ALL SELECT 5, 'Little Bobby Tables', 'Expert mode - riddles only', 12, 'riddle', 8, 10, 4, 10
) src
ON d.difficulty_id = src.difficulty_id
WHEN NOT MATCHED THEN INSERT (difficulty_id, name, description, time_budget_hours, clue_clarity, min_locations, max_locations, red_herrings, decoy_destinations)
VALUES (src.difficulty_id, src.name, src.description, src.time_budget_hours, src.clue_clarity, src.min_locations, src.max_locations, src.red_herrings, src.decoy_destinations);

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
