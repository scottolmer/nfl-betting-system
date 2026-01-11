# NFL Betting Analysis - Mobile App

React Native mobile app for the NFL Betting Analysis system. Built with Expo and TypeScript.

## Features Implemented ✅

### Phase 1: Backend API - Complete
- FastAPI backend with 9-agent analysis system
- Props analysis endpoints
- Pre-built parlay generation
- Line adjustment for Pick 6
- CORS middleware for mobile app

### Phase 2: Mobile App MVP - In Progress
- ✅ Bottom tab navigation (5 tabs)
- ✅ Home screen (Top 10 props display)
- ✅ Pre-Built Parlays screen
- ✅ API service layer
- ✅ TypeScript types
- 🚧 Build screen (placeholder)
- 🚧 My Bets screen (placeholder)
- 🚧 More/Settings screen (placeholder)

## Tech Stack

- **Framework**: React Native with Expo
- **Navigation**: React Navigation (Bottom Tabs)
- **API Client**: Axios
- **Language**: TypeScript
- **Backend**: FastAPI (Python)

## Prerequisites

- Node.js 18+ and npm
- Expo CLI: `npm install -g expo-cli`
- Python 3.9+ (for backend)
- Expo Go app on your phone (for testing)

## Setup Instructions

### 1. Install Mobile Dependencies

```bash
cd mobile
npm install
```

### 2. Start the Backend API

The mobile app needs the FastAPI backend running. In a separate terminal:

```bash
# From the project root
cd ..
pip install fastapi uvicorn pydantic-settings

# Start the backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- Local: http://localhost:8000
- Network: http://<your-ip>:8000

### 3. Configure API URL

If testing on a physical device, update the API URL in `src/services/api.ts`:

```typescript
const API_BASE_URL = __DEV__
  ? 'http://192.168.x.x:8000'  // Replace with your computer's local IP
  : 'https://your-production-api.com';
```

To find your local IP:
- **Windows**: Run `ipconfig` and look for IPv4 Address
- **Mac/Linux**: Run `ifconfig` or `ip addr`

### 4. Start the Mobile App

```bash
npm start
```

This will start the Expo development server and show a QR code.

### 5. Test on Your Device

#### Option A: Expo Go App (Easiest)
1. Install **Expo Go** from App Store (iOS) or Google Play (Android)
2. Scan the QR code from the terminal
3. The app will load on your device

#### Option B: iOS Simulator (Mac only)
```bash
npm run ios
```

#### Option C: Android Emulator
```bash
npm run android
```

## Testing the App

### 1. Check Backend Health

First, verify the backend is running:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "nfl-betting-api",
  "version": "1.0.0"
}
```

### 2. Test API Endpoints

**Get Top Props:**
```bash
curl -H "X-API-Key: dev_test_key_12345" \
  "http://localhost:8000/api/props/top?week=17&limit=10"
```

**Get Pre-Built Parlays:**
```bash
curl -H "X-API-Key: dev_test_key_12345" \
  "http://localhost:8000/api/parlays/prebuilt?week=17&min_confidence=58"
```

### 3. Test Mobile App

1. **Home Screen**: Should show top 10 props for Week 17
2. **Parlays Screen**: Should show 6 pre-built parlays
3. **Pull to Refresh**: Swipe down to reload data
4. **Tap to Expand**: Tap on parlays to see individual legs

## Current Week

The app is currently set to **Week 17**. To change this:
1. Edit `src/screens/HomeScreen.tsx` - Line 18: `const [currentWeek] = useState(17);`
2. Edit `src/screens/ParlaysScreen.tsx` - Line 20: `const [currentWeek] = useState(17);`

TODO: Make this dynamic (fetch from backend or user settings).

## API Authentication

All API requests require the `X-API-Key` header:
- Development key: `dev_test_key_12345`
- Production: Use secure key from environment variables

The API service automatically includes this header in all requests.

## Project Structure

```
mobile/
├── src/
│   ├── screens/           # Screen components
│   │   ├── HomeScreen.tsx         # Top 10 props
│   │   ├── ParlaysScreen.tsx      # Pre-built parlays
│   │   ├── BuildScreen.tsx        # Parlay builder (placeholder)
│   │   ├── MyBetsScreen.tsx       # Bet tracking (placeholder)
│   │   └── MoreScreen.tsx         # Settings (placeholder)
│   ├── navigation/        # Navigation setup
│   │   └── AppNavigator.tsx       # Bottom tab navigator
│   ├── services/          # API services
│   │   └── api.ts                 # API client (Axios)
│   ├── types/             # TypeScript types
│   │   └── index.ts               # PropAnalysis, Parlay types
│   └── components/        # Reusable components (future)
├── App.tsx                # Root component
├── package.json           # Dependencies
└── tsconfig.json          # TypeScript config
```

## Troubleshooting

### "Network request failed" Error

**Problem**: Mobile app can't reach the backend API.

**Solutions**:
1. Make sure backend is running: `http://localhost:8000/health`
2. If on physical device, use your computer's local IP (not localhost)
3. Check firewall settings (Windows Defender may block port 8000)
4. Ensure phone and computer are on the same WiFi network

### "X-API-Key header required" Error

**Problem**: API authentication failing.

**Solution**: The API service should automatically include the key. Check `src/services/api.ts` line 18.

### TypeScript Errors

**Problem**: Type errors during development.

**Solution**:
```bash
npm install --save-dev @types/react @types/react-native
```

### Expo Go App Not Loading

**Problem**: QR code scans but app doesn't load.

**Solutions**:
1. Make sure Expo CLI is up to date: `npm install -g expo-cli@latest`
2. Clear Expo cache: `expo start -c`
3. Restart the Expo dev server

## Next Steps

### Immediate (Phase 2 completion):
- [ ] Make current week dynamic
- [ ] Add loading states and error handling improvements
- [ ] Add pull-to-refresh animations
- [ ] Implement search functionality

### Phase 3: Parlay Builder
- [ ] Filter UI (teams, positions, confidence)
- [ ] Add/remove props to custom parlay
- [ ] Live confidence calculation
- [ ] Save/load parlays
- [ ] Line adjustment UI
- [ ] Free tier limits (2-3 parlays)

### Phase 4: Premium Features
- [ ] Push notifications (Firebase)
- [ ] ESPN API post-game grading
- [ ] Payment integration (RevenueCat)
- [ ] Agent customization
- [ ] Post-game analysis screens

## Documentation

See the `docs/` folder for:
- `MOBILE_APP_STRATEGY.md` - Complete mobile app strategy
- `PARLAY_BUILDER_TRACKER_SPEC.md` - Parlay builder specification
- `ESPN_API_POST_GAME_GRADING.md` - Post-game auto-grading spec

## Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review the planning session summary: `docs/SESSION_SUMMARY_2026-01-10.md`
3. Test API endpoints directly with curl
4. Check Expo and React Native docs

---

**Status**: Phase 2 MVP (in progress)
**Last Updated**: 2026-01-10
