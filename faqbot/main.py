import json
import os
import requests
import asyncio
from telegram import Message, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    ApplicationBuilder,
    MessageHandler,
    filters,
)


# Load FAQs from JSON
def load_faqs():
    return requests.get(os.environ.get("FAQ_JSON_URI")).json()


FAQS = load_faqs()


# Show the main FAQ menu
async def faq_menu(update: Update, context: CallbackContext) -> None:
    print("faq_menu")
    if update.message and update.message.chat.type != "private":
        print("faq_menu in group")

        keyboard = [
            [
                InlineKeyboardButton(
                    "شروع چت با ربات سوالات متداول", url="https://t.me/nasnetfaqbot"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = f"با استفاده از این ربات میتونی به سوال های متداول دسترسی داشته باشی @nasnetfaqbot"

        message = await update.message.reply_text(
            welcome_message, reply_markup=reply_markup
        )
        asyncio.create_task(delete_message(message=message, delay=20))
        return

    keyboard = [
        [InlineKeyboardButton(key.replace("_", " ").title(), callback_data=key)]
        for key in FAQS.keys()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            " یکی از سوالات متداول را انتخاب کنید:", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            " یکی از سوالات متداول را انتخاب کنید:", reply_markup=reply_markup
        )


async def display_faq(update: Update, context: CallbackContext) -> None:
    print("display_faq")
    query = update.callback_query
    await query.answer()
    answer = FAQS.get(query.data, "پاسخی برای سوال شما پیدا نشد.")

    keyboard = [[InlineKeyboardButton("بازگشت به منو", callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=answer, reply_markup=reply_markup)


async def delete_message(message: Message, delay=60):
    await asyncio.sleep(delay)
    print("delete_message")
    await message.delete()


# Handle new users joining the group
async def welcome_new_user(update: Update, context: CallbackContext) -> None:
    print("welcome_new_user")
    for member in update.message.new_chat_members:
        keyboard = [
            [
                InlineKeyboardButton(
                    "شروع چت با ربات سوالات متداول", url="https://t.me/nasnetfaqbot"
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_message = (
            f"سلام @{member.username} , خوش اومدی! "
            f"با استفاده از این ربات میتونی به سوال های متداول دسترسی داشته باشی:\n@nasnetfaqbot"
        )

        message = await update.message.reply_text(
            welcome_message, reply_markup=reply_markup
        )
        asyncio.create_task(delete_message(message=message, delay=60))


def main():
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler(["faq", "start"], faq_menu))
    app.add_handler(CallbackQueryHandler(display_faq, pattern="^(?!back_to_menu$).*"))
    app.add_handler(CallbackQueryHandler(faq_menu, pattern="^back_to_menu$"))
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_user)
    )

    app.run_polling(timeout=20)


if __name__ == "__main__":
    main()
