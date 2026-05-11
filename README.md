# 🎓 StudyBRO - Telegram Student Assistant Bot

> A feature-packed Telegram bot designed to make student life easier.  
> Team **GPR** | Intro to Programming - Team Project

---

## 📋 Features

| Feature | Description |
|---|---|
| 📊 **GPA Calculator** | Enter courses with grades & credits, get your GPA instantly |
| 📐 **Unit Converter** | Convert length, weight, and temperature between common units |
| 📅 **Deadline Tracker** | Add deadlines with due dates, see how many days are left |
| ✅ **To-Do List** | Add tasks and mark them as complete |
| 🃏 **Flashcard Maker** | Create Q&A flashcards and quiz yourself |

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/StudyBRO.git
cd StudyBRO
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the bot
```bash
python bot.py
```

Then open Telegram and search for your bot by username, then send `/start`.

---

## 📁 Project Structure

```
StudyBRO/
├── bot.py            # Main bot logic (all features)
├── requirements.txt  # Python dependencies
├── user_data.json    # Auto-generated: stores user deadlines, tasks & flashcards
└── README.md         # This file
```

---

## 🧮 GPA Grade Scale

| Letter | Points |
|--------|--------|
| A      | 4.0    |
| A-     | 3.67    |
| B+     | 3.33    |
| B      | 3.0    |
| B-     | 2.67    |
| C+     | 2.33    |
| C      | 2.0    |
| C-     | 1.67    |
| D      | 1.0    |
| D-      | 0.67    |
| F      | 0.0    |

**Input format:** `CourseName Grade Credits`  
**Example:** `Mathematics A 3`

---

## 📐 Unit Converter — Supported Units

- **Length:** km, m, cm, mm, mile, yard, foot, inch  
- **Weight:** kg, g, mg, lb, oz, ton  
- **Temperature:** °C, °F, K

---

## 👥 Team GPR

* **Alikhan Seitkassym**: GPA calculator logic, JSON setup, and overall bot architecture.
* **Otelbek Sherkhan**: Unit Converter module and final presentation preparation.
* **Zhaksybay Almuktadir**: Deadline Tracker and To-Do List modules, technical documentation (README.md).
* **Utebayev Ansar**: Flashcards system (including question randomizer) and bot video demo recording.
---

## 🛠 Tech Stack

- Python 3.10+
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v20.7
- JSON file storage for persistence
