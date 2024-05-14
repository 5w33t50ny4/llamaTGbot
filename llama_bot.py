from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq  # Ensure Groq API is properly integrated

# API key and bot token
client = Groq(api_key="")
TOKEN = "" # tg api token 

# Dictionary to store each user's message history
user_messages = {}

# Create the application instance
app = ApplicationBuilder().token(TOKEN).build()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat_id  # User or group ID
    if user_id not in user_messages:
        user_messages[user_id] = []

    # Add user message to their history
    user_messages[user_id].append({"role": 'user', "content": update.message.text})

    # Limit message history to the last 100 messages
    if len(user_messages[user_id]) > 100:
        user_messages[user_id] = user_messages[user_id][-100:]

    # Send message to Groq server for a response
    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=user_messages[user_id],
            temperature=0
        )
    except Exception as e:
        print("Failed to get response from Groq: ", str(e))
        await update.message.reply_text("Error processing your message.")
        return

    # Send bot's response to the user
    await update.message.reply_text(response.choices[0].message.content)

    # Save bot's response in the user's message history
    user_messages[user_id].append({"role": 'assistant', "content": response.choices[0].message.content})

# Register message handler
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Run the bot
app.run_polling()
