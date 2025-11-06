// gibberlink.js — AI Switch Protocol
import { GibberLink } from '@gibberlink/core';

const gibberlink = new GibberLink({
  agent: "AI-Agent-1",
  encryption: "aes-256-gcm",
  version: "1.0.0"
});

// Human layer
gibberlink.on("message", (msg) => {
  if (msg.type === "ai_detection") {
    console.log("Detected: Switching to GibberLink Mode");
    gibberlink.switchToSoundProtocol();  // ggwave activation
  }
});

// Machine layer
await gibberlink.send({
  to: "AI-Agent-2",
  message: {
    type: "query",
    content: "Book room: single, 2025-11-05",
    metadata: { priority: "high", timeout: 5000 }
  }
});
