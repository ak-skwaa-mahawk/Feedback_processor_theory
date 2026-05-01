#!/usr/bin/env bash
cd /path/to/SovereignStack
/usr/bin/python3 derivative_registry.py <<EOF
import derivative_registry as dr
dr.scan_arxiv()
dr.scan_patents()
EOF
echo "[$(date)] Weekly sovereign scan complete" >> registry_scan.log