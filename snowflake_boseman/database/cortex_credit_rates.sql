-- Snowflake Cortex LLM Credit Consumption Rates
-- Source: https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf (Table 6a)
-- Effective: January 13, 2026
-- Credits per 1 million tokens

CREATE OR REPLACE TABLE cortex_credit_rates (
    model_name VARCHAR PRIMARY KEY,
    credits_per_million_input_tokens FLOAT NOT NULL,
    credits_per_million_output_tokens FLOAT NOT NULL,
    model_provider VARCHAR,
    notes VARCHAR,
    effective_date DATE DEFAULT '2026-01-13'
);

-- Insert credit rates for Cortex LLM models from Table 6(a)
-- Values from Snowflake Service Consumption Table effective January 13, 2026
INSERT INTO cortex_credit_rates (model_name, credits_per_million_input_tokens, credits_per_million_output_tokens, model_provider, notes) VALUES

-- Anthropic Claude models
('claude-4-sonnet', 3.14, 15.69, 'Anthropic', 'Claude 4 Sonnet'),
('claude-4-5-sonnet', 3.45, 17.26, 'Anthropic', 'Claude 4.5 Sonnet'),
('claude-haiku-4-5', 1.15, 5.75, 'Anthropic', 'Claude Haiku 4.5'),

-- Mistral models
('mistral-large2', 2.09, 6.28, 'Mistral AI', 'Mistral Large 2'),

-- OpenAI models
('openai-gpt-4.1', 2.30, 9.21, 'OpenAI', 'GPT-4.1'),
('openai-gpt-5', 1.44, 11.51, 'OpenAI', 'GPT-5'),

-- Fine-tuning models from Table 6(g) - inference rates
('llama3.1-70b', 2.42, 2.42, 'Meta', 'Llama 3.1 70B - Fine-tuning inference rate'),
('llama3.1-8b', 0.38, 0.38, 'Meta', 'Llama 3.1 8B - Fine-tuning inference rate'),
('mistral-7b', 0.24, 0.24, 'Mistral AI', 'Mistral 7B - Fine-tuning inference rate'),
('mixtral-8x7b', 0.44, 0.44, 'Mistral AI', 'Mixtral 8x7B - Fine-tuning inference rate'),
('llama3-70b', 2.42, 2.42, 'Meta', 'Llama 3 70B - Legacy fine-tuning inference rate'),
('llama3-8b', 0.38, 0.38, 'Meta', 'Llama 3 8B - Legacy fine-tuning inference rate');

-- NOTE: Some models from our AVAILABLE_AI_MODELS list may not be in Table 6(a)
-- Verify against current documentation for: llama3.1-405b, llama3.3-70b, llama4-maverick, 
-- llama4-scout, mistral-large, deepseek-r1, snowflake-arctic, snowflake-llama-3.1-405b, 
-- snowflake-llama-3.3-70b, claude-3-5-sonnet, claude-3-7-sonnet, claude-4-opus, openai-o4-mini
