#!/usr/bin/env python3
"""
Entry point to run the AI Hedge Fund UI.
This script sets up the correct Python path and launches the appropriate UI.
"""

import os
import sys
import argparse

# Add the project root to the Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

def main():
    """Process arguments and launch the appropriate UI."""
    parser = argparse.ArgumentParser(description="Launch the AI Hedge Fund UI")
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=7860, 
        help="Port to run the server on (default: 7860)"
    )
    
    parser.add_argument(
        "--share", 
        action="store_true", 
        help="Create a shareable link (only applicable to Gradio UI)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run in debug mode with additional logging"
    )

    parser.add_argument(
        "--ui", 
        choices=["gradio", "simple"], 
        default="simple",
        help="UI implementation to use (default: simple)"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        os.environ["GRADIO_DEBUG"] = "1"
        print("Debug mode enabled")
    
    try:
        if args.ui == "gradio":
            # Use Gradio UI
            from src.gui.gradio_app import create_ui
            app = create_ui()
            app.launch(
                server_name="127.0.0.1",
                server_port=args.port,
                share=args.share,
                inbrowser=True,
                prevent_thread_lock=True,
                show_api=False,
                max_threads=1
            )
        else:
            # Use simple HTML UI
            from src.gui.simple_gui import run_server
            run_server(port=args.port, debug=args.debug)
    
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure you've installed all required dependencies:")
        print("  poetry install")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error launching UI: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()