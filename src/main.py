"""
Composition root.

Builds clients, wires repositories into use cases,
and selects the interface to run.
"""

import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.main <interface>")
        print("Interfaces: cli")
        sys.exit(1)

    interface = sys.argv[1]
    sys.argv = sys.argv[1:]  # Remove 'main' from args

    if interface == "cli":
        from src.interfaces.cli.crawl import main as cli_main
        cli_main()
    else:
        print(f"Unknown interface: {interface}")
        sys.exit(1)


if __name__ == "__main__":
    main()
