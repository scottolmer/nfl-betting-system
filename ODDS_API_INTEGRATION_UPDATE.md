# Odds API Integration Update

## Summary
The Odds API now runs on every analysis command to fetch fresh betting lines in real-time.

## Changes Made

### 1. Created Silent Fetcher (`scripts/fetch_odds_silent.py`)
- Fetches odds from The Odds API without verbose output
- Returns boolean success/failure
- Saves data to `betting_lines_wk_X_live.csv`
- Uses 1 API request per call

### 2. Updated CLI (`betting_cli_updated.py`)
Both `analyze` and `parlays` commands now:
1. Fetch fresh odds from The Odds API (1 API request)
2. Save to CSV
3. Proceed with analysis using fresh data

### 3. Created Test Script (`test_odds_api_integration.py`)
Tests the complete integration:
- Environment variable check
- OddsAPI initialization
- API quota verification  
- Silent fetch functionality
- CSV file creation

## API Usage

Each `analyze` command now uses:
- **1 API request** to fetch all current player props

Each `parlays` command now uses:
- **1 API request** to fetch all current player props

## Files Modified/Created

**Modified:**
- `betting_cli.py` → Updated to `betting_cli_updated.py` (review before replacing)

**Created:**
- `scripts/fetch_odds_silent.py` - Silent odds fetcher
- `test_odds_api_integration.py` - Integration test script

## Testing

Run the test script to verify everything works:
```bash
python test_odds_api_integration.py
```

Expected output:
- ✅ ODDS_API_KEY found
- ✅ OddsAPI initialized
- ✅ API connection working
- ✅ Silent fetch successful
- ✅ CSV file created

## Usage Flow

**Before (old way):**
```
analyze Jordan Love 250 pass yards
→ Uses whatever CSV data existed
```

**After (new way):**
```
analyze Jordan Love 250 pass yards
→ 📡 Fetches fresh odds from API
→ ✅ Fresh odds loaded
→ 🔄 Analyzes with current data
```

## API Quota Management

The Odds API typically provides:
- **500 requests per month** (free tier)
- **~16 requests per day** if used daily

With this integration:
- Each analysis = 1 request
- Each parlay generation = 1 request
- Quota checked before each fetch
- Graceful fallback to existing data if API fails

## Next Steps

1. **Test the integration:**
   ```bash
   python test_odds_api_integration.py
   ```

2. **Review the updated CLI:**
   - Compare `betting_cli.py` vs `betting_cli_updated.py`
   - Backup original if needed
   - Rename updated version to replace original

3. **Test a live analysis:**
   ```bash
   python betting_cli_updated.py
   analyze Jordan Love 250 pass yards
   ```

## Error Handling

The system includes graceful fallbacks:
- If API fails → Uses existing CSV data
- If API returns no data → Uses existing CSV data  
- If API key missing → Shows clear error message

## Notes

- The silent fetcher suppresses verbose output for better UX
- CSV files are timestamped with fetch time
- Each fetch overwrites the previous week's live data
- The system automatically loads the most recent betting lines file
