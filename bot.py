import json
import os
import logging
import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

TOKEN = "8675321937:AAEC0bcHhO59t6SwlqvgXstd2FCNFk7CZcg"
DATA_FILE = "user_data.json"

MAIN_MENU, GPA_ENTER, UNIT_CATEGORY, UNIT_FROM, UNIT_TO, UNIT_VALUE, DEADLINE_MENU, DEADLINE_ADD_TITLE, DEADLINE_ADD_DATE, DEADLINE_REMOVE, TODO_MENU, TODO_ADD, TODO_COMPLETE, FLASH_MENU, FLASH_ADD_Q, FLASH_ADD_A, FLASH_QUIZ = range(17)

MAIN_KB = ReplyKeyboardMarkup([["🎓 GPA Calculator", "📏 Unit Converter"], ["📅 Deadline Tracker", "✅ To-Do List"], ["🃏 Flashcards", "❓ Help"]], resize_keyboard=True)
BACK_KB = ReplyKeyboardMarkup([["🔙 Back"]], resize_keyboard=True)
DEADLINE_KB = ReplyKeyboardMarkup([["➕ Add Deadline", "📋 View Deadlines"], ["❌ Remove Deadline", "🔙 Back"]], resize_keyboard=True)
TODO_KB = ReplyKeyboardMarkup([["➕ Add Task", "📋 View Tasks"], ["✅ Complete Task", "❌ Remove Task"], ["🔙 Back"]], resize_keyboard=True)
FLASH_KB = ReplyKeyboardMarkup([["➕ Add Card", "🧠 Quiz Me!"], ["📋 View Cards", "🗑 Clear Cards"], ["🔙 Back"]], resize_keyboard=True)

GRADE_MAP = {
    "A": 4.0, "A-": 3.67,
    "B+": 3.33, "B": 3.0, "B-": 2.67,
    "C+": 2.33, "C": 2.0, "C-": 1.67,
    "D+": 1.33, "D": 1.0, "D-": 0.67,
    "F": 0.0
}

UNIT_OPTIONS = {
    "📏 Length": {"units": ["km", "m", "cm", "mm", "mile", "yard", "foot", "inch"], "to_base": {"km": 1000, "m": 1, "cm": 0.01, "mm": 0.001, "mile": 1609.344, "yard": 0.9144, "foot": 0.3048, "inch": 0.0254}},
    "⚖️ Weight": {"units": ["kg", "g", "mg", "lb", "oz", "ton"], "to_base": {"kg": 1000, "g": 1, "mg": 0.001, "lb": 453.592, "oz": 28.3495, "ton": 1000000}},
    "🌡 Temperature": {"units": ["C", "F", "K"], "to_base": None}
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, uid):
    if uid not in data:
        data[uid] = {"deadlines": [], "todos": [], "flashcards": []}
    return data[uid]

def calculate_gpa(entries):
    total_points = sum(g * c for g, c in entries)
    total_credits = sum(c for _, c in entries)
    if total_credits == 0:
        return 0.0
    return total_points / total_credits

