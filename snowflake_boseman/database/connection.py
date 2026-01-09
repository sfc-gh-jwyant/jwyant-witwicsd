"""Snowflake connection handling for Streamlit in Snowflake."""

import streamlit as st
from typing import Any

# Cortex AI safety prompt for all AI-generated content
SAFETY_SYSTEM_PROMPT = """
You are a content generator for a family-friendly geography education game 
similar to "Where in the World is Carmen Sandiego?" 

CONTENT GUIDELINES:
- All content must be safe for work and appropriate for all ages
- Focus on geography, culture, landmarks, history, and travel
- No violence, adult themes, controversial politics, or sensitive topics
- Keep descriptions educational, fun, and engaging
- Use playful detective/mystery language appropriate for the game theme
- Avoid stereotypes; represent cultures respectfully and accurately
"""


def get_connection():
    """Get Snowflake connection from Streamlit."""
    return st.connection("snowflake")


def get_session():
    """Get active Snowpark session."""
    conn = get_connection()
    return conn.session()


def execute_query(query: str) -> list[dict[str, Any]]:
    """Execute a SQL query and return results as list of dicts."""
    session = get_session()
    result = session.sql(query).collect()
    return [row.as_dict() for row in result]


def execute_write(query: str) -> None:
    """Execute a write query (INSERT, UPDATE, DELETE, MERGE)."""
    session = get_session()
    session.sql(query).collect()


def safe_complete(prompt: str, model: str = "llama3.1-8b") -> str:
    """
    Generate content using Cortex AI with safety guardrails.
    
    Uses the safety system prompt and Cortex Guard for content filtering.
    """
    session = get_session()
    full_prompt = f"{SAFETY_SYSTEM_PROMPT}\n\n{prompt}"
    
    # Escape the prompt for SQL
    escaped_prompt = full_prompt.replace("'", "''").replace("$", "\\$")
    
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            '{model}',
            $prompt${escaped_prompt}$prompt$,
            {{'guard': TRUE}}
        ) as response
    """).collect()
    
    if result:
        return result[0]['RESPONSE']
    return ""


def get_current_user() -> dict[str, str]:
    """Get current Snowflake user context."""
    session = get_session()
    result = session.sql("""
        SELECT 
            CURRENT_USER() as username,
            CURRENT_ROLE() as role,
            CURRENT_ACCOUNT() as account
    """).collect()[0]
    
    return {
        "username": result['USERNAME'],
        "role": result['ROLE'],
        "account": result['ACCOUNT']
    }

