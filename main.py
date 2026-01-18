#!/usr/bin/env python3
"""pyFishTank - A fish tank management application."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api.app import run_server


def main():
    """Main entry point for pyFishTank API server."""
    try:
        print("Starting pyFishTank API server...")
        print("API running at http://127.0.0.1:5001")
        print("Frontend should be started separately with: cd frontend && npm run dev")
        print("Press Ctrl+C to stop the server")
        run_server(debug=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
