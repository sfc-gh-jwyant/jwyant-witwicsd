-- Snowflake Cortex LLM Credit Consumption Rates
-- Source: https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf (Table 6a)
-- Credits per 1 million tokens

CREATE OR REPLACE TABLE cortex_credit_rates (
    model_name VARCHAR PRIMARY KEY,
    credits_per_million_input_tokens FLOAT NOT NULL,
    credits_per_million_output_tokens FLOAT NOT NULL,
    model_provider VARCHAR,
    notes VARCHAR,
    last_updated DATE DEFAULT CURRENT_DATE()
);

-- Insert credit rates for Cortex LLM models
-- Note: Rates are subject to change - verify against current Snowflake documentation
INSERT INTO cortex_credit_rates (model_name, credits_per_million_input_tokens, credits_per_million_output_tokens, model_provider, notes) VALUES
-- Llama models
('llama3.1-8b', 0.19, 0.19, 'Meta', 'Llama 3.1 8B parameter model'),
('llama3.1-70b', 1.21, 1.21, 'Meta', 'Llama 3.1 70B parameter model'),
('llama3.1-405b', 3.00, 3.00, 'Meta', 'Llama 3.1 405B parameter model'),
('llama3.3-70b', 1.21, 1.21, 'Meta', 'Llama 3.3 70B parameter model'),
('llama3-8b', 0.19, 0.19, 'Meta', 'Llama 3 8B parameter model'),
('llama3-70b', 1.21, 1.21, 'Meta', 'Llama 3 70B parameter model'),
('llama4-maverick', 0.48, 1.44, 'Meta', 'Llama 4 Maverick model'),
('llama4-scout', 0.24, 0.96, 'Meta', 'Llama 4 Scout model'),

-- Snowflake models
('snowflake-arctic', 0.84, 1.05, 'Snowflake', 'Snowflake Arctic model'),
('snowflake-llama-3.1-405b', 3.00, 3.00, 'Snowflake', 'Snowflake-hosted Llama 3.1 405B'),
('snowflake-llama-3.3-70b', 1.21, 1.21, 'Snowflake', 'Snowflake-hosted Llama 3.3 70B'),

-- Mistral models
('mistral-7b', 0.12, 0.12, 'Mistral AI', 'Mistral 7B parameter model'),
('mistral-large', 5.10, 15.30, 'Mistral AI', 'Mistral Large model'),
('mistral-large2', 3.00, 9.00, 'Mistral AI', 'Mistral Large 2 model'),
('mixtral-8x7b', 0.22, 0.22, 'Mistral AI', 'Mixtral 8x7B MoE model'),

-- Anthropic Claude models (if available in your region)
('claude-3-5-sonnet', 3.00, 15.00, 'Anthropic', 'Claude 3.5 Sonnet'),
('claude-3-7-sonnet', 3.00, 15.00, 'Anthropic', 'Claude 3.7 Sonnet'),
('claude-4-sonnet', 3.00, 15.00, 'Anthropic', 'Claude 4 Sonnet'),
('claude-4-opus', 15.00, 75.00, 'Anthropic', 'Claude 4 Opus - highest capability'),

-- OpenAI models (if available in your region)
('openai-gpt-4.1', 2.00, 8.00, 'OpenAI', 'GPT-4.1 model'),
('openai-o4-mini', 1.10, 4.40, 'OpenAI', 'GPT-4o mini model'),

-- DeepSeek models
('deepseek-r1', 0.55, 2.19, 'DeepSeek', 'DeepSeek R1 reasoning model');

-- Create a view to calculate estimated costs for the game
CREATE OR REPLACE VIEW v_ai_cost_estimates AS
SELECT 
    p.snowflake_user,
    p.ai_prompt_count,
    p.ai_token_count,
    ROUND(p.ai_token_count / 1000000.0 * 1.21, 4) as estimated_credits_llama70b,
    ROUND(p.ai_token_count / 1000000.0 * 0.19, 4) as estimated_credits_llama8b
FROM players p
ORDER BY p.ai_token_count DESC;

-- View to show cost breakdown by model
CREATE OR REPLACE VIEW v_cortex_model_costs AS
SELECT 
    model_name,
    model_provider,
    credits_per_million_input_tokens as input_credits_per_1m,
    credits_per_million_output_tokens as output_credits_per_1m,
    (credits_per_million_input_tokens + credits_per_million_output_tokens) / 2 as avg_credits_per_1m,
    notes
FROM cortex_credit_rates
ORDER BY avg_credits_per_1m;
