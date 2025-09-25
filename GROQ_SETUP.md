# Groq API Setup (Fallback)

This application now includes automatic fallback to Groq when Gemini API quota is exceeded.

## Getting a Groq API Key

1. **Visit Groq Console**: Go to https://console.groq.com/
2. **Sign up/Login**: Create an account or login
3. **Get API Key**: Navigate to API Keys section and create a new key
4. **Copy the key**: Copy your API key

## Configuration

1. **Update .env file**: Add your Groq API key to the `.env` file:
   ```
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

2. **Restart the application**: The fallback system will automatically detect and use Groq

## How the Fallback Works

- **Primary**: Gemini API (50 requests/day free)
- **Fallback**: Groq API (1,000 requests/day free)
- **Automatic switching**: When Gemini quota is exceeded, it automatically switches to Groq
- **Status monitoring**: Check `/status` endpoint to see current provider

## Benefits

- ✅ **Higher request limits**: 1,000 requests/day with Groq vs 50 with Gemini
- ✅ **Automatic failover**: No manual intervention needed
- ✅ **Seamless experience**: Users don't notice the switch
- ✅ **Cost effective**: Both APIs have generous free tiers

## Models Used

- **Gemini**: gemini-1.5-flash (primary)
- **Groq**: llama-3.1-8b-instant (fallback)

Both models provide high-quality bias detection with similar accuracy.