def convert_temp(val, u_from, u_to):
    celsius = val
    if u_from == "F":
        celsius = (val - 32) * 5 / 9
    elif u_from == "K":
        celsius = val - 273.15
    
    if u_to == "F":
        return celsius * 9 / 5 + 32
    elif u_to == "K":
        return celsius + 273.15
    return celsius

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "bro"
    await update.message.reply_text(f"Sup {name}! ✌️ I am StudyBRO. Choose what you need below:", reply_markup=MAIN_KB)
    return MAIN_MENU

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Features 🚀:\n- 🎓 GPA Calculator\n- 📏 Unit Converter\n- 📅 Deadline Tracker\n- ✅ To-Do List\n- 🃏 Flashcards\nJust use the buttons."
    await update.message.reply_text(text, reply_markup=MAIN_KB)
    return MAIN_MENU

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎓 GPA Calculator":
        msg = (
            "Send your courses like this:\n"
            "Math A 3\n"
            "Physics B+ 4\n\n"
            "Grades & Points:\n"
            "A  = 4.00 (95-100)\n"
            "A- = 3.67 (90-94)\n"
            "B+ = 3.33 (85-89)\n"
            "B  = 3.00 (80-84)\n"
            "B- = 2.67 (75-79)\n"
            "C+ = 2.33 (70-74)\n"
            "C  = 2.00 (65-69)\n"
            "C- = 1.67 (60-64)\n"
            "D+ = 1.33 (55-59)\n"
            "D  = 1.00 (50-54)\n"
            "D- = 0.67 (45-49)\n"
            "F  = 0.00 (0-44)"
        )
        await update.message.reply_text(msg, reply_markup=BACK_KB)
        return GPA_ENTER
    elif text == "📏 Unit Converter":
        kb = ReplyKeyboardMarkup([["📏 Length", "⚖️ Weight"], ["🌡 Temperature", "🔙 Back"]], resize_keyboard=True)
        await update.message.reply_text("Choose category 🛠:", reply_markup=kb)
        return UNIT_CATEGORY
    elif text == "📅 Deadline Tracker":
        await update.message.reply_text("Deadline Tracker menu ⏰:", reply_markup=DEADLINE_KB)
        return DEADLINE_MENU
    elif text == "✅ To-Do List":
        await update.message.reply_text("To-Do List menu 📝:", reply_markup=TODO_KB)
        return TODO_MENU
    elif text == "🃏 Flashcards":
        await update.message.reply_text("Flashcards menu 🧠:", reply_markup=FLASH_KB)
        return FLASH_MENU
    elif text == "❓ Help":
        return await help_command(update, context)
    else:
        await update.message.reply_text("Use the buttons 🔽", reply_markup=MAIN_KB)
        return MAIN_MENU

async def gpa_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
    
    lines = text.split("\n")
    entries = []
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            try:
                credits = float(parts[-1])
                grade = parts[-2].upper()
                if credits > 0 and grade in GRADE_MAP:
                    entries.append((GRADE_MAP[grade], credits))
            except:
                pass
                
    if not entries:
        await update.message.reply_text("Wrong format ❌. Try again:\nMath A 3", reply_markup=BACK_KB)
        return GPA_ENTER
        
    gpa = calculate_gpa(entries)
    await update.message.reply_text(f"Your GPA: {gpa:.2f} 🎓", reply_markup=MAIN_KB)
    return MAIN_MENU

