# 🎯 Mobile App: Key Decisions & Next Steps

**Planning Session Date:** 2026-01-10
**Quick Reference for Implementation**

---

## ✅ KEY DECISIONS MADE

### **1. Architecture: Backend API + Mobile Frontend**
- Keep Python analysis engine (90% code reuse)
- Convert to FastAPI REST API
- Build React Native mobile app
- PostgreSQL database
- **Timeline:** 8-12 weeks MVP

### **2. Live Tracking: SKIP IT** ❌
**Decision:** Do NOT build live game tracking
**Reason:** DraftKings already does this; users won't leave DK during games
**Better focus:** Pre-game analysis + post-game learning

### **3. Post-Game Auto-Grading: BUILD IT** ✅
**Decision:** Use ESPN API for automatic prop grading after games
**Benefit:** Immediate results (Sunday night vs Tuesday)
**Cost:** ~$0/month (free API) + $70/mo infrastructure
**API Usage:** Only 53 calls/week (very sustainable)

### **4. Line Adjustment: FREE FEATURE** ✅
**Decision:** Manual line adjustment for Pick 6 is FREE (not premium)
**Reason:** It's core functionality; Pick 6 market is huge; better features exist for monetization
**Implementation:** Simple UI to adjust lines, re-score confidence in real-time

### **5. Parlay Builder + Tracker: PRIMARY FEATURE** ✅
**Decision:** Make this a main tab - it's both builder AND bet tracker (3-in-1)
**Key Innovation:** User builds parlay in app → saves it → places in their book → auto-graded
**Features:**
- Filter by teams, positions, confidence, prop types
- Live combined confidence
- Multi-sportsbook support (DraftKings, FanDuel, Underdog, PrizePicks, etc.)
- Save parlays (Free: 2-3, Premium: unlimited)
- Auto-optimization suggestions
- Line adjustment for Pick 6 built-in
- No OCR needed (user manually builds)

---

## 💰 FREEMIUM PRICING

### **FREE Tier**
- Top 10 props
- 2 pre-built parlays
- **2-3 saved custom parlays** (limit to drive upgrades)
- Manual line adjustment (unlimited)
- 10 prop searches/week
- 1 sportsbook selection
- Post-game auto-grading

### **PREMIUM ($9.99/mo)**
- All 100+ props
- 6 pre-built parlays
- **Unlimited saved parlays** (no 2-3 limit)
- Multiple sportsbooks
- Saved filter presets
- Push notifications
- Post-game auto-grading & analysis
- Custom agent weights
- Full bet history
- Share parlays with friends

### **PRO ($29.99/mo)**
- Everything in Premium
- AI chat/queries
- API access
- Community features (trending parlays)
- Advanced analytics (EV calculator, Kelly Criterion)

**Target:** 5% free → premium conversion = $6,495/mo at 10k users

---

## 🚀 IMPLEMENTATION ROADMAP

### **Phase 1: Backend API (Weeks 1-3)**
- [ ] Set up FastAPI project
- [ ] Convert analysis engine to REST endpoints
- [ ] PostgreSQL database migration
- [ ] JWT authentication
- [ ] Deploy to Heroku/Railway

### **Phase 2: Mobile MVP (Weeks 4-8)**
- [ ] React Native project setup
- [ ] Authentication/signup
- [ ] Home screen (top 10 props)
- [ ] Pre-built parlays view
- [ ] Basic prop search
- [ ] My Bets screen

### **Phase 3: Custom Builder (Weeks 9-10)**
- [ ] Filter UI (teams, positions, confidence)
- [ ] Add/remove props to parlay
- [ ] Live confidence calculation
- [ ] Save/load parlays

### **Phase 4: Premium Features (Weeks 11-12)**
- [ ] Push notifications (Firebase)
- [ ] ESPN API post-game grading
- [ ] Payment integration (RevenueCat)
- [ ] Agent customization
- [ ] Post-game analysis screens

### **Phase 5: Launch (Weeks 13-14)**
- [ ] Beta testing
- [ ] Bug fixes
- [ ] App Store submission
- [ ] Google Play submission
- [ ] Marketing materials

---

## 🎯 MUST-BUILD FEATURES (Priority Order)

### **1. Post-Game Analysis** 🔥🔥🔥
**Why:** DraftKings doesn't explain WHY props hit/miss
**Value:** Helps users learn edge, builds trust
**Implementation:** 3 weeks

