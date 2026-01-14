-- Migration: Add stolen_items table
-- Run this if you have an existing database without this table

CREATE TABLE IF NOT EXISTS stolen_items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR NOT NULL,
    category VARCHAR
);

-- Insert stolen items (60 tech/Snowflake themed joke items)
INSERT INTO stolen_items (item_id, item_name, category) VALUES
-- Snowflake Data Cloud themed
(1, 'the entire Data Cloud', 'snowflake'),
(2, 'a Virtual Warehouse (still running)', 'snowflake'),
(3, 'the Zero-Copy Cloning patent', 'snowflake'),
(4, 'all the Snowflake Credits', 'snowflake'),
(5, 'the Time Travel feature (from the future)', 'snowflake'),
(6, 'a Snowpark DataFrame', 'snowflake'),
(7, 'the Cortex AI brain', 'snowflake'),
(8, 'a perfectly optimized query plan', 'snowflake'),
(9, 'the Snowflake Arctic model weights', 'snowflake'),
(10, 'the Fail-Safe backup tapes', 'snowflake'),
(11, 'a Secure Data Share agreement', 'snowflake'),
(12, 'the Snowflake Marketplace catalog', 'snowflake'),
(13, 'a Snowpipe (still streaming)', 'snowflake'),
(14, 'the Dynamic Data Masking policies', 'snowflake'),
(15, 'a Materialized View (very heavy)', 'snowflake'),

-- Database humor
(16, 'all the NULL values', 'database'),
(17, 'the PRIMARY KEY to success', 'database'),
(18, 'a perfectly normalized schema', 'database'),
(19, 'the last working INDEX', 'database'),
(20, 'a FOREIGN KEY relationship', 'database'),
(21, 'the DROP TABLE permissions', 'database'),
(22, 'a recursive CTE that actually works', 'database'),
(23, 'the ACID compliance certificate', 'database'),
(24, 'a MERGE statement without conflicts', 'database'),
(25, 'the database admin password (on a sticky note)', 'database'),

-- General tech humor
(26, 'the last working printer', 'tech'),
(27, 'all the semicolons from production code', 'tech'),
(28, 'the WiFi password', 'tech'),
(29, 'a stack of Stack Overflow answers', 'tech'),
(30, 'the Kubernetes cluster (all 47 pods)', 'tech'),
(31, 'a Docker container (still containerized)', 'tech'),
(32, 'the Git history (force pushed)', 'tech'),
(33, 'the original Bitcoin wallet', 'tech'),
(34, 'a working Regex pattern', 'tech'),
(35, 'the cloud (literally, a small fluffy one)', 'tech'),

-- AI/ML themed
(36, 'a Large Language Model (extra large)', 'ai'),
(37, 'the training data for GPT-6', 'ai'),
(38, 'all the GPU memory', 'ai'),
(39, 'a perfectly tuned hyperparameter', 'ai'),
(40, 'the neural network secret sauce', 'ai'),
(41, 'an AI that passed the Turing test', 'ai'),
(42, 'the embeddings to life, the universe, and everything', 'ai'),

-- Classic computer jokes
(43, 'the Any Key (nobody could find it anyway)', 'classic'),
(44, 'a box of unused floppy disks', 'classic'),
(45, 'the source code to Pac-Man', 'classic'),
(46, 'a Y2K survival kit', 'classic'),
(47, 'the Windows 95 startup sound', 'classic'),
(48, 'a dial-up modem (for nostalgia)', 'classic'),
(49, 'the Konami Code', 'classic'),
(50, 'a copy of Half-Life 3', 'classic'),

-- More Snowflake/data themed
(51, 'the Iceberg table (very cold)', 'snowflake'),
(52, 'a Streamlit app (this one, actually)', 'snowflake'),
(53, 'the account admin role', 'snowflake'),
(54, 'all the micro-partitions', 'snowflake'),
(55, 'the Query History logs', 'snowflake'),
(56, 'a Reader Account invitation', 'snowflake'),
(57, 'the Data Clean Room blueprints', 'snowflake'),
(58, 'a perfectly partitioned table', 'database'),
(59, 'the execution plan from a 3-hour query', 'database'),
(60, 'the INFORMATION_SCHEMA', 'database');

SELECT 'Migration complete: stolen_items table created with ' || COUNT(*) || ' items.' as status
FROM stolen_items;
