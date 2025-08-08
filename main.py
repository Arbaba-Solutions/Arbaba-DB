#!/usr/bin/env python3
"""
Personal Database Application

A command-line tool for managing your notes, ideas, and research
with tagging, searching, and filtering capabilities.

Usage:
    python main.py [command] [options]
    
Examples:
    python main.py init-db                           # Initialize database
    python main.py add-entry "Title" "Content"      # Add new entry
    python main.py list-entries --tag python        # List entries by tag
    python main.py search "keyword"                  # Search entries
    python main.py show "title"                      # Show specific entry
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Main application entry point."""
    try:
        # Import CLI after path setup
        from cli import app
        
        # Check if .env file exists
        env_file = current_dir / '.env'
        if not env_file.exists():
            print("❌ Error: .env file not found!")
            print("Please create a .env file with your database configuration.")
            print("\nExample .env file:")
            print("user=postgres.your_project_id")
            print("password=your_password")
            print("host=aws-0-region.pooler.supabase.com")
            print("port=6543")
            print("dbname=postgres")
            sys.exit(1)
        
        # Run the CLI app
        app()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()