# 🚨 Line Movement Alert System - Setup Guide

## What This Does

Monitors NFL betting lines 24/7 and sends instant Slack alerts when:
- Lines move 2+ points (significant movement)
- Reverse line movement detected (sharp money indicator)
- Totals shift significantly
- Suspicious betting patterns emerge

---

## 📋 Setup (15 minutes)

### **Step 1: Get The Odds API Key**

1. Go to: https://the-odds-api.com
2. Sign up for free account
3. Get your API key
4. **Free tier:** 500 requests/month (enough for hourly checks)
5. **Paid tier:** $50/month for unlimited

### **Step 2: Get Slack Webhook URL** (Optional but Recommended)

1. Go to: https://api.slack.com/apps
2. Select your "NFL Betting Bot" app
3. Click "Incoming Webhooks" (left sidebar)
4. Toggle "Activate Incoming Webhooks" to **ON**
5. Click "Add New Webhook to Workspace"
6. Select channel: `#nfl-betting` or wherever you want alerts
7. Click "Allow"
8. Copy the Webhook URL (looks like: `https://hooks.slack.com/services/xxx/yyy/zzz`)

### **Step 3: Add to .env File**

```bash
notepad C:\Users\scott\Desktop\nfl-betting-system\.env
```

Add these lines:

```bash
# The Odds API
ODDS_API_KEY=your-api-key-here

# Slack Webhook (for alerts)
SLACK_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz
```

Save and close.

---

## 🚀 Running the Monitor

### **Option A: Run Continuously (Background)**

In a NEW terminal:

```bash
cd C:\Users\scott\Desktop\nfl-betting-system
python scripts\line_monitoring\monitor_main.py
```

**This will:**
- Check lines every hour
- Run until you stop it (Ctrl+C)
- Send Slack alerts instantly when lines move
- Log all movements to CSV

**Leave this terminal open!**

---

### **Option B: Run Once (Test)**

```bash
cd C:\Users\scott\Desktop\nfl-betting-system
python scripts\line_monitoring\line_monitor.py
```

Runs ONE check cycle, then stops. Good for testing.

---

## 📊 What You'll Get

### **Slack Alerts Look Like:**

```
🚨 LINE MOVEMENT ALERT

📉 PIT Steelers @ CIN Bengals
   PIT Steelers: -3.5 → -5.5 (-2.0)
   Book: draftkings

📈 SF 49ers @ SEA Seahawks  
   Total: 45.5 → 48.0 (+2.5)
   Book: fanduel
```

### **Data Stored:**

**Current lines:**
`data/lines/current_lines.json`

**Historical log:**
`data/lines/line_movements_log.csv`

---

## ⚙️ Configuration

### **Change Alert Threshold**

Edit `line_monitor.py` around line 30:

```python
self.SIGNIFICANT_MOVEMENT = 2.0  # Change to 1.5 for more alerts
```

### **Change Check Frequency**

When starting monitor:

```python
# Check every 30 minutes instead of 60
monitor.run_continuously(interval_minutes=30)
```

**Warning:** More frequent checks = more API calls = hits free tier limit faster

---

## 📈 Understanding the Alerts

### **Sharp Money Indicators:**

🚨 **Line moves AGAINST public betting**
- Example: 70% of bets on Team A, but line moves to Team B
- Indicates professional/sharp money on Team B

🚨 **Large movement with little time**
- Line shifts 3+ points in 1 hour
- Usually means big money hit the book

🚨 **Coordinated movement**
- Multiple books move same direction simultaneously
- Indicates market-wide adjustment

---

## 🔧 Troubleshooting

### **"ODDS_API_KEY not configured"**

Add it to your `.env` file (see Step 3 above)

### **"Failed to fetch current lines"**

Check:
- API key is valid
- Haven't exceeded free tier limit (500/month)
- Internet connection working

### **"Cannot send Slack alert"**

Add `SLACK_WEBHOOK` to `.env` file. 

Without it, alerts will still be logged to console and CSV, just not sent to Slack.

### **"Too many API requests"**

Free tier = 500 requests/month

If checking every hour = ~720 requests/month

Solutions:
- Check every 2 hours instead: `interval_minutes=120`
- Upgrade to paid tier: $50/month
- Only run during key times (weekdays, leading up to games)

---

## 📊 Historical Analysis

All movements are logged to CSV. You can analyze:

```python
import pandas as pd

# Load historical movements
df = pd.read_csv('data/lines/line_movements_log.csv')

# Find biggest movements
big_moves = df[df['movement_abs'] >= 3.0]

# Movements by bookmaker
df.groupby('bookmaker')['movement_abs'].mean()

# Most volatile games
df.groupby('game')['movement_abs'].sum().sort_values(ascending=False)
```

---

## 🎯 Best Practices

### **When to Act on Line Movements:**

✅ **DO act on:**
- Early week movements (Mon-Wed) - sharps get in early
- Coordinated moves across multiple books
- Reverse line movement (line vs public betting %)
- Movements of 3+ points

❌ **DON'T act on:**
- Friday/Saturday movements (often public money)
- Single book movements (could be balancing their book)
- Small movements (<1.5 points)
- Movements right before kickoff (noise)

### **Optimal Check Times:**

**Monday-Wednesday:** Check every 2 hours
- Sharp money hits early
- Most valuable movements

**Thursday-Saturday:** Check every hour
- More volatile
- Track if early moves holding

**Sunday morning:** Check every 30 minutes
- Last chance to catch value
- Compare to your opening lines

---

## 💰 ROI Expectations

**Line movement monitoring typically adds:**
- 2-5% edge on sharp-follow plays
- Better timing on your original picks
- Avoid bad beats from late line shifts

**Most valuable during:**
- NFL Weeks 1-17
- Playoff games
- Thursday Night Football (less info, more movement)

---

## 🚀 Advanced Features (Coming Soon)

- Public betting % integration
- Opening line vs current line comparison
- Steam detection (rapid line moves)
- Injury correlation
- Weather impact alerts

---

## 📧 Support

Having issues? Check:
1. `.env` file has correct API keys
2. API key hasn't exceeded limit
3. Slack webhook URL is correct
4. Monitor is still running (check terminal)

---

**Ready to start monitoring? Run the monitor now!**

```bash
python scripts\line_monitoring\monitor_main.py
```
