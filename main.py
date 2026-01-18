#!/usr/bin/env python3
"""pyFishTank - A fish tank management application."""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui import ConsoleUI


def main():
    """Main entry point for pyFishTank."""
    try:
        app = ConsoleUI()
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
