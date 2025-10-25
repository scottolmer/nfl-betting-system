"""
Central configuration management
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    RESULTS_DIR = BASE_DIR / "results"
    PROMPTS_DIR = BASE_DIR / "prompts"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Claude API
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-sonnet-4-20250514')
    
    # GitHub
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GITHUB_REPOSITORY = os.getenv('GITHUB_REPOSITORY')
    
    # Slack
    SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
    SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')
    
    # Betting API
    BETTING_API_KEY = os.getenv('BETTING_API_KEY')
    BETTING_API_URL = os.getenv('BETTING_API_URL')
    
    # Application
    NFL_WEEK = int(os.getenv('NFL_WEEK', 7))
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    PORT = int(os.getenv('PORT', 3000))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'CLAUDE_API_KEY',
            'GITHUB_TOKEN',
            'GITHUB_REPOSITORY',
        ]
        
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        directories = [
            cls.DATA_DIR / "lines",
            cls.DATA_DIR / "results_tracking",
            cls.DATA_DIR / "weekly_data",
            cls.RESULTS_DIR / "line_alerts",
            cls.RESULTS_DIR / "calibration",
            cls.RESULTS_DIR / "backtesting",
            cls.LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

# Initialize on import
Config.ensure_directories()