### **2. Parlay Builder + Tracker (3-in-1)** 🔥🔥🔥
**Why:** Solves bet tracking + build + analysis in one feature
**Value:** Natural workflow, high engagement, no OCR complexity
**Key:** Build in app → Place in book → Auto-grade
**Implementation:** 3 weeks

### **3. Push Notifications** 🔥🔥🔥
**Why:** Line movement alerts are high value
**Value:** FOMO driver, high stickiness
**Implementation:** 1 week

### **4. Line Adjustment (Pick 6)** 🔥🔥
**Why:** Pick 6 is massive market
**Value:** Platform compatibility
**Implementation:** 1 week

### **5. System Performance Dashboard** 🔥🔥
**Why:** Transparency builds trust
**Value:** Shows which agents are accurate
**Implementation:** 1 week

### **6. One-Tap Export to DraftKings** 🔥
**Why:** Reduces friction
**Value:** Easier bet placement
**Implementation:** Few days

---

## 🚫 FEATURES TO SKIP

### **1. Live Game Tracking** ❌
- DraftKings already does this
- Users won't leave DK during games
- Would cost 6 weeks + $100/mo
- **Skip and focus on pre/post game value**

### **2. Complex AI Chat (MVP)** ❌
- Nice-to-have, not critical
- Can add in Pro tier later
- **Build post-game analysis first**

### **3. Social Sharing (MVP)** ❌
- Community features are Pro tier
- Focus on core analysis first
- **Add after launch**

---

## 📊 TECH STACK

### **Backend**
- Framework: **FastAPI** (Python)
- Database: **PostgreSQL** (Supabase or Heroku)
- Cache: **Redis**
- Hosting: **Heroku** or **Railway**
- Auth: **JWT tokens**

### **Mobile**
- Framework: **React Native**
- State: **Redux Toolkit** or **Zustand**
- Navigation: **React Navigation**
- Push Notifications: **Firebase Cloud Messaging**
- Payments: **RevenueCat** (handles iOS/Android IAP)

### **External APIs**
- **ESPN API** (post-game grading) - FREE
- **DraftKings API** (odds) - FREE
- **The Odds API** (backup) - $50/mo if needed

### **Services**
- **Firebase** (push notifications, analytics)
- **Sentry** (error tracking)
- **Mixpanel** (user analytics)
- **Stripe** (subscription management)

---

## 💡 KEY DESIGN PRINCIPLES

### **1. Mobile-First UX**
- One-handed use
- Bottom navigation (thumb-friendly)
- Big tap targets (44x44 minimum)
- Pull-to-refresh
- Swipe gestures

### **2. Speed**
- Home screen loads in <2 seconds
- Optimistic UI updates
- Aggressive caching
- Lazy loading

### **3. Trust**
- Always show WHY (top 3 reasons)
- System performance transparency
- Post-game "what we got right/wrong"
- Color-coded confidence (no mental math)

### **4. Simplicity**
- Default to smart recommendations
- Hide complexity in settings
- Progressive disclosure
- One-tap actions

---

## 📱 APP STRUCTURE

```
Bottom Navigation (5 tabs)
├─ 🏠 Home (Top 10 props, quick search)
├─ 🎰 Parlays (6 pre-built, ready to bet)
├─ ⚡ Build (My Parlays + Builder + Tracker) ← 3-in-1!
├─ 📊 My Bets (Results, history, analytics)
└─ ⚙️ More (Settings, stats, sportsbooks)
```

---

## 🎯 SUCCESS METRICS

### **MVP (First 3 months)**
- 1,000+ downloads
- 10% weekly active users
- 3% conversion to premium
- <5% churn rate

### **Year 1**
- 10,000+ users
- 500+ premium subscribers
- $5,000+ MRR
- 65%+ hit rate on 75+ confidence props

---

## 🔄 POST-GAME AUTO-GRADING FLOW

```
Sunday 4:15 PM - Early games end
    ↓
Backend polls ESPN API (every 5 min)
    ↓
Detects game is STATUS_FINAL
    ↓
Fetches box score (player stats)
    ↓
Compares actual vs line for each prop
    ↓
Marks HIT/MISS in database
    ↓
Analyzes which agents were accurate
    ↓
Generates insights
    ↓
Sends push notification to user
"🏈 Early games complete! Your props: 4/6 hit"
    ↓
User opens app → sees detailed results
    ↓
Shows "why it hit/miss" for each prop
    ↓
Shows agent performance today
    ↓
Generates lessons for next week
```

