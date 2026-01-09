# Where in the World is Snowflake Boseman Montana? ❄️🔍

A geography mystery adventure game inspired by the classic "Where in the World is Carmen Sandiego?" - built as a Streamlit in Snowflake application.

## 🎮 Game Overview

Track the elusive **Snowflake Boseman Montana** across the globe! Gather clues, follow the trail, and arrest the suspect before time runs out.

### Features

- **100 real-world cities** across all continents with famous landmarks
- **12 unique suspects** with distinctive traits (database-themed villains!)
- **5 difficulty levels** (from "SELECT * FROM clues" to "Little Bobby Tables")
- **Dynamic clue generation** powered by Snowflake Cortex AI
- **1992 Deluxe Edition inspired UI** with retro detective aesthetic
- **Leaderboard** with high scores based on completion time
- **Game telemetry** for analytics and player insights

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              Streamlit in Snowflake                 │
│  ┌────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │   Game UI  │  │ Game Loop    │  │  Session   │  │
│  │            │→ │ Controller   │→ │   State    │  │
│  └────────────┘  └──────────────┘  └────────────┘  │
└─────────────────────────┬───────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────┐
│                 Snowflake Database                   │
│  ┌────────────────┐  ┌───────────────────────────┐  │
│  │ Hybrid Tables  │  │    Snowflake Cortex AI    │  │
│  │ (Game State)   │  │   (Dynamic Clue Gen)      │  │
│  └────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
snowflake_boseman/
├── streamlit_app.py          # Main Streamlit entry point
├── requirements.txt          # Dependencies
├── models/                   # Data models
│   ├── location.py          # Location & Landmark classes
│   ├── suspect.py           # Suspect class
│   ├── clue.py              # Clue class with types
│   ├── player.py            # Player with rank progression
│   ├── case.py              # Case & CaseProgress
│   └── time_manager.py      # Time/difficulty management
├── game/                     # Game logic
│   ├── game_controller.py   # Main game orchestration
│   ├── case_generator.py    # New case creation
│   ├── clue_generator.py    # Cortex AI clue generation
│   └── telemetry.py         # Event tracking
├── database/                 # Database layer
│   ├── connection.py        # Snowflake connection
│   ├── schema.sql           # Hybrid table DDL
│   └── seed_data.sql        # Reference data
├── ui/                       # User interface
│   ├── styles.py            # 1992 theme CSS
│   ├── pages/               # Page components
│   │   ├── main_menu.py
│   │   ├── investigation.py
│   │   ├── travel.py
│   │   ├── case_result.py
│   │   └── high_scores.py
│   └── components/          # Reusable UI components
│       ├── art_placeholder.py
│       ├── clue_notebook.py
│       ├── suspect_dossier.py
│       └── world_map.py
├── assets/                   # Art placeholders
│   ├── locations/
│   ├── landmarks/
│   ├── suspects/
│   └── clues/
└── data/
    └── cities.json          # City reference data
```

## 🚀 Deployment to Snowflake

### 1. Create Database Objects

Run the schema creation script in Snowflake:

```sql
-- Create a database for the game
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_BOSEMAN_GAME;
USE DATABASE SNOWFLAKE_BOSEMAN_GAME;
CREATE SCHEMA IF NOT EXISTS GAME;
USE SCHEMA GAME;

-- Run the schema.sql file to create Hybrid Tables
-- Run the seed_data.sql file to populate reference data
```

### 2. Deploy Streamlit App

In Snowflake, create a new Streamlit app:

1. Go to **Streamlit** in Snowsight
2. Click **+ Streamlit App**
3. Upload the contents of `snowflake_boseman/` directory
4. Set `streamlit_app.py` as the entry point
5. Configure warehouse and database access

### 3. Grant Permissions

```sql
-- Grant Cortex AI access
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE <your_role>;

-- Grant table access
GRANT ALL ON ALL TABLES IN SCHEMA GAME TO ROLE <your_role>;
```

## 🎯 Difficulty Levels

| Level | Name | Time | Clues | Red Herrings |
|-------|------|------|-------|--------------|
| 1 | SELECT * FROM clues | 72 hrs | Very obvious | 0 |
| 2 | WITH (NOLOCK) | 48 hrs | Clear | 1 |
| 3 | Foreign Key Violation | 36 hrs | Cryptic | 2 |
| 4 | Deadlock Victim | 24 hrs | Very cryptic | 3 |
| 5 | Little Bobby Tables | 12 hrs | Riddles only | 4 |

## 🏆 Scoring

Score = (Time Bonus + Efficiency Bonus) × Difficulty Multiplier

- **Time Bonus**: (Budget - Used) × 100 points per hour saved
- **Efficiency Bonus**: Fewer locations visited = bonus points
- **Difficulty Multiplier**: 1× to 16× based on level

## 📊 Telemetry & Analytics

The game tracks:
- Daily active users
- Win rate by difficulty
- Friction points (where players get stuck)
- Player progression and rank ups
- Session duration and engagement

## 🎨 Art Assets

The game includes placeholders for:
- **Location Art** (300×400px) - City scenes as backgrounds
- **Landmark Art** (200×150px) - Famous landmarks
- **Suspect Art** (150×200px) - Character mugshots
- **Clue Art** (100×100px) - Clue icons

Replace placeholder images in the `assets/` folder with actual art.

## 🔒 Content Safety

All AI-generated content uses:
- **System prompt** enforcing family-friendly content
- **Cortex Guard** for additional content filtering
- Focus on geography, culture, and education

## 📜 License

Inspired by Carmen Sandiego. For educational and entertainment purposes.

Built with ❄️ Snowflake, 🐍 Python, and 🎈 Streamlit

