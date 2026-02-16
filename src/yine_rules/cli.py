"""
Command-line interface for Yine corpus conditioning and rule engine utilities.
"""
from __future__ import annotations
import argparse
import logging
from pathlib import Path

from yine_rules.settings import Settings
from yine_rules.utils.logging import setup_logging
from yine_rules.preprocessing.conditioning_pipeline import run_conditioning

log = logging.getLogger("yine_rules")

def build_parser() -> argparse.ArgumentParser:
    """
    Construye el parser de argumentos para la CLI.
    
    :return: El parser de argumentos configurado.
    :rtype: ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="yine-rules",
        description="Yine corpus conditioning + rule engine utilities"
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # condition subcommand
    condition_parser = subparsers.add_parser("condition", help="Run corpus conditioning pipeline")
    condition_parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to main config yaml"
    )
    condition_parser.add_argument(
        "--logging-config",
        type=str,
        default="configs/logging.yaml",
        help="Path to logging yaml"
    )

    return parser

def main():
    """
    Main function for the Yine command-line interface.
    """
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(args.logging_config if Path(args.logging_config).exists() else None)

    settings = Settings.load(args.config).config

    if args.cmd == "condition":
        run_conditioning(settings)
    else:
        raise SystemExit(f"Unknown command: {args.cmd}")

if __name__ == "__main__":
    main()