**API Usage:** 53 calls/week (sustainable!)

---

## 💰 COST BREAKDOWN

### **Development (One-Time)**
```
Backend API: 3 weeks @ $5k = $15k
Mobile MVP: 8 weeks @ $5k = $40k
Premium features: 4 weeks @ $5k = $20k

Total: $75k (if outsourced)
OR: 12-14 weeks (if built in-house)
```

### **Monthly Operating Costs**
```
Backend hosting (Heroku): $50/mo
Database (PostgreSQL): $25/mo
Redis cache: $15/mo
Push notifications (Firebase): $10/mo
Error tracking (Sentry): $10/mo
Analytics (Mixpanel): $10/mo

Total: $120/mo
```

### **Break-Even**
```
$120/mo ÷ $9.99 premium = 12 users

Revenue at scale:
- 10k users @ 5% conversion = 500 premium
- 500 × $9.99 = $4,995/mo
- 50 × $29.99 (Pro) = $1,500/mo
- Total MRR: $6,495/mo ($78k/year)
```

---

## 📝 IMMEDIATE NEXT STEPS

### **This Week**
1. [ ] Choose React Native vs Flutter (recommend React Native)
2. [ ] Set up FastAPI backend project
3. [ ] Design database schema
4. [ ] Create Figma mockups for 5 main screens

### **Next Week**
1. [ ] Build core API endpoints (props, parlays, analysis)
2. [ ] Set up PostgreSQL database
3. [ ] Implement JWT authentication
4. [ ] Deploy backend to Heroku

### **Week 3**
1. [ ] Initialize React Native project
2. [ ] Build authentication screens
3. [ ] Build Home screen
4. [ ] Connect to backend API

### **Week 4**
1. [ ] Build Parlays screen
2. [ ] Build My Bets screen
3. [ ] Build prop search
4. [ ] Test MVP on device

---

## 🎓 LEARNING RESOURCES

### **React Native**
- Official docs: https://reactnative.dev/
- Expo (easier setup): https://expo.dev/
- React Navigation: https://reactnavigation.org/

### **FastAPI**
- Official docs: https://fastapi.tiangolo.com/
- Tutorial: https://testdriven.io/blog/fastapi-crud/

### **Mobile App Monetization**
- RevenueCat docs: https://www.revenuecat.com/docs/
- Subscription best practices: https://www.revenuecat.com/blog/

### **Push Notifications**
- Firebase Cloud Messaging: https://firebase.google.com/docs/cloud-messaging
- React Native Firebase: https://rnfirebase.io/

---

## 📚 RELATED DOCUMENTS

- **Full Strategy:** `MOBILE_APP_STRATEGY.md`
- **ESPN API Spec:** `ESPN_API_POST_GAME_GRADING.md`
- **Current System:** `SYSTEM_ARCHITECTURE.md`

---

## ⚠️ IMPORTANT REMINDERS

### **1. Don't Build Live Tracking**
Users won't use it. DraftKings already has this. Focus on pre-game and post-game value.

### **2. Make Line Adjustment Free**
It's not a premium feature - it's core Pick 6 compatibility. Monetize better features.

### **3. Post-Game Analysis is Gold**
This is your differentiation. DraftKings shows W/L but not WHY. Build this well.

### **4. Start Simple**
Don't build everything at once. MVP = Home + Parlays + My Bets. Add features iteratively.

### **5. Test With Real Users Early**
Get beta testers by Week 6. Their feedback will be invaluable.

---

## 🎯 THE CORE VALUE PROPOSITION

**Your app's job:**

1. **Pre-game (Friday-Sunday AM):** Help users find +EV bets
   - Analysis engine, confidence scores, custom builder

2. **During game (Sunday 1-10pm):** Let DraftKings handle tracking
   - Users are in DK app placing/watching bets

3. **Post-game (Sunday night):** Help users learn and improve
   - Auto-graded results, "why it hit/miss", agent accuracy

**You're not competing with DraftKings. You're complementing them.**

---

**Document Status:** Ready for implementation
**Next Review:** After MVP launch
**Questions?** Reference the detailed docs above or DM
