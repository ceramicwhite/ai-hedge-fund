#!/usr/bin/env python3
"""
Command-line entry point for launching the AI Hedge Fund Gradio UI.
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Parse command line arguments and launch the Gradio UI."""
    parser = argparse.ArgumentParser(description="Launch the AI Hedge Fund Gradio UI")
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the Gradio server on (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a shareable link accessible over the internet"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode with additional logging"
    )
    
    args = parser.parse_args()
    
    # Set debug mode if specified
    if args.debug:
        os.environ["GRADIO_DEBUG"] = "1"
        print("Debug mode enabled")
    
    try:
        # Import the Gradio app
        from gui.gradio_app import create_ui
        
        # Create and launch the UI with simplified server settings
        # to avoid Pydantic schema validation errors
        app = create_ui()
        app.launch(
            server_name="127.0.0.1",      # Use localhost
            server_port=args.port,        # Use CLI port argument
            share=args.share,             # Use CLI share argument
            inbrowser=True,
            prevent_thread_lock=True,     # Prevent thread locking issues
            show_api=False,               # Disable API docs that use Pydantic
            max_threads=1                 # Limit concurrency to avoid issues
        )
    
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure you've installed all required dependencies:")
        print("  poetry install")
        print("  # Or if you're not using Poetry:")
        print("  pip install -e .")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error launching UI: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()