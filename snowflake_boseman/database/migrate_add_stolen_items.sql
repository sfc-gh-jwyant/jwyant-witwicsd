-- Migration: Add stolen_items table
-- Run this if you have an existing database without this table

CREATE TABLE IF NOT EXISTS stolen_items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR NOT NULL,
    category VARCHAR
);

-- Insert stolen items (use MERGE to avoid duplicates)
MERGE INTO stolen_items s
USING (
    SELECT 1 as item_id, 'the entire Data Cloud' as item_name, 'snowflake' as category
    UNION ALL SELECT 2, 'a Virtual Warehouse (still running)', 'snowflake'
    UNION ALL SELECT 3, 'the Zero-Copy Cloning patent', 'snowflake'
    UNION ALL SELECT 4, 'all the Snowflake Credits', 'snowflake'
    UNION ALL SELECT 5, 'the Time Travel feature (from the future)', 'snowflake'
    UNION ALL SELECT 6, 'a Snowpark DataFrame', 'snowflake'
    UNION ALL SELECT 7, 'the Cortex AI brain', 'snowflake'
    UNION ALL SELECT 8, 'a perfectly optimized query plan', 'snowflake'
    UNION ALL SELECT 9, 'the Snowflake Arctic model weights', 'snowflake'
    UNION ALL SELECT 10, 'the Fail-Safe backup tapes', 'snowflake'
    UNION ALL SELECT 11, 'a Secure Data Share agreement', 'snowflake'
    UNION ALL SELECT 12, 'the Snowflake Marketplace catalog', 'snowflake'
    UNION ALL SELECT 13, 'a Snowpipe (still streaming)', 'snowflake'
    UNION ALL SELECT 14, 'the Dynamic Data Masking policies', 'snowflake'
    UNION ALL SELECT 15, 'a Materialized View (very heavy)', 'snowflake'
    UNION ALL SELECT 16, 'all the NULL values', 'database'
    UNION ALL SELECT 17, 'the PRIMARY KEY to success', 'database'
    UNION ALL SELECT 18, 'a perfectly normalized schema', 'database'
    UNION ALL SELECT 19, 'the last working INDEX', 'database'
    UNION ALL SELECT 20, 'a FOREIGN KEY relationship', 'database'
    UNION ALL SELECT 21, 'the DROP TABLE permissions', 'database'
    UNION ALL SELECT 22, 'a recursive CTE that actually works', 'database'
    UNION ALL SELECT 23, 'the ACID compliance certificate', 'database'
    UNION ALL SELECT 24, 'a MERGE statement without conflicts', 'database'
    UNION ALL SELECT 25, 'the database admin password (on a sticky note)', 'database'
    UNION ALL SELECT 26, 'the last working printer', 'tech'
    UNION ALL SELECT 27, 'all the semicolons from production code', 'tech'
    UNION ALL SELECT 28, 'the WiFi password', 'tech'
    UNION ALL SELECT 29, 'a stack of Stack Overflow answers', 'tech'
    UNION ALL SELECT 30, 'the Kubernetes cluster (all 47 pods)', 'tech'
    UNION ALL SELECT 31, 'a Docker container (still containerized)', 'tech'
    UNION ALL SELECT 32, 'the Git history (force pushed)', 'tech'
    UNION ALL SELECT 33, 'the original Bitcoin wallet', 'tech'
    UNION ALL SELECT 34, 'a working Regex pattern', 'tech'
    UNION ALL SELECT 35, 'the cloud (literally, a small fluffy one)', 'tech'
    UNION ALL SELECT 36, 'a Large Language Model (extra large)', 'ai'
    UNION ALL SELECT 37, 'the training data for GPT-6', 'ai'
    UNION ALL SELECT 38, 'all the GPU memory', 'ai'
    UNION ALL SELECT 39, 'a perfectly tuned hyperparameter', 'ai'
    UNION ALL SELECT 40, 'the neural network secret sauce', 'ai'
    UNION ALL SELECT 41, 'an AI that passed the Turing test', 'ai'
    UNION ALL SELECT 42, 'the embeddings to life, the universe, and everything', 'ai'
    UNION ALL SELECT 43, 'the Any Key (nobody could find it anyway)', 'classic'
    UNION ALL SELECT 44, 'a box of unused floppy disks', 'classic'
    UNION ALL SELECT 45, 'the source code to Pac-Man', 'classic'
    UNION ALL SELECT 46, 'a Y2K survival kit', 'classic'
    UNION ALL SELECT 47, 'the Windows 95 startup sound', 'classic'
    UNION ALL SELECT 48, 'a dial-up modem (for nostalgia)', 'classic'
    UNION ALL SELECT 49, 'the Konami Code', 'classic'
    UNION ALL SELECT 50, 'a copy of Half-Life 3', 'classic'
    UNION ALL SELECT 51, 'the Iceberg table (very cold)', 'snowflake'
    UNION ALL SELECT 52, 'a Streamlit app (this one, actually)', 'snowflake'
    UNION ALL SELECT 53, 'the account admin role', 'snowflake'
    UNION ALL SELECT 54, 'all the micro-partitions', 'snowflake'
    UNION ALL SELECT 55, 'the Query History logs', 'snowflake'
    UNION ALL SELECT 56, 'a Reader Account invitation', 'snowflake'
    UNION ALL SELECT 57, 'the Data Clean Room blueprints', 'snowflake'
    UNION ALL SELECT 58, 'a perfectly partitioned table', 'database'
    UNION ALL SELECT 59, 'the execution plan from a 3-hour query', 'database'
    UNION ALL SELECT 60, 'the INFORMATION_SCHEMA', 'database'
) src
ON s.item_id = src.item_id
WHEN NOT MATCHED THEN INSERT (item_id, item_name, category)
VALUES (src.item_id, src.item_name, src.category);

SELECT 'Migration complete: stolen_items table created with ' || COUNT(*) || ' items.' as status
FROM stolen_items;
