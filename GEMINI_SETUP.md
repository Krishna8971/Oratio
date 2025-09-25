# Gemini API Setup Guide

## Getting Your API Key

1. **Visit Google AI Studio**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Choose "Create API Key in new project" or select existing project
   - Copy the generated API key

3. **Set Environment Variable**
   
   **Windows (PowerShell):**
   ```powershell
   $env:GEMINI_API_KEY="your-api-key-here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set GEMINI_API_KEY=your-api-key-here
   ```
   
   **Linux/macOS:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. **Verify Setup**
   ```bash
   python test_gemini.py
   ```

## Environment Variables

You can also create a `.env` file in your project root:

```env
GEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-pro
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=oratio
```

## Features

The Gemini API provides:

- **Comprehensive Bias Detection**: Detects gender, racial, ageist, ableist, religious, and socioeconomic bias
- **Contextual Analysis**: Understands nuanced language and context
- **Neutral Suggestions**: Provides inclusive alternatives for biased language
- **Multiple Bias Types**: Identifies various forms of discrimination and stereotyping
- **High Accuracy**: Advanced AI model trained on diverse datasets

## API Limits

- Free tier: 15 requests per minute
- Paid tier: Higher limits available
- Check [Google AI Studio pricing](https://ai.google.dev/pricing) for current rates

## Troubleshooting

**Error: "GEMINI_API_KEY not found"**
- Make sure you've set the environment variable correctly
- Restart your terminal/IDE after setting the variable

**Error: "API key invalid"**
- Verify your API key is correct
- Check if the API key has the necessary permissions

**Error: "Quota exceeded"**
- You've hit the rate limit
- Wait a minute or upgrade to a paid plan