async def unit_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    if text not in UNIT_OPTIONS:
        return UNIT_CATEGORY
        
    context.user_data["ucat"] = text
    units = UNIT_OPTIONS[text]["units"]
    kb = [units[i:i+3] for i in range(0, len(units), 3)] + [["🔙 Back"]]
    
    await update.message.reply_text("Convert from 🔄:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return UNIT_FROM

async def unit_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    cat = context.user_data.get("ucat")
    if text not in UNIT_OPTIONS[cat]["units"]:
        return UNIT_FROM
        
    context.user_data["ufrom"] = text
    units = UNIT_OPTIONS[cat]["units"]
    kb = [units[i:i+3] for i in range(0, len(units), 3)] + [["🔙 Back"]]
    
    await update.message.reply_text("Convert to 🎯:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return UNIT_TO

async def unit_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    cat = context.user_data.get("ucat")
    if text not in UNIT_OPTIONS[cat]["units"]:
        return UNIT_TO
        
    context.user_data["uto"] = text
    await update.message.reply_text("Enter amount 🔢:", reply_markup=BACK_KB)
    return UNIT_VALUE

async def unit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    try:
        val = float(text.replace(",", "."))
    except:
        await update.message.reply_text("Send a number ❌.", reply_markup=BACK_KB)
        return UNIT_VALUE
        
    cat = context.user_data["ucat"]
    ufrom = context.user_data["ufrom"]
    uto = context.user_data["uto"]
    
    if cat == "🌡 Temperature":
        res = convert_temp(val, ufrom, uto)
    else:
        base = UNIT_OPTIONS[cat]["to_base"]
        res = val * base[ufrom] / base[uto]
        
    await update.message.reply_text(f"Result ✨: {res:.2f} {uto}", reply_markup=MAIN_KB)
    return MAIN_MENU

async def deadline_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    if text == "➕ Add Deadline":
        await update.message.reply_text("Enter task name 📝:", reply_markup=BACK_KB)
        return DEADLINE_ADD_TITLE
        
    if text == "📋 View Deadlines":
        if not user["deadlines"]:
            await update.message.reply_text("List is empty 📭", reply_markup=DEADLINE_KB)
            return DEADLINE_MENU
            
        msg = "Deadlines ⏰:\n"
        for i, d in enumerate(sorted(user["deadlines"], key=lambda x: x["date"])):
            msg += f"{i+1}. 📌 {d['title']} - {d['date']}\n"
        await update.message.reply_text(msg, reply_markup=DEADLINE_KB)
        return DEADLINE_MENU
        
    if text == "❌ Remove Deadline":
        if not user["deadlines"]:
            await update.message.reply_text("Nothing to remove 📭", reply_markup=DEADLINE_KB)
            return DEADLINE_MENU
            
        msg = "Enter number to delete 🗑:\n"
        for i, d in enumerate(user["deadlines"]):
            msg += f"{i+1}. {d['title']}\n"
        await update.message.reply_text(msg, reply_markup=BACK_KB)
        return DEADLINE_REMOVE
        
    return DEADLINE_MENU

async def deadline_add_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    context.user_data["dtitle"] = update.message.text
    await update.message.reply_text("Enter date and time (MM-DD HH:MM) ⏳:", reply_markup=BACK_KB)
    return DEADLINE_ADD_DATE

async def deadline_add_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    try:
        datetime.strptime(text, "%m-%d %H:%M")
    except:
        await update.message.reply_text("Bad format ❌. Use MM-DD HH:MM.", reply_markup=BACK_KB)
        return DEADLINE_ADD_DATE
        
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    user["deadlines"].append({"title": context.user_data["dtitle"], "date": text})
    save_data(data)
    
    await update.message.reply_text("Saved! ✅", reply_markup=DEADLINE_KB)
    return DEADLINE_MENU

async def deadline_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    try:
        idx = int(text) - 1
        user["deadlines"].pop(idx)
        save_data(data)
        await update.message.reply_text("Deleted 🗑", reply_markup=DEADLINE_KB)
    except:
        await update.message.reply_text("Wrong number ❌", reply_markup=BACK_KB)
        return DEADLINE_REMOVE
        
    return DEADLINE_MENU

async def todo_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    if text == "➕ Add Task":
        await update.message.reply_text("Enter task 📝:", reply_markup=BACK_KB)
        return TODO_ADD
        
    if text == "📋 View Tasks":
        if not user["todos"]:
            await update.message.reply_text("No tasks 📭", reply_markup=TODO_KB)
            return TODO_MENU
            
        msg = "Tasks 📋:\n"
        for i, t in enumerate(user["todos"]):
            status = "✅" if t["done"] else "⏳ [in progress]"
            msg += f"{i+1}. {status} {t['task']}\n"
        await update.message.reply_text(msg, reply_markup=TODO_KB)
        return TODO_MENU
        
    if text == "✅ Complete Task":
        context.user_data["todoact"] = "done"
        msg = "Enter number to complete ✅:\n"
        for i, t in enumerate(user["todos"]):
            if not t["done"]:
                msg += f"{i+1}. {t['task']}\n"
        await update.message.reply_text(msg, reply_markup=BACK_KB)
        return TODO_COMPLETE
        
    if text == "❌ Remove Task":
        context.user_data["todoact"] = "del"
        msg = "Enter number to delete 🗑:\n"
        for i, t in enumerate(user["todos"]):
            msg += f"{i+1}. {t['task']}\n"
        await update.message.reply_text(msg, reply_markup=BACK_KB)
        return TODO_COMPLETE
        
    return TODO_MENU

async def todo_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    user["todos"].append({"task": text, "done": False})
    save_data(data)
    
    await update.message.reply_text("Added ✅", reply_markup=TODO_KB)
    return TODO_MENU

async def todo_complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    act = context.user_data.get("todoact")
    
    try:
        idx = int(text) - 1
        if act == "del":
            user["todos"].pop(idx)
        else:
            user["todos"][idx]["done"] = True
        save_data(data)
        await update.message.reply_text("Done 🎉", reply_markup=TODO_KB)
    except:
        await update.message.reply_text("Wrong number ❌", reply_markup=BACK_KB)
        return TODO_COMPLETE
        
    return TODO_MENU

async def flash_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    if text == "➕ Add Card":
        await update.message.reply_text("Send question ❓:", reply_markup=BACK_KB)
        return FLASH_ADD_Q
        
    if text == "📋 View Cards":
        if not user["flashcards"]:
            await update.message.reply_text("No cards 📭", reply_markup=FLASH_KB)
            return FLASH_MENU
            
        msg = "Cards 🃏:\n"
        for i, c in enumerate(user["flashcards"]):
            msg += f"{i+1}. Q: {c['q']} | A: {c['a']}\n"
        await update.message.reply_text(msg, reply_markup=FLASH_KB)
        return FLASH_MENU
        
    if text == "🧠 Quiz Me!":
        if not user["flashcards"]:
            await update.message.reply_text("Add cards first ⚠️", reply_markup=FLASH_KB)
            return FLASH_MENU
            
        context.user_data["qidx"] = 0
        context.user_data["qscore"] = 0
        
        cards_copy = user["flashcards"].copy()
        random.shuffle(cards_copy)
        context.user_data["qcards"] = cards_copy
        
        await update.message.reply_text(f"Q: {cards_copy[0]['q']}", reply_markup=BACK_KB)
        return FLASH_QUIZ
        
    if text == "🗑 Clear Cards":
        user["flashcards"] = []
        save_data(data)
        await update.message.reply_text("Cleared 🗑", reply_markup=FLASH_KB)
        return FLASH_MENU
        
    return FLASH_MENU

async def flash_add_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    context.user_data["fq"] = update.message.text
    await update.message.reply_text("Send answer 💡:", reply_markup=BACK_KB)
    return FLASH_ADD_A

async def flash_add_a(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    uid = str(update.effective_user.id)
    data = load_data()
    user = get_user(data, uid)
    
    user["flashcards"].append({"q": context.user_data["fq"], "a": text})
    save_data(data)
    
    await update.message.reply_text("Added ✅", reply_markup=FLASH_KB)
    return FLASH_MENU

async def flash_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await update.message.reply_text("Main menu:", reply_markup=MAIN_KB)
        return MAIN_MENU
        
    cards = context.user_data["qcards"]
    idx = context.user_data["qidx"]
    
    if text.strip().lower() == cards[idx]["a"].strip().lower():
        context.user_data["qscore"] += 1
        resp = "Correct! ✅"
    else:
        resp = f"Wrong! ❌ It was: {cards[idx]['a']}"
        
    idx += 1
    context.user_data["qidx"] = idx
    
    if idx >= len(cards):
        score = context.user_data["qscore"]
        await update.message.reply_text(f"{resp}\nDone! 🎉 Score: {score}/{len(cards)}", reply_markup=FLASH_KB)
        return FLASH_MENU
        
    await update.message.reply_text(f"{resp}\n\nQ: {cards[idx]['q']}", reply_markup=BACK_KB)
    return FLASH_QUIZ

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("help", help_command)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_handler)],
            GPA_ENTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gpa_enter)],
            UNIT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, unit_category)],
            UNIT_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, unit_from)],
            UNIT_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, unit_to)],
            UNIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, unit_value)],
            DEADLINE_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, deadline_menu_handler)],
            DEADLINE_ADD_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, deadline_add_title)],
            DEADLINE_ADD_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, deadline_add_date)],
            DEADLINE_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, deadline_remove)],
            TODO_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, todo_menu_handler)],
            TODO_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, todo_add)],
            TODO_COMPLETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, todo_complete)],
            FLASH_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, flash_menu_handler)],
            FLASH_ADD_Q: [MessageHandler(filters.TEXT & ~filters.COMMAND, flash_add_q)],
            FLASH_ADD_A: [MessageHandler(filters.TEXT & ~filters.COMMAND, flash_add_a)],
            FLASH_QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, flash_quiz)],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("help", help_command)],
        allow_reentry=True
    )
    
    app.add_handler(conv)
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()