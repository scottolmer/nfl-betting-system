# Mobile App UX Overhaul - Testing Checklist

## Pre-Testing Setup
- [ ] Fresh install on clean device/emulator
- [ ] Clear AsyncStorage before testing
- [ ] Backend server running and accessible
- [ ] Test data available for Week 17

---

## Phase 1: Onboarding Tests

### First Launch Experience
- [ ] Fresh install shows onboarding carousel
- [ ] All 3 screens display correctly (Welcome, How It Works, Confidence)
- [ ] Pagination dots show current step
- [ ] Can swipe between screens
- [ ] "Skip" button works on all screens
- [ ] "Next" button advances to next screen
- [ ] "Get Started" button completes onboarding on final screen
- [ ] After completion, app navigates to main interface
- [ ] Onboarding never shown again on subsequent launches

### Onboarding Content Verification
- [ ] Welcome screen shows app icon and 3 feature items
- [ ] How It Works shows 3 ways to use app with icons
- [ ] Confidence System shows 3 tiers with correct colors:
  - 🔥 80+ Elite (Green #22C55E)
  - ⭐ 75-79 Strong (Orange #F59E0B)
  - ✅ 70-74 Solid (Blue #3B82F6)

---

## Phase 2: Navigation & Home Screen Tests

### Navigation Tab Verification
- [ ] Tab 1: "Picks" with 🎯 icon
- [ ] Tab 2: "Pre-Built" with 🎰 icon
- [ ] Tab 3: "My Parlays" with ⚡ icon
- [ ] Tab 4: "Results" with 📈 icon
- [ ] Tab 5: "More" with ⚙️ icon
- [ ] All tabs navigate correctly
- [ ] Active tab highlighted in blue (#3B82F6)
- [ ] Inactive tabs in gray (#6B7280)

### Home Screen - Quick Start Section
- [ ] Quick Start section visible at top
- [ ] Featured prop card displays correctly
- [ ] Featured prop shows confidence badge
- [ ] "View Pre-Built" button navigates to Pre-Built tab
- [ ] "Build Custom" button navigates to My Parlays tab
- [ ] Tap featured prop opens detail modal (if implemented)

### Home Screen - Top Props List
- [ ] Props displayed as collapsible cards
- [ ] Cards start in collapsed state
- [ ] Tap card to expand shows full details
- [ ] Expanded card shows:
  - Player name and team
  - Stat type, bet type, line
  - Projection and cushion (if available)
  - Top reasons (first 3)
  - Agent count
- [ ] "Tap to expand" hint visible on collapsed cards
- [ ] Can collapse expanded card by tapping again

### Home Screen - Help & Info
- [ ] Info tooltip icon visible in header
- [ ] Help footer "New to betting props?" visible
- [ ] "Watch Tutorial" button functional
- [ ] Section title "Top 10 Props" with info tooltip

---

## Phase 3: Educational Components Tests

### InfoTooltip Component
- [ ] [?] icons visible throughout app
- [ ] Tap [?] opens explanation modal
- [ ] Modal shows title, description, and example
- [ ] Modal has "Got it" button
- [ ] "Got it" closes modal
- [ ] Tap outside modal closes it
- [ ] Multiple tooltips can be accessed in sequence

### Tooltip Content Verification
Test these key tooltips exist and display correctly:
- [ ] confidence - Explains AI scoring
- [ ] cushion - Explains projection vs line difference
- [ ] projection - Explains predicted outcome
- [ ] combinedConfidence - Explains parlay confidence calculation
- [ ] riskLevel - Explains LOW/MEDIUM/HIGH
- [ ] parlays - Explains what parlays are
- [ ] sportsbook - Explains platform selection
- [ ] myParlays - Explains custom parlay feature

### HelpBanner Component
- [ ] Help banners show on first visit to screens
- [ ] "Got it" button dismisses banner
- [ ] "Don't show again" button dismisses permanently
- [ ] Dismissed banners don't reappear
- [ ] Banner state persists across app restarts

---

## Phase 4: Pre-Built & My Parlays Tests

### Pre-Built Parlays Screen
- [ ] "How to Use" help banner shows on first visit
- [ ] Banner can be dismissed
- [ ] Filter buttons display correctly (All, 2-Leg, 3-Leg, 4+)
- [ ] Filter counts accurate
- [ ] Selecting filter updates parlay list
- [ ] FEATURED badge on highest confidence parlay
- [ ] Parlay cards show:
  - Name
  - Leg count and combined confidence
  - Risk level badge with correct color
  - Info tooltips
- [ ] Tap parlay card expands to show legs
- [ ] Expanded view shows all leg details
- [ ] "Copy Props" and "Save" buttons functional

### My Parlays Screen (Empty State)
- [ ] Empty state shows when no parlays
- [ ] Empty state displays ⚡ icon
- [ ] "Build Your First Parlay" title and description
- [ ] "+ Create Your First Parlay" button
- [ ] Button navigates to Create Parlay wizard

### My Parlays Screen (With Parlays)
- [ ] "Create" button visible in header or top
- [ ] Parlay cards display correctly
- [ ] Status badges show correct colors:
  - Draft: Gray
  - Placed: Blue
  - Won: Green
  - Lost: Red
- [ ] Tap card expands to show legs
- [ ] Actions available: Copy, Mark Placed, Delete
- [ ] Delete confirmation works
- [ ] Mark as Placed updates status

---

## Phase 5: Create Parlay Wizard Tests

### Wizard Navigation
- [ ] Progress stepper shows "Step 1 of 3"
- [ ] Step labels: Setup, Add Props, Review
- [ ] Current step highlighted
- [ ] Completed steps show checkmark
- [ ] Back button not visible on Step 1
- [ ] Back button works on Steps 2 & 3
- [ ] Next button changes to "Review" on Step 2
- [ ] Step 3 shows "Save Parlay" button instead of Next

### Step 1: Setup
- [ ] Parlay name input field autofocuses
- [ ] Sportsbook selection displays all options
- [ ] "DraftKings Pick 6" shows RECOMMENDED badge
- [ ] Can select different sportsbook
- [ ] Selected sportsbook highlighted with checkmark
- [ ] Info tooltips present and functional
- [ ] "Why DraftKings Pick 6?" info box displays
- [ ] Cannot proceed without parlay name

### Step 2: Add Props
- [ ] Floating summary card appears
- [ ] Summary shows "0 / 6 legs" initially
- [ ] "Need at least 2 legs" indicator when 0-1 legs
- [ ] Filters collapsed by default
- [ ] Tap "Filters" expands filter panel
- [ ] Min Confidence buttons work (60, 65, 70, 75, 80)
- [ ] Position chips work (QB, RB, WR, TE)
- [ ] Props list updates when filters change
- [ ] Props display with confidence scores
- [ ] Tap prop to select (border turns blue, checkmark appears)
- [ ] Selected props appear in horizontal scroll at top
- [ ] Can remove prop from selected chips
- [ ] Maximum 6 legs enforced
- [ ] Alert shown when trying to add 7th leg
- [ ] Floating summary updates live:
  - Leg count accurate
  - Combined confidence calculates correctly
  - Risk level updates (LOW/MEDIUM/HIGH)
  - "Valid parlay" shown for 2-6 legs
- [ ] "Adjust Line" button functional (if testing line adjustment)
- [ ] Cannot proceed to Step 3 without 2+ legs

### Step 3: Review
- [ ] Summary card shows parlay name and sportsbook
- [ ] Stats display: Legs, Combined Confidence, Risk Level
- [ ] All legs listed with full details
- [ ] Leg numbers (1, 2, 3...) displayed
- [ ] Each leg shows:
  - Player name
  - Team and position
  - Stat type, bet type, line
  - Projection and cushion
  - Individual confidence
- [ ] Adjusted lines show "(Adjusted from X)" note
- [ ] "Next Steps" info box displayed
- [ ] Disclaimer warning visible
- [ ] "Save Parlay" button enabled with 2+ legs

### Wizard Completion
- [ ] Save button triggers save
- [ ] Success alert shown
- [ ] Parlay appears in My Parlays
- [ ] Wizard closes after save
- [ ] Can cancel wizard at any step
- [ ] Cancel confirmation (if implemented)

---

## Phase 6: Results & More Screens Tests

### Results Screen
- [ ] "Coming Soon" card displays
- [ ] Card shows 📈 icon and title
- [ ] 4 upcoming features listed with icons
- [ ] "For Now" info box with guidance
- [ ] "View My Parlays" button navigates correctly
- [ ] Footer encourages feedback
- [ ] Info tooltip in header functional

### More Screen
- [ ] Help & Learning section at top
- [ ] Help items display:
  - 📖 View Tutorial
  - ❓ Understanding Confidence
  - 🎯 How to Build Parlays
  - 🔢 Reading Projections
- [ ] Tutorial Settings section shows
- [ ] "Reset Tutorial" option available
- [ ] App Info section displays version and backend info
- [ ] Coming Soon section lists future features
- [ ] About section shows app description
- [ ] Footer text displayed

### Tutorial Re-access
- [ ] Tap "View Tutorial" opens tutorial modal
- [ ] Tutorial shows full onboarding carousel
- [ ] Close button visible and functional
- [ ] Can dismiss tutorial at any point
- [ ] Completing tutorial closes modal
- [ ] App remains in logged-in state

### Reset Tutorial
- [ ] Tap "Reset Tutorial" shows confirmation alert
- [ ] Cancel button dismisses alert
- [ ] Reset button clears onboarding flag
- [ ] Success message shown
- [ ] Tutorial appears on next app launch
- [ ] Tutorial doesn't immediately show after reset

---

## Phase 7: Polish & Testing

### Performance Tests
- [ ] App launches in < 3 seconds
- [ ] Screens transition smoothly (no janky animations)
- [ ] Scrolling is smooth on all screens
- [ ] Props load within 2 seconds
- [ ] No memory leaks during navigation
- [ ] Images/icons load quickly
- [ ] No dropped frames during animations

### Accessibility Tests
- [ ] Screen reader support (VoiceOver/TalkBack)
- [ ] All interactive elements have proper labels
- [ ] Buttons have sufficient touch target size (44x44)
- [ ] Sufficient color contrast (4.5:1 minimum)
- [ ] Text is readable at system font sizes
- [ ] No critical info conveyed by color alone
- [ ] Focus order is logical
- [ ] Dynamic type support

### Cross-Device Testing
- [ ] Test on small screen (iPhone SE / 5" Android)
- [ ] Test on medium screen (iPhone 14 / 6" Android)
- [ ] Test on large screen (iPhone 14 Pro Max / 6.7" Android)
- [ ] Test on tablet (iPad / Android tablet)
- [ ] Landscape orientation (if supported)
- [ ] Dark mode compatibility (if implemented)

### Error Handling
- [ ] Network error shows helpful message
- [ ] Failed prop load shows retry button
- [ ] Invalid line adjustment shows error alert
- [ ] Save failure shows error message
- [ ] Loading states show spinners
- [ ] Empty states show helpful guidance

### Edge Cases
- [ ] App works with 0 props available
- [ ] App works with 0 parlays
- [ ] App works with maximum parlays (free tier limit)
- [ ] Handles very long player names
- [ ] Handles very long parlay names
- [ ] Handles special characters in names
- [ ] Handles very high/low confidence scores
- [ ] Network offline handling
- [ ] Background/foreground transitions

### Analytics Verification
- [ ] Check console logs for analytics events (dev mode)
- [ ] Verify events tracked:
  - App opened
  - Onboarding completed
  - Screen views
  - Parlay created
  - Filter applied
  - Tooltip opened
  - Help banner dismissed

---

## User Flows - End-to-End Tests

### Flow 1: First-Time User Complete Journey
1. [ ] Launch app for first time
2. [ ] Complete onboarding (all 3 screens)
3. [ ] Land on Picks screen
4. [ ] View Quick Start section
5. [ ] Tap featured prop (if modal implemented)
6. [ ] Navigate to Pre-Built tab
7. [ ] Dismiss help banner
8. [ ] Filter parlays by 2-Leg
9. [ ] Tap parlay to expand
10. [ ] Navigate to My Parlays tab
11. [ ] See empty state
12. [ ] Tap "Create Your First Parlay"
13. [ ] Complete wizard (all 3 steps)
14. [ ] Save parlay
15. [ ] See parlay in My Parlays
16. [ ] Navigate to Results
17. [ ] See coming soon message
18. [ ] Navigate to More
19. [ ] Open tutorial modal
20. [ ] Complete tutorial
21. [ ] Exit app

### Flow 2: Returning User Quick Action
1. [ ] Launch app (skip onboarding)
2. [ ] Navigate to My Parlays
3. [ ] Tap Create button
4. [ ] Enter name (Step 1)
5. [ ] Next to Step 2
6. [ ] Apply filters
7. [ ] Select 3 props
8. [ ] Next to Step 3
9. [ ] Review details
10. [ ] Save parlay
11. [ ] Mark parlay as "Placed"
12. [ ] Exit app

### Flow 3: Educational Journey
1. [ ] Launch app
2. [ ] Tap multiple [?] tooltips on Picks screen
3. [ ] Navigate to Pre-Built
4. [ ] Tap info tooltips
5. [ ] Read help banner
6. [ ] Navigate to More
7. [ ] View Tutorial
8. [ ] Browse Help & Learning items
9. [ ] Exit app

---

## Regression Tests

After any bug fix or new feature, re-test:
- [ ] Onboarding flow still works
- [ ] Navigation between tabs works
- [ ] Parlay wizard completes successfully
- [ ] Existing parlays still display
- [ ] AsyncStorage persistence works
- [ ] No new console errors/warnings

---

## Known Limitations (Document, Don't Test)

- Results screen is placeholder (auto-grading not implemented)
- Line adjustment requires backend API endpoint
- Tutorial items in More screen are informational only
- Analytics events logged to console only (no service integration)
- No push notifications
- No offline mode
- No social sharing
- No dark mode
- No internationalization

---

## Testing Notes

### Device/Emulator Setup
- iOS: Use Xcode Simulator (iOS 15+)
- Android: Use Android Emulator (API 30+)
- Physical device preferred for performance testing

### Test Data Requirements
- Backend should have Week 17 props loaded
- Props should have varied confidence scores (60-85)
- Props should cover all positions (QB, RB, WR, TE)

### Bug Reporting Format
When filing bugs, include:
1. Device/OS version
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Screenshots/video
6. Console logs (if applicable)

---

## Success Criteria

### Must Pass
- All onboarding tests pass
- All navigation tests pass
- Parlay wizard completes successfully
- No app crashes
- No data loss

### Should Pass
- All help features functional
- All tooltips accessible
- Performance acceptable
- Basic accessibility support

### Nice to Have
- Perfect cross-device compatibility
- Advanced accessibility features
- Sub-2 second load times
- Zero console warnings

---

## Test Completion Sign-Off

| Test Section | Pass/Fail | Notes | Tester | Date |
|--------------|-----------|-------|--------|------|
| Phase 1: Onboarding | | | | |
| Phase 2: Navigation & Home | | | | |
| Phase 3: Educational | | | | |
| Phase 4: Parlays | | | | |
| Phase 5: Wizard | | | | |
| Phase 6: Results & More | | | | |
| Phase 7: Polish | | | | |
| User Flows | | | | |
| Performance | | | | |
| Accessibility | | | | |

---

**Ready for Production When:**
- [x] All "Must Pass" criteria met
- [x] All "Should Pass" criteria met
- [x] No critical bugs outstanding
- [x] Performance acceptable on target devices
- [x] User flows complete successfully
