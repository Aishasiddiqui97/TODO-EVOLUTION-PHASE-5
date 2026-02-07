# OpenRouter Setup Guide

## What is OpenRouter?

OpenRouter provides unified access to multiple LLM models through a single OpenAI-compatible API. This gives you:

✅ **Access to multiple models** - GPT-4, Claude, Gemini, Llama, and more
✅ **Lower costs** - Competitive pricing across providers
✅ **Fallback options** - Switch models if one is unavailable
✅ **No vendor lock-in** - Easy to switch between models

## Getting Started

### 1. Create an OpenRouter Account

Visit: https://openrouter.ai/

- Sign up with Google, GitHub, or email
- Free credits available for testing

### 2. Get Your API Key

1. Go to: https://openrouter.ai/keys
2. Click "Create Key"
3. Copy your API key (starts with `sk-or-v1-`)
4. Keep it secure!

### 3. Add Credits (Optional)

- Go to: https://openrouter.ai/credits
- Add credits via credit card or crypto
- $5 minimum, credits never expire
- Free tier available for testing

## Model Selection

### Recommended Models for Task Management

#### Best Quality (Higher Cost)
```cmd
set OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```
- Best reasoning and function calling
- ~$0.01 per 1K tokens (input)
- Recommended for production

#### Balanced (Medium Cost)
```cmd
set OPENROUTER_MODEL=anthropic/claude-3-sonnet
```
- Excellent reasoning, good speed
- ~$0.003 per 1K tokens (input)
- Great for most use cases

#### Fast & Cheap (Lower Cost)
```cmd
set OPENROUTER_MODEL=openai/gpt-3.5-turbo
```
- Fast responses, lower cost
- ~$0.0005 per 1K tokens (input)
- Good for development/testing

#### Open Source (Lowest Cost)
```cmd
set OPENROUTER_MODEL=meta-llama/llama-3-70b-instruct
```
- Open source, very affordable
- ~$0.0007 per 1K tokens (input)
- Good performance for the price

### View All Models

Browse all available models: https://openrouter.ai/models

Filter by:
- **Context length** (how much text it can process)
- **Price** (cost per token)
- **Modality** (text, vision, etc.)
- **Provider** (OpenAI, Anthropic, Google, etc.)

## Configuration for This Project

### Environment Variables

**Required:**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Optional (defaults to GPT-4 Turbo):**
```cmd
set OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

### How It Works

The application uses the OpenAI Python SDK but points it to OpenRouter's API:

```python
openai.api_key = "your-openrouter-key"
openai.api_base = "https://openrouter.ai/api/v1"
```

This makes it 100% compatible with OpenAI's API while giving you access to multiple models.

## Cost Estimation

### Typical Usage (per conversation)

**Average conversation:**
- Input: ~500 tokens (your message + context)
- Output: ~200 tokens (AI response)

**Cost per conversation:**
- GPT-4 Turbo: ~$0.007 ($7 per 1000 conversations)
- Claude 3 Sonnet: ~$0.002 ($2 per 1000 conversations)
- GPT-3.5 Turbo: ~$0.0004 ($0.40 per 1000 conversations)
- Llama 3 70B: ~$0.0005 ($0.50 per 1000 conversations)

**$5 credit gets you:**
- ~700 conversations with GPT-4 Turbo
- ~2,500 conversations with Claude 3 Sonnet
- ~12,500 conversations with GPT-3.5 Turbo
- ~10,000 conversations with Llama 3 70B

## Features Supported

✅ **Function Calling** - All recommended models support tool/function calling
✅ **Streaming** - Real-time response streaming (if enabled)
✅ **Context Windows** - Up to 128K tokens depending on model
✅ **JSON Mode** - Structured output support
✅ **Vision** - Some models support image input

## Troubleshooting

### "Invalid API key"
- Check your key starts with `sk-or-v1-`
- Verify it's set correctly: `echo %OPENROUTER_API_KEY%`
- Make sure you copied the full key

### "Insufficient credits"
- Add credits at: https://openrouter.ai/credits
- Check your balance in the dashboard
- Free tier has daily limits

### "Model not found"
- Check model name is correct: https://openrouter.ai/models
- Some models require special access
- Try a different model

### "Rate limit exceeded"
- Free tier has rate limits
- Add credits to increase limits
- Wait a few minutes and retry

### Function calling not working
- Not all models support function calling
- Use recommended models (GPT-4, Claude 3, GPT-3.5)
- Check model capabilities on OpenRouter

## Monitoring Usage

### View Your Usage

1. Go to: https://openrouter.ai/activity
2. See all API calls, costs, and models used
3. Filter by date, model, or status
4. Export usage data

### Set Spending Limits

1. Go to: https://openrouter.ai/settings
2. Set daily/monthly spending limits
3. Get alerts when approaching limits
4. Prevent unexpected charges

## Switching Back to OpenAI

If you want to use OpenAI directly instead:

1. Change environment variable:
```cmd
set OPENAI_API_KEY=sk-your-openai-key
```

2. Update `backend/src/services/chat-api/ai/agent.py`:
```python
# Change this:
self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

# To this:
self.api_key = api_key or os.getenv("OPENAI_API_KEY")
# Remove the api_base line
```

## Benefits of OpenRouter

### 1. Cost Savings
- Compare prices across providers
- Use cheaper models for simple tasks
- Use expensive models only when needed

### 2. Reliability
- Automatic fallback to other models
- No single point of failure
- Better uptime

### 3. Flexibility
- Try different models easily
- Switch models without code changes
- A/B test model performance

### 4. Transparency
- See exact costs per request
- Monitor usage in real-time
- No surprise bills

## Support

- **Documentation**: https://openrouter.ai/docs
- **Discord**: https://discord.gg/openrouter
- **Email**: support@openrouter.ai
- **Status**: https://status.openrouter.ai

## Summary

OpenRouter gives you access to the best AI models at competitive prices with a single API. Perfect for:

✅ Development and testing (use cheap models)
✅ Production (use best models with fallbacks)
✅ Cost optimization (switch models based on task)
✅ Avoiding vendor lock-in (easy to switch providers)

**Get started now:** https://openrouter.ai/keys
