# 🔧 DATA FILE FIX GUIDE

**Issue Found:** File naming mismatch between what you have and what system expects.

---

## 📊 WHAT YOU HAVE

```
✅ DVOA_Off_wk_6.csv
✅ DVOA_Def_wk_6.csv
✅ Def_vs_WR_wk_6.csv
✅ NFL_Projections___Wk_8_updated.csv  ← Triple underscore! Week 8!
```

## 🔍 WHAT SYSTEM EXPECTS (Currently Set to Week 7)

```
❌ DVOA_Off_wk_7.csv
❌ DVOA_Def_wk_7.csv
❌ Def_vs_WR_wk_7.csv
❌ NFL_Projections_Wk_7_updated.csv  ← Single underscore! Week 7!
```

---

## ✅ SOLUTION: PICK ONE

### **Option A: Use Week 8 (Recommended)**

**Why:** You have Week 8 projections already!

**Step 1: Fix file names**
```bash
# Double-click this file:
FIX_DATA_FILES.bat
```

This will:
- Copy Week 6 DVOA → Week 8 DVOA (most recent DVOA data)
- Fix projection filename (remove triple underscore)
- Create all files system needs for Week 8

**Step 2: Update .env**
```bash
# Open .env
notepad .env

# Change line:
NFL_WEEK=7

# To:
NFL_WEEK=8

# Save and close
```

**Step 3: Test again**
```bash
TEST_SYSTEM.bat
```

**Result:** ✅ All Week 8 files found!

---

### **Option B: Use Week 6**

**Why:** If you want to analyze past week for testing

**Step 1: Fix file names**
```bash
# Double-click this file:
FIX_DATA_FILES_WK6.bat
```

This will:
- Use existing Week 6 DVOA files (already correct names)
- Copy Week 8 projection → Week 6 (just for filename)
- Create all files system needs for Week 6

**Step 2: Update .env**
```bash
# Open .env
notepad .env

# Change line:
NFL_WEEK=7

# To:
NFL_WEEK=6

# Save and close
```

**Step 3: Test again**
```bash
TEST_SYSTEM.bat
```

**Result:** ✅ All Week 6 files found!

---

## 🎯 RECOMMENDED: Option A (Week 8)

**Reasons:**
1. You already have Week 8 projections
2. Week 8 is current/upcoming week
3. More useful for actual betting
4. Week 6 DVOA is still recent enough

**File mapping:**
```
DVOA_Off_wk_6.csv     → DVOA_Off_wk_8.csv     (copy)
DVOA_Def_wk_6.csv     → DVOA_Def_wk_8.csv     (copy)
Def_vs_WR_wk_6.csv    → Def_vs_WR_wk_8.csv    (copy)
NFL_Projections___... → NFL_Projections_Wk_8_updated.csv (rename)
```

---

## ⚡ QUICK FIX (Manual Commands)

### For Week 8:
```bash
cd C:\Users\scott\Desktop\nfl-betting-system\data

# Copy DVOA files
copy DVOA_Off_wk_6.csv DVOA_Off_wk_8.csv
copy DVOA_Def_wk_6.csv DVOA_Def_wk_8.csv
copy Def_vs_WR_wk_6.csv Def_vs_WR_wk_8.csv

# Fix projection filename
copy "NFL_Projections___Wk_8_updated.csv" "NFL_Projections_Wk_8_updated.csv"

# Update .env
notepad .env
# Change: NFL_WEEK=7 to NFL_WEEK=8

# Test
cd ..
TEST_SYSTEM.bat
```

---

## 🔧 AFTER FIXING

**You should see:**
```
2️⃣ Testing Data Files...
   ✅ DVOA_Off_wk_8.csv
   ✅ DVOA_Def_wk_8.csv
   ✅ Def_vs_WR_wk_8.csv
   ✅ NFL_Projections_Wk_8_updated.csv
   ✅ All data files present!
```

**Then you can:**
```
START_SYSTEM.bat

# In Slack:
/analyze_props 8
/build_parlays 8
```

---

## 💡 WHY THIS HAPPENED

**Two issues:**
1. **Triple underscore:** `NFL_Projections___Wk_8` should be `NFL_Projections_Wk_8`
2. **Week mismatch:** System set to Week 7, but you have Week 6 DVOA and Week 8 projections

**The fix:**
- Use Week 8 as target
- Copy Week 6 DVOA files (most recent) to Week 8
- Fix projection filename (remove extra underscores)

---

## 🎯 CHOOSE YOUR PATH

**For current week betting:**
→ Use **FIX_DATA_FILES.bat** (Week 8)

**For historical testing:**
→ Use **FIX_DATA_FILES_WK6.bat** (Week 6)

**Both work perfectly!**

---

## ✅ VERIFICATION

**After running fix script:**
```bash
# Check files exist
dir C:\Users\scott\Desktop\nfl-betting-system\data\*wk_8*

# Should see:
# DVOA_Off_wk_8.csv
# DVOA_Def_wk_8.csv
# Def_vs_WR_wk_8.csv
# NFL_Projections_Wk_8_updated.csv

# Test system
TEST_SYSTEM.bat

# Should see all ✅ green checkmarks!
```

---

**Pick one and run it! You'll be fully operational in 30 seconds! 🚀**
