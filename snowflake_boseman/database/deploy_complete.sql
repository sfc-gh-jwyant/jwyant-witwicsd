-- ============================================================================
-- WHERE IN THE WORLD IS SNOWFLAKE BOSEMAN MONTANA?
-- Complete Deployment Script (Database + Tables + Seed Data)
-- Run this in Snowsight or authenticated SnowSQL session
-- ============================================================================

-- Create and use the database
CREATE DATABASE IF NOT EXISTS DEMO_WITWISBM;
USE DATABASE DEMO_WITWISBM;
CREATE SCHEMA IF NOT EXISTS GAME;
USE SCHEMA GAME;

-- ============================================================================
-- CREATE ALL TABLES
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

CREATE OR REPLACE TABLE cortex_credit_rates (
    model_name VARCHAR PRIMARY KEY,
    input_rate FLOAT NOT NULL,  -- Credits per 1M input tokens
    output_rate FLOAT NOT NULL, -- Credits per 1M output tokens
    effective_date DATE
);

-- ============================================================================
-- SEED DATA: CORTEX CREDIT RATES (per 1M tokens)
-- Score = input_tokens * input_rate + output_tokens * output_rate
-- ============================================================================

INSERT INTO cortex_credit_rates (model_name, input_rate, output_rate, effective_date) VALUES
-- Anthropic Claude models
('claude-3-5-sonnet', 1.50, 7.50, '2026-01-13'),
('claude-3-7-sonnet', 1.50, 7.50, '2026-01-13'),
('claude-4-sonnet', 1.50, 7.50, '2026-01-13'),
('claude-4-opus', 7.50, 37.50, '2026-01-13'),
('claude-haiku-4-5', 0.55, 2.75, '2026-01-13'),
('claude-opus-4-5', 2.75, 13.75, '2026-01-13'),
('claude-sonnet-4-5', 1.65, 8.25, '2026-01-13'),
-- DeepSeek
('deepseek-r1', 0.68, 2.70, '2026-01-13'),
-- Google Gemini
('gemini-2-5-flash', 0.15, 1.25, '2026-01-13'),
('gemini-2-5-flash-lite', 0.05, 0.20, '2026-01-13'),
('gemini-3-pro', 1.00, 6.00, '2026-01-13'),
-- Meta Llama
('llama3.1-405b', 1.20, 1.20, '2026-01-13'),
('llama3.1-70b', 0.36, 0.36, '2026-01-13'),
('llama3.1-8b', 0.11, 0.11, '2026-01-13'),
('llama3.3-70b', 0.36, 0.36, '2026-01-13'),
('llama4-maverick', 0.12, 0.49, '2026-01-13'),
('llama4-scout', 0.09, 0.33, '2026-01-13'),
-- Mistral
('mistral-large2', 1.00, 3.00, '2026-01-13'),
('mistral-7b', 0.08, 0.10, '2026-01-13'),
('mixtral-8x7b', 0.23, 0.35, '2026-01-13'),
('pixtral-large', 1.00, 3.00, '2026-01-13'),
-- OpenAI
('openai-gpt-4.1', 1.00, 4.00, '2026-01-13'),
('openai-gpt-5', 0.69, 5.50, '2026-01-13'),
('openai-gpt-5-chat', 0.63, 5.00, '2026-01-13'),
('openai-gpt-5-mini', 0.14, 1.10, '2026-01-13'),
('openai-gpt-5-nano', 0.03, 0.22, '2026-01-13'),
('openai-gpt-5.1', 0.69, 5.50, '2026-01-13'),
('openai-gpt-5.2', 0.97, 7.70, '2026-01-13'),
('openai-gpt-oss-120b', 0.08, 0.30, '2026-01-13'),
('openai-gpt-oss-20b', 0.04, 0.15, '2026-01-13'),
('openai-o4-mini', 0.55, 2.20, '2026-01-13'),
-- Snowflake
('snowflake-arctic', 0.84, 0.84, '2026-01-13'),
('snowflake-llama-3.1-405b', 0.96, 0.96, '2026-01-13'),
('snowflake-llama-3.3-70b', 0.29, 0.29, '2026-01-13');

-- ============================================================================
-- SEED DATA: 100 CITIES
-- ============================================================================

