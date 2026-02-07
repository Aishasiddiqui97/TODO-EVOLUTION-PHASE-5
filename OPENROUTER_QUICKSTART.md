# 🎯 OpenRouter Quick Start

## Get Running in 3 Steps

### 1️⃣ Get Your API Key
Visit: **https://openrouter.ai/keys**
- Sign up (free credits available)
- Create an API key
- Copy it (starts with `sk-or-v1-`)

### 2️⃣ Set Environment Variable
Open Command Prompt:
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

**Optional - Choose a model:**
```cmd
set OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

### 3️⃣ Run the Application
```cmd
cd E:\Python.py\Hackaton 2(1)
START.bat
```

Wait 30 seconds, then open: **http://localhost:3000**

---

## Popular Models

| Model | Cost per 1K msgs | Best For |
|-------|------------------|----------|
| `openai/gpt-4-turbo-preview` | $7 | Production (default) |
| `anthropic/claude-3-sonnet` | $2 | Balanced quality/cost |
| `openai/gpt-3.5-turbo` | $0.40 | Development/testing |
| `meta-llama/llama-3-70b-instruct` | $0.50 | Open source option |

See all: **https://openrouter.ai/models**

---

## Test It Works

Once running, try in the chat interface:
> "Create a task to review proposal by Friday"

The AI will create the task for you!

---

## Troubleshooting

**"OPENROUTER_API_KEY not set"**
- Set the variable in the same Command Prompt window
- Get key from: https://openrouter.ai/keys

**"Invalid API key"**
- Check it starts with `sk-or-v1-`
- No extra spaces when copying

**"Insufficient credits"**
- Add credits at: https://openrouter.ai/credits
- Free tier available for testing

**Backend won't start**
- Make sure Docker Desktop is running
- Run `dapr init` first

---

## What You Get

✅ Access to 100+ AI models
✅ Lower costs than direct OpenAI
✅ No vendor lock-in
✅ Easy model switching
✅ Transparent pricing

---

## Full Documentation

- **OPENROUTER_SETUP.md** - Complete guide
- **OPENROUTER_CONVERSION_COMPLETE.md** - What changed
- **READY_TO_RUN.md** - Detailed setup

---

**Ready?** Get your key and run START.bat! 🚀
