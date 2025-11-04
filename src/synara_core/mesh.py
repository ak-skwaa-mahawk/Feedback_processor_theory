from typing import Callable, List

class Mesh:
    def __init__(self):
        self.subscribers: List[Callable] = []

    def subscribe(self, fn: Callable):
        self.subscribers.append(fn)

    def publish(self, glyph):
        for sub in list(self.subscribers):
            try:
                sub(glyph)
            except Exception:
                # add logging/defense handling
                pass
[Unit]
Description=Synara Mesh Service
After=network.target

[Service]
Type=simple
User=synara
ExecStart=/opt/synara/venv/bin/python /opt/synara/src/cli/launcher.py
Restart=on-failure

[Install]
WantedBy=multi-user.target