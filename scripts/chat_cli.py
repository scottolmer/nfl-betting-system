"""
Natural Language Chat Interface - CLI Entry Point

Usage:
    python scripts/chat_cli.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
load_dotenv(project_root / ".env")

from scripts.analysis.chat_interface import run_chat_interface


def main():
    """Main entry point for chat interface"""
    data_dir = str(project_root / "data")

    try:
        run_chat_interface(data_dir=data_dir)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Chat session ended\n")
        sys.exit(0)
    except ImportError as e:
        print(f"\n[ERROR] Missing dependency: {e}")
        print("\nMake sure you have installed the required packages:")
        print("  pip install anthropic")
        print("\nAlso ensure ANTHROPIC_API_KEY is set in your .env file\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
