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
-- Difficulty changes: clue clarity, number of locations, red herrings, decoys
INSERT INTO difficulty_levels (difficulty_id, name, description, time_budget_hours, clue_clarity, min_locations, max_locations, red_herrings, decoy_destinations) VALUES
(1, 'SELECT * FROM clues', 'Obvious clues, short chase', 144, 'obvious', 3, 4, 0, 2),
(2, 'WITH (NOLOCK)', 'Clear hints, moderate chase', 144, 'clear', 4, 5, 1, 4),
(3, 'Foreign Key Violation', 'Cryptic clues, longer chase', 144, 'cryptic', 5, 7, 2, 6),
(4, 'Deadlock Victim', 'Very cryptic, extended chase', 144, 'very_cryptic', 7, 9, 3, 8),
(5, 'Little Bobby Tables', 'Riddles only, world tour', 144, 'riddle', 9, 12, 4, 10);

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
