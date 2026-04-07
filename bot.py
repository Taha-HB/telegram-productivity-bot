from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import datetime
from config import TOKEN

# ---------- utilities ----------
def load(file):
    try:
        with open(file,"r") as f:
            return json.load(f)
    except:
        return {}

def save(file,data):
    with open(file,"w") as f:
        json.dump(data,f,indent=4)

# ---------- start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Productivity Bot v2\n\n"
        "/pomodoro 25\n"
        "/habit Study\n"
        "/done Study\n"
        "/streak\n"
        "/score\n"
        "/remind 18:30 Study\n"
        "/timetable Monday Math 9AM"
    )

# ---------- Pomodoro ----------
async def pomodoro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    minutes = int(context.args[0])
    chat_id = update.effective_chat.id

    await update.message.reply_text(f"🍅 Focus for {minutes} minutes")

    context.job_queue.run_once(
        pomodoro_done,
        when=minutes*60,
        chat_id=chat_id
    )

async def pomodoro_done(context):
    await context.bot.send_message(
        context.job.chat_id,
        text="⏰ Time's up! Take a break."
    )

# ---------- Habit ----------
async def habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)
    data = load("habits.json")
    user = str(update.effective_user.id)

    data.setdefault(user,[])
    data[user].append(name)

    save("habits.json",data)
    await update.message.reply_text("Habit added")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habit = " ".join(context.args)

    streak = load("streak.json")
    user = str(update.effective_user.id)

    today = str(datetime.date.today())

    streak.setdefault(user,{})
    streak[user][today] = streak[user].get(today,0)+1

    save("streak.json",streak)
    await update.message.reply_text("✅ Habit completed")

# ---------- Streak ----------
async def streak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load("streak.json")
    user = str(update.effective_user.id)

    days = len(data.get(user,{}))
    await update.message.reply_text(f"🔥 Streak: {days} days")

# ---------- Score ----------
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load("streak.json")
    user = str(update.effective_user.id)

    today = str(datetime.date.today())
    score = data.get(user,{}).get(today,0)*10

    await update.message.reply_text(f"📊 Productivity Score: {score}/100")

# ---------- Custom Reminder ----------
async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = context.args[0]
    text = " ".join(context.args[1:])

    hour,minute = map(int,time.split(":"))
    chat_id = update.effective_chat.id

    context.job_queue.run_daily(
        reminder,
        time=datetime.time(hour,minute),
        chat_id=chat_id,
        data=text
    )

    await update.message.reply_text("Reminder set")

async def reminder(context):
    await context.bot.send_message(
        context.job.chat_id,
        text=context.job.data
    )

# ---------- Timetable ----------
async def timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = context.args[0]
    subject = context.args[1]
    time = context.args[2]

    data = load("timetable.json")
    user = str(update.effective_user.id)

    data.setdefault(user,{})
    data[user].setdefault(day,[])
    data[user][day].append(f"{subject} {time}")

    save("timetable.json",data)
    await update.message.reply_text("📅 Added to timetable")

# ---------- motivation ----------
async def motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quotes = [
        "Discipline beats motivation.",
        "Small steps daily.",
        "Consistency builds greatness.",
        "Study now, shine later."
    ]

    import random
    await update.message.reply_text(random.choice(quotes))

# ---------- app ----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("pomodoro", pomodoro))
app.add_handler(CommandHandler("habit", habit))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("streak", streak_cmd))
app.add_handler(CommandHandler("score", score))
app.add_handler(CommandHandler("remind", remind))
app.add_handler(CommandHandler("timetable", timetable))
app.add_handler(CommandHandler("motivate", motivate))

print("Bot running...")
app.run_polling()
