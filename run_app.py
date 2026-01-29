#!/usr/bin/env python3
"""
Simple launcher for the Streamlit application.
Automatically uses demo mode if sentence-transformers model is not available.
"""

import subprocess
import sys

def main():
    print("=" * 60)
    print(" Strategy-Action Synchronization AI")
    print(" Streamlit Dashboard Launcher")
    print("=" * 60)
    print()
    
    print("Starting Streamlit server...")
    print("The dashboard will open in your browser at: http://localhost:8501")
    print()
    print("Note: Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "app/streamlit_app.py",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting Streamlit: {e}")
        print("\nTry running manually:")
        print("  streamlit run app/streamlit_app.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