INSERT INTO locations (location_id, city, country, continent, latitude, longitude, description) VALUES
('loc_paris', 'Paris', 'France', 'Europe', 48.8566, 2.3522, 'The City of Light, known for its iconic iron tower, world-class museums, and romantic boulevards.'),
('loc_london', 'London', 'United Kingdom', 'Europe', 51.5074, -0.1278, 'A historic metropolis where ancient castles meet modern skyscrapers along the winding Thames.'),
('loc_rome', 'Rome', 'Italy', 'Europe', 41.9028, 12.4964, 'The Eternal City, where ancient ruins stand alongside Renaissance masterpieces and bustling piazzas.'),
('loc_amsterdam', 'Amsterdam', 'Netherlands', 'Europe', 52.3676, 4.9041, 'A city of canals, cycling culture, and world-famous museums housing Dutch masters.'),
('loc_barcelona', 'Barcelona', 'Spain', 'Europe', 41.3851, 2.1734, 'A Mediterranean gem famous for whimsical architecture and vibrant street life.'),
('loc_tokyo', 'Tokyo', 'Japan', 'Asia', 35.6762, 139.6503, 'A neon-lit metropolis where ancient temples coexist with cutting-edge technology.'),
('loc_bangkok', 'Bangkok', 'Thailand', 'Asia', 13.7563, 100.5018, 'A city of ornate temples, floating markets, and legendary street food.'),
('loc_mumbai', 'Mumbai', 'India', 'Asia', 19.0760, 72.8777, 'India''s bustling financial capital, home to Bollywood and the iconic Gateway.'),
('loc_singapore', 'Singapore', 'Singapore', 'Asia', 1.3521, 103.8198, 'A futuristic city-state known for its gardens, hawker centers, and immaculate streets.'),
('loc_beijing', 'Beijing', 'China', 'Asia', 39.9042, 116.4074, 'An ancient capital with imperial palaces, massive squares, and the nearby Great Wall.'),
('loc_newyork', 'New York City', 'United States', 'North America', 40.7128, -74.0060, 'The city that never sleeps, with towering skyscrapers, Broadway lights, and Central Park.'),
('loc_losangeles', 'Los Angeles', 'United States', 'North America', 34.0522, -118.2437, 'The entertainment capital of the world, where palm trees line boulevards of stars.'),
('loc_mexico', 'Mexico City', 'Mexico', 'North America', 19.4326, -99.1332, 'A vibrant capital built on ancient Aztec ruins, famous for its cuisine and murals.'),
('loc_toronto', 'Toronto', 'Canada', 'North America', 43.6532, -79.3832, 'Canada''s largest city, known for its iconic tower and diverse neighborhoods.'),
('loc_sanfrancisco', 'San Francisco', 'United States', 'North America', 37.7749, -122.4194, 'A hilly city famous for its red bridge, cable cars, and tech innovation.'),
('loc_rio', 'Rio de Janeiro', 'Brazil', 'South America', -22.9068, -43.1729, 'A cidade maravilhosa with stunning beaches, a famous statue, and carnival spirit.'),
('loc_buenosaires', 'Buenos Aires', 'Argentina', 'South America', -34.6037, -58.3816, 'The Paris of South America, known for tango, steak, and European-style architecture.'),
('loc_lima', 'Lima', 'Peru', 'South America', -12.0464, -77.0428, 'A culinary capital perched above the Pacific, gateway to ancient Incan wonders.'),
('loc_cairo', 'Cairo', 'Egypt', 'Africa', 30.0444, 31.2357, 'A sprawling city at the edge of the desert, guarded by ancient pyramids.'),
('loc_capetown', 'Cape Town', 'South Africa', 'Africa', -33.9249, 18.4241, 'A stunning coastal city beneath a flat-topped mountain at Africa''s southern tip.'),
('loc_marrakech', 'Marrakech', 'Morocco', 'Africa', 31.6295, -7.9811, 'A sensory feast of spice markets, ornate palaces, and snake charmers.'),
('loc_sydney', 'Sydney', 'Australia', 'Oceania', -33.8688, 151.2093, 'A harbor city famous for its sail-shaped opera house and iconic bridge.'),
('loc_auckland', 'Auckland', 'New Zealand', 'Oceania', -36.8509, 174.7645, 'The City of Sails, gateway to volcanic landscapes and Maori culture.'),
('loc_mcmurdo', 'McMurdo Station', 'Antarctica', 'Antarctica', -77.8419, 166.6863, 'A remote research station on the frozen continent, accessible only by ice.'),
('loc_bozeman', 'Bozeman', 'United States', 'North America', 45.6770, -111.0429, 'A mountain town in Big Sky Country, gateway to Yellowstone and home to Snowflake HQ.'),
('loc_berlin', 'Berlin', 'Germany', 'Europe', 52.5200, 13.4050, 'A city of history and reinvention, where the remnants of a divided past meet cutting-edge culture.'),
('loc_vienna', 'Vienna', 'Austria', 'Europe', 48.2082, 16.3738, 'The city of music and imperial grandeur, where Mozart and Freud once walked.'),
('loc_prague', 'Prague', 'Czech Republic', 'Europe', 50.0755, 14.4378, 'The City of a Hundred Spires, with a medieval old town and famous astronomical clock.'),
('loc_budapest', 'Budapest', 'Hungary', 'Europe', 47.4979, 19.0402, 'The Pearl of the Danube, famous for thermal baths and stunning architecture.'),
('loc_athens', 'Athens', 'Greece', 'Europe', 37.9838, 23.7275, 'The cradle of Western civilization, dominated by the ancient Acropolis.'),
('loc_lisbon', 'Lisbon', 'Portugal', 'Europe', 38.7223, -9.1393, 'A hilly coastal capital famous for pastel buildings, trams, and pastéis de nata.'),
('loc_dublin', 'Dublin', 'Ireland', 'Europe', 53.3498, -6.2603, 'A literary capital with Georgian architecture and legendary pub culture.'),
('loc_edinburgh', 'Edinburgh', 'Scotland', 'Europe', 55.9533, -3.1883, 'A dramatic city with a medieval Old Town and elegant Georgian New Town.'),
('loc_stockholm', 'Stockholm', 'Sweden', 'Europe', 59.3293, 18.0686, 'A city spread across 14 islands, known for design, innovation, and the Nobel Prize.'),
('loc_copenhagen', 'Copenhagen', 'Denmark', 'Europe', 55.6761, 12.5683, 'The happiest city, home to Tivoli Gardens and the Little Mermaid.'),
('loc_oslo', 'Oslo', 'Norway', 'Europe', 59.9139, 10.7522, 'A city surrounded by fjords and forests, gateway to Nordic wilderness.'),
('loc_helsinki', 'Helsinki', 'Finland', 'Europe', 60.1699, 24.9384, 'A design capital on the Baltic Sea, famous for saunas and modern architecture.'),
('loc_warsaw', 'Warsaw', 'Poland', 'Europe', 52.2297, 21.0122, 'A phoenix city rebuilt from WWII ashes, blending history with modernity.'),
('loc_brussels', 'Brussels', 'Belgium', 'Europe', 50.8503, 4.3517, 'The heart of the EU, famous for chocolate, waffles, and Art Nouveau.'),
('loc_zurich', 'Zurich', 'Switzerland', 'Europe', 47.3769, 8.5417, 'A pristine lakeside city known for banking, chocolate, and Alpine views.'),
('loc_munich', 'Munich', 'Germany', 'Europe', 48.1351, 11.5820, 'Bavaria''s capital, famous for Oktoberfest, beer gardens, and BMW.'),
('loc_milan', 'Milan', 'Italy', 'Europe', 45.4642, 9.1900, 'Italy''s fashion and finance capital, home to The Last Supper and La Scala.'),
('loc_venice', 'Venice', 'Italy', 'Europe', 45.4408, 12.3155, 'A floating city of canals, gondolas, and Renaissance masterpieces.'),
('loc_florence', 'Florence', 'Italy', 'Europe', 43.7696, 11.2558, 'The birthplace of the Renaissance, home to Michelangelo''s David.'),
('loc_istanbul', 'Istanbul', 'Turkey', 'Europe', 41.0082, 28.9784, 'A city straddling two continents, where Byzantine and Ottoman empires meet.'),
('loc_seoul', 'Seoul', 'South Korea', 'Asia', 37.5665, 126.9780, 'A high-tech metropolis where K-pop meets ancient palaces.'),
('loc_hongkong', 'Hong Kong', 'China', 'Asia', 22.3193, 114.1694, 'A dazzling harbor city with towering skyscrapers and dim sum traditions.'),
('loc_shanghai', 'Shanghai', 'China', 'Asia', 31.2304, 121.4737, 'China''s largest city, where Art Deco meets futuristic towers.'),
('loc_taipei', 'Taipei', 'Taiwan', 'Asia', 25.0330, 121.5654, 'A city of night markets, temples, and the iconic Taipei 101.'),
('loc_hanoi', 'Hanoi', 'Vietnam', 'Asia', 21.0278, 105.8342, 'Vietnam''s ancient capital with French colonial charm and street food paradise.'),
('loc_hochiminhcity', 'Ho Chi Minh City', 'Vietnam', 'Asia', 10.8231, 106.6297, 'A bustling metropolis blending war history with modern energy.'),
('loc_kualalumpur', 'Kuala Lumpur', 'Malaysia', 'Asia', 3.1390, 101.6869, 'A multicultural capital dominated by the iconic Petronas Towers.'),
('loc_jakarta', 'Jakarta', 'Indonesia', 'Asia', -6.2088, 106.8456, 'A sprawling megacity of contrasts, from colonial Dutch buildings to modern malls.'),
('loc_manila', 'Manila', 'Philippines', 'Asia', 14.5995, 120.9842, 'A vibrant bayside capital with Spanish colonial heritage.'),
('loc_delhi', 'Delhi', 'India', 'Asia', 28.7041, 77.1025, 'India''s capital territory, where Mughal monuments meet modern chaos.'),
('loc_kathmandu', 'Kathmandu', 'Nepal', 'Asia', 27.7172, 85.3240, 'A mystical valley city, gateway to the Himalayas and Everest.'),
('loc_colombo', 'Colombo', 'Sri Lanka', 'Asia', 6.9271, 79.8612, 'A tropical port city with colonial architecture and Buddhist temples.'),
('loc_dhaka', 'Dhaka', 'Bangladesh', 'Asia', 23.8103, 90.4125, 'One of the world''s most densely populated cities, a textile capital.'),
('loc_osaka', 'Osaka', 'Japan', 'Asia', 34.6937, 135.5023, 'Japan''s kitchen, famous for street food, castles, and comedy.'),
('loc_kyoto', 'Kyoto', 'Japan', 'Asia', 35.0116, 135.7681, 'The cultural heart of Japan, with thousands of temples and geisha traditions.'),
('loc_dubai', 'Dubai', 'United Arab Emirates', 'Asia', 25.2048, 55.2708, 'A desert oasis of superlatives: tallest building, largest mall, and artificial islands.'),
('loc_doha', 'Doha', 'Qatar', 'Asia', 25.2854, 51.5310, 'A futuristic Gulf city rising from the desert with world-class museums.'),
('loc_telaviv', 'Tel Aviv', 'Israel', 'Asia', 32.0853, 34.7818, 'A Mediterranean beach city known for Bauhaus architecture and startup culture.'),
('loc_jerusalem', 'Jerusalem', 'Israel', 'Asia', 31.7683, 35.2137, 'A holy city sacred to three religions, ancient and eternally contested.'),
('loc_baku', 'Baku', 'Azerbaijan', 'Asia', 40.4093, 49.8671, 'The City of Winds on the Caspian Sea, mixing ancient walls with flame towers.'),
('loc_chicago', 'Chicago', 'United States', 'North America', 41.8781, -87.6298, 'The Windy City, birthplace of the skyscraper and deep-dish pizza.'),
('loc_miami', 'Miami', 'United States', 'North America', 25.7617, -80.1918, 'A tropical gateway with Art Deco glamour and Cuban coffee.'),
('loc_lasvegas', 'Las Vegas', 'United States', 'North America', 36.1699, -115.1398, 'Sin City, where neon lights and casinos rise from the desert.'),
('loc_seattle', 'Seattle', 'United States', 'North America', 47.6062, -122.3321, 'The Emerald City, birthplace of grunge, coffee culture, and tech giants.'),
('loc_boston', 'Boston', 'United States', 'North America', 42.3601, -71.0589, 'America''s walking city, steeped in Revolutionary history.'),
('loc_neworleans', 'New Orleans', 'United States', 'North America', 29.9511, -90.0715, 'The Big Easy, where jazz, Creole cuisine, and Mardi Gras reign.'),
('loc_washingtondc', 'Washington D.C.', 'United States', 'North America', 38.9072, -77.0369, 'The nation''s capital, home to monuments, museums, and political power.'),
('loc_denver', 'Denver', 'United States', 'North America', 39.7392, -104.9903, 'The Mile High City, gateway to the Rocky Mountains.'),
('loc_vancouver', 'Vancouver', 'Canada', 'North America', 49.2827, -123.1207, 'A Pacific gem surrounded by mountains and ocean.'),
('loc_montreal', 'Montreal', 'Canada', 'North America', 45.5017, -73.5673, 'A bilingual city with European flair, poutine, and underground malls.'),
('loc_havana', 'Havana', 'Cuba', 'North America', 23.1136, -82.3666, 'A time-capsule city of vintage cars, salsa, and revolutionary history.'),
('loc_cancun', 'Cancun', 'Mexico', 'North America', 21.1619, -86.8515, 'A Caribbean resort paradise with nearby Mayan ruins.'),
('loc_guadalajara', 'Guadalajara', 'Mexico', 'North America', 20.6597, -103.3496, 'The birthplace of mariachi and tequila, Mexico''s cultural heartland.'),
('loc_panama', 'Panama City', 'Panama', 'North America', 8.9824, -79.5199, 'A modern skyline rising beside the famous canal.'),
('loc_sanjuan', 'San Juan', 'Puerto Rico', 'North America', 18.4655, -66.1057, 'A colorful colonial city with cobblestone streets and Caribbean vibes.'),
('loc_bogota', 'Bogotá', 'Colombia', 'South America', 4.7110, -74.0721, 'A high-altitude capital blending colonial history with street art culture.'),
('loc_medellin', 'Medellín', 'Colombia', 'South America', 6.2476, -75.5658, 'The City of Eternal Spring, transformed from infamous to innovative.'),
('loc_santiago', 'Santiago', 'Chile', 'South America', -33.4489, -70.6693, 'A modern capital nestled between the Andes and the Pacific.'),
('loc_quito', 'Quito', 'Ecuador', 'South America', -0.1807, -78.4678, 'A UNESCO city on the equator with preserved colonial architecture.'),
('loc_lapaz', 'La Paz', 'Bolivia', 'South America', -16.4897, -68.1193, 'The world''s highest capital, set in a dramatic Andean canyon.'),
('loc_montevideo', 'Montevideo', 'Uruguay', 'South America', -34.9011, -56.1645, 'A relaxed riverside capital with Art Deco architecture and mate culture.'),
('loc_cartagena', 'Cartagena', 'Colombia', 'South America', 10.3910, -75.4794, 'A Caribbean walled city of colorful colonial streets.'),
('loc_cusco', 'Cusco', 'Peru', 'South America', -13.5320, -71.9675, 'The ancient Incan capital and gateway to Machu Picchu.'),
('loc_saopaulo', 'São Paulo', 'Brazil', 'South America', -23.5505, -46.6333, 'South America''s largest city, a concrete jungle of culture and cuisine.'),
('loc_salvador', 'Salvador', 'Brazil', 'South America', -12.9714, -38.5014, 'Brazil''s Afro-Brazilian heart, famous for Carnival and capoeira.'),
('loc_nairobi', 'Nairobi', 'Kenya', 'Africa', -1.2921, 36.8219, 'A safari gateway city with a national park inside city limits.'),
('loc_johannesburg', 'Johannesburg', 'South Africa', 'Africa', -26.2041, 28.0473, 'The City of Gold, South Africa''s economic powerhouse.'),
('loc_lagos', 'Lagos', 'Nigeria', 'Africa', 6.5244, 3.3792, 'Africa''s largest city, a chaotic cultural and business hub.'),
('loc_accra', 'Accra', 'Ghana', 'Africa', 5.6037, -0.1870, 'A vibrant coastal capital blending colonial forts with Afrobeats culture.'),
('loc_addisababa', 'Addis Ababa', 'Ethiopia', 'Africa', 9.0320, 38.7469, 'Africa''s diplomatic capital, birthplace of coffee and ancient civilization.'),
('loc_dakar', 'Dakar', 'Senegal', 'Africa', 14.7167, -17.4677, 'A colorful Atlantic city at the westernmost point of Africa.'),
('loc_casablanca', 'Casablanca', 'Morocco', 'Africa', 33.5731, -7.5898, 'Morocco''s largest city with stunning Art Deco and the Hassan II Mosque.'),
('loc_tunis', 'Tunis', 'Tunisia', 'Africa', 36.8065, 10.1815, 'A Mediterranean capital with ancient Carthage ruins nearby.'),
('loc_luxor', 'Luxor', 'Egypt', 'Africa', 25.6872, 32.6396, 'The world''s greatest open-air museum of ancient Egyptian temples.'),
('loc_zanzibar', 'Zanzibar City', 'Tanzania', 'Africa', -6.1659, 39.2026, 'A spice island paradise with Stone Town''s winding alleys.'),
('loc_melbourne', 'Melbourne', 'Australia', 'Oceania', -37.8136, 144.9631, 'Australia''s cultural capital, famous for coffee, street art, and sports.'),
('loc_brisbane', 'Brisbane', 'Australia', 'Oceania', -27.4698, 153.0251, 'A sunny river city, gateway to the Gold Coast and Great Barrier Reef.'),
('loc_perth', 'Perth', 'Australia', 'Oceania', -31.9505, 115.8605, 'The world''s most isolated city, with pristine beaches and wine regions.'),
('loc_wellington', 'Wellington', 'New Zealand', 'Oceania', -41.2866, 174.7756, 'The windy capital, home to Middle-earth movie magic.'),
('loc_suva', 'Suva', 'Fiji', 'Oceania', -18.1416, 178.4419, 'A tropical capital where colonial architecture meets Pacific island culture.');

-- ============================================================================
-- SEED DATA: 12 SUSPECTS
-- ============================================================================

INSERT INTO suspects (suspect_id, name, hair_color, eye_color, hobby, vehicle, favorite_food, distinguishing_feature) VALUES
('sus_boseman', 'Snowflake Boseman Montana', 'Silver-white', 'Ice blue', 'Data hoarding', 'Snowmobile', 'Frozen treats', 'Always leaves a trail of snowflakes'),
('sus_carmen', 'Carmen Sandiego-Inspired', 'Black', 'Brown', 'Stealing landmarks', 'Red convertible', 'Paella', 'Wears a signature red trench coat'),
('sus_byte', 'Binary Byte', 'Green (dyed)', 'Hazel', 'Hacking', 'Electric scooter', 'Ramen', 'Types furiously on a vintage keyboard'),
('sus_query', 'Query McSelectson', 'Bald', 'Gray', 'Writing SQL', 'Database-themed van', 'Table salt on everything', 'Mutters SELECT statements constantly'),
('sus_null', 'Null Pointer', 'Invisible (shaved)', 'Unknown', 'Crashing systems', 'Teleportation', 'Nothing', 'Causes exceptions wherever they go'),
('sus_pip', 'Pip Install', 'Purple', 'Green', 'Package management', 'Python-wrapped motorcycle', 'Snake fruit', 'Leaves dependency conflicts behind'),
('sus_cache', 'Cache Money', 'Gold', 'Golden', 'Collecting valuables', 'Armored cache truck', 'Expensive caviar', 'Everything they touch turns to cache'),
('sus_merge', 'Merge Conflict', 'Half black, half white', 'One blue, one brown', 'Creating chaos', 'Split-colored car', 'Mixed dishes', 'Leaves conflicting clues everywhere'),
('sus_docker', 'Docker Whale', 'Blue', 'Deep sea blue', 'Container shipping', 'Cargo ship', 'Seafood', 'Always travels in containers'),
('sus_git', 'Git Blame', 'Red', 'Shifty brown', 'Pointing fingers', 'Branch-hopping vehicle', 'Blame game cookies', 'Never takes responsibility'),
('sus_cloud', 'Cloudy McFloatface', 'Wispy white', 'Sky blue', 'Weather manipulation', 'Hot air balloon', 'Cloud-shaped candy', 'Floats into cities unannounced'),
('sus_api', 'API Endpoint', 'Rainbow (changes daily)', 'REST-ful gray', 'Making connections', 'Any vehicle that requests', 'JSON-formatted food', 'Responds differently to everyone');

-- ============================================================================
-- SEED DATA: DIFFICULTY LEVELS
-- ============================================================================

-- All difficulties have 144 hours (6 days like original Carmen Sandiego)
-- Difficulty names inspired by Snowflake, database, and AI concepts
INSERT INTO difficulty_levels (difficulty_id, name, description, time_budget_hours, clue_clarity, min_locations, max_locations, red_herrings, decoy_destinations) VALUES
(1, 'XS Warehouse', 'Extra Small challenge - clues served instantly', 144, 'obvious', 3, 4, 0, 2),
(2, 'Query Queued', 'Your investigation has been queued behind 3 others', 144, 'clear', 4, 5, 1, 4),
(3, 'Schema Drift', 'The clues keep changing when you are not looking', 144, 'cryptic', 5, 7, 2, 6),
(4, 'Cortex Hallucinating', 'The AI is confident but probably wrong', 144, 'very_cryptic', 7, 9, 3, 8),
(5, 'DROP PRODUCTION CASCADE', 'Everything is on fire. Good luck.', 144, 'riddle', 9, 12, 4, 10);

-- ============================================================================
-- SEED DATA: STOLEN ITEMS (50+ tech/Snowflake themed joke items)
-- ============================================================================

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

SELECT 'Deployment complete! Database DEMO_WITWISBM.GAME is ready.' as status;
