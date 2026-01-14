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
-- AI Complete function rates - Effective January 13, 2026
INSERT INTO cortex_credit_rates (model_name, credits_per_million_input_tokens, credits_per_million_output_tokens, model_provider, notes) VALUES

-- Anthropic Claude models
('claude-3-5-sonnet', 1.50, 7.50, 'Anthropic', 'Claude 3.5 Sonnet'),
('claude-3-7-sonnet', 1.50, 7.50, 'Anthropic', 'Claude 3.7 Sonnet'),
('claude-4-sonnet', 1.50, 7.50, 'Anthropic', 'Claude 4 Sonnet'),
('claude-4-opus', 7.50, 37.50, 'Anthropic', 'Claude 4 Opus'),
('claude-haiku-4-5', 0.55, 2.75, 'Anthropic', 'Claude Haiku 4.5'),
('claude-opus-4-5', 2.75, 13.75, 'Anthropic', 'Claude Opus 4.5'),
('claude-sonnet-4-5', 1.65, 8.25, 'Anthropic', 'Claude Sonnet 4.5'),

-- DeepSeek models
('deepseek-r1', 0.68, 2.70, 'DeepSeek', 'DeepSeek R1'),

-- Google Gemini models
('gemini-2-5-flash', 0.15, 1.25, 'Google', 'Gemini 2.5 Flash'),
('gemini-2-5-flash-lite', 0.05, 0.20, 'Google', 'Gemini 2.5 Flash Lite'),
('gemini-3-pro', 1.00, 6.00, 'Google', 'Gemini 3 Pro'),

-- Meta Llama models
('llama3.1-405b', 1.20, 1.20, 'Meta', 'Llama 3.1 405B'),
('llama3.1-70b', 0.36, 0.36, 'Meta', 'Llama 3.1 70B'),
('llama3.1-8b', 0.11, 0.11, 'Meta', 'Llama 3.1 8B'),
('llama3.3-70b', 0.36, 0.36, 'Meta', 'Llama 3.3 70B'),
('llama4-maverick', 0.12, 0.49, 'Meta', 'Llama 4 Maverick'),
('llama4-scout', 0.09, 0.33, 'Meta', 'Llama 4 Scout'),

-- Mistral models
('mistral-large2', 1.00, 3.00, 'Mistral AI', 'Mistral Large 2'),
('mistral-7b', 0.08, 0.10, 'Mistral AI', 'Mistral 7B'),
('mixtral-8x7b', 0.23, 0.35, 'Mistral AI', 'Mixtral 8x7B'),
('pixtral-large', 1.00, 3.00, 'Mistral AI', 'Pixtral Large'),

-- OpenAI models
('openai-gpt-4.1', 1.00, 4.00, 'OpenAI', 'GPT-4.1'),
('openai-gpt-5', 0.69, 5.50, 'OpenAI', 'GPT-5'),
('openai-gpt-5-chat', 0.63, 5.00, 'OpenAI', 'GPT-5 Chat'),
('openai-gpt-5-mini', 0.14, 1.10, 'OpenAI', 'GPT-5 Mini'),
('openai-gpt-5-nano', 0.03, 0.22, 'OpenAI', 'GPT-5 Nano'),
('openai-gpt-5.1', 0.69, 5.50, 'OpenAI', 'GPT-5.1'),
('openai-gpt-5.2', 0.97, 7.70, 'OpenAI', 'GPT-5.2'),
('openai-gpt-oss-120b', 0.08, 0.30, 'OpenAI', 'GPT OSS 120B'),
('openai-gpt-oss-20b', 0.04, 0.15, 'OpenAI', 'GPT OSS 20B'),
('openai-o4-mini', 0.55, 2.20, 'OpenAI', 'O4 Mini'),

-- Snowflake models
('snowflake-arctic', 0.84, 0.84, 'Snowflake', 'Snowflake Arctic'),
('snowflake-llama-3.1-405b', 0.96, 0.96, 'Snowflake', 'Snowflake Llama 3.1 405B'),
('snowflake-llama-3.3-70b', 0.29, 0.29, 'Snowflake', 'Snowflake Llama 3.3 70B');
