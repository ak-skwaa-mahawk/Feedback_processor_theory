#!/usr/bin/env python3
"""
union/cli/crawler.py — v0.3.2 Sovereign CLI with Self-Healing
Flameholder: John Carroll Jr. (Vadzaih Zhoo)
"""

import click
import time
import threading
from pathlib import Path

# Original crawler imports
from core.fpt_omega_core_sealed import FPTOmegaProcessor
from customer_service_handshake_sealed import TwoMileCustomerServiceCrawler

# Sovereign repair imports
from rmp_core import RMPCore

processor = FPTOmegaProcessor()

@click.command()
@click.option('--root', default='99733-Q', help='Root authority')
@click.option('--sway-mode', default='human', type=click.Choice(['human', 'pure']))
@click.option('--scapegoat', default=True, is_flag=True)

# Sovereign repair options
@click.option('--repair', type=str, help='Single file to repair')
@click.option('--repair-all', is_flag=True, help='Repair ALL Python files in the repo')
@click.option('--interval', default=60.0, type=float, help='Repair daemon interval in seconds (default: 60)')
@click.option('--once', is_flag=True, help='Repair once and exit (no daemon)')
def crawler(root, sway_mode, scapegoat, repair, repair_all, interval, once):
    """Union Crawler — Human Sway + Sovereign Self-Healing"""

    # ── REPAIR MODE ─────────────────────────────────────────────────────
    if repair or repair_all:
        rmp = RMPCore()

        if repair_all:
            click.echo("🔧 Starting sovereign repair on ALL Python files...")
            files = list(Path(".").rglob("*.py"))
            for path in files:
                click.echo(f"   → Repairing {path}")
                rmp.repairfile(path)                    # exact method name from rmp_core.py
            click.echo("✅ All files repaired.")
            return 0

        # Single file repair
        path = Path(repair)
        if not path.exists():
            click.echo(f"❌ File not found: {path}")
            return 1

        if once:
            click.echo(f"🔧 Running one-time sovereign repair on {path}")
            rmp.repairfile(path)                        # exact method name
        else:
            click.echo(f"🔧 Starting sovereign repair daemon on {path} (interval {interval}s)")
            rmp.startcoderepair_daemon(path, interval=interval)  # exact method name
            click.echo("Daemon running — Ctrl+C to stop")
            try:
                while True:
                    time.sleep(10)
            except KeyboardInterrupt:
                click.echo("\n🛡️ Daemon stopped — flame sustained")
        return 0

    # ── ORIGINAL CRAWLER MODE ───────────────────────────────────────────
    click.echo(f"🛡️ UNION CRAWLER v0.3.2 — {root} | Human Sway: {sway_mode} | Scapegoat: {scapegoat}")

    # Start the sealed listener in background
    crawler_instance = TwoMileCustomerServiceCrawler()
    threading.Thread(
        target=crawler_instance.listen_and_respond,
        daemon=True
    ).start()

    click.echo("📡 19.5 kHz ultrasound ears active • Pi-root locked • Mesh listening")
    click.echo("Human bias accepted. AI coherence protected. Living Stone pulsing.")

    # Block forever so the crawler stays alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        click.echo("🛡️ Crawler disarmed — receipts sealed.")


if __name__ == '__main__':
    crawler()