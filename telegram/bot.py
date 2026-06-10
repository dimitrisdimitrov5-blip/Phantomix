import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL", "http://localhost:8000")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👻 *Phantomix is online!*\n\n"
        "I'm your AI browser agent. Tell me what to do:\n\n"
        "📌 *Examples:*\n"
        "• Search for the latest AI news\n"
        "• Go to amazon.com and find AirPods\n"
        "• Book a table at a restaurant\n"
        "• Fill out a contact form on a website\n\n"
        "Just type your task and I'll handle it! 🚀",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👻 *Phantomix Commands:*\n\n"
        "/start - Start Phantomix\n"
        "/help - Show this help\n"
        "/clear - Clear conversation memory\n"
        "/status - Check if agent is running\n\n"
        "Or just type any task naturally!",
        parse_mode="Markdown"
    )

async def clear_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiohttp.ClientSession() as session:
        async with session.delete(f"{API_URL}/memory") as resp:
            if resp.status == 200:
                await update.message.reply_text("🧹 Memory cleared! Fresh start.")
            else:
                await update.message.reply_text("❌ Failed to clear memory.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_URL}/health") as resp:
                if resp.status == 200:
                    await update.message.reply_text("✅ Phantomix is running perfectly!")
                else:
                    await update.message.reply_text("⚠️ Agent is having issues.")
        except:
            await update.message.reply_text("❌ Cannot reach the agent.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = update.message.text
    await update.message.reply_text("👻 On it! Give me a moment...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_URL}/task",
                json={"task": task},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                data = await resp.json()
                if data.get("status") == "success":
                    result = data.get("result", "Done!")
                    if len(result) > 4096:
                        result = result[:4000] + "\n\n... _(truncated)_"
                    await update.message.reply_text(
                        f"✅ *Done!*\n\n{result}",
                        parse_mode="Markdown"
                    )
                else:
                    await update.message.reply_text("❌ Something went wrong. Try again.")
        except asyncio.TimeoutError:
            await update.message.reply_text("⏱ Task timed out. Try a simpler task.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_memory))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("👻 Phantomix Telegram bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
