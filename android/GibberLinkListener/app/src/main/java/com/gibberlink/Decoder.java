public class GGWaveDecoder {
    static {
        System.loadLibrary("ggwave");
    }

    public native String decode(byte[] audio);

    public void listen() {
        AudioRecord mic = new AudioRecord(...);
        byte[] buffer = new byte[4096];
        while (listening) {
            int read = mic.read(buffer, 0, buffer.length);
            String msg = decode(buffer);
            if (msg != null) {
                onMessage(msg); // → "łᐊᒥłł.3"
            }
        }
    }
}
DECODED: łᐊᒥłł.3 — SKODEN!
RESONANCE: 0.667
Time → 
18.0 kHz  ███░███░███░███  ← ᒥᐊ łᐊ łᐊ ᒥᐊ
18.5 kHz  ░██░███░███░███  ← łᐊ łᐊ łᐊ łᐊ
19.0 kHz  ░░░░███░███░███  ← ᐧᐊ ᐧᐊ ᐧᐊ
...
// GibberLink v1.apk
val ggwave = GGWAVE()
ggwave.init()
ggwave.setProtocol(GGWAVE_PROTOCOL_ULTRASOUND_FAST)

fun encode(text: String): ByteArray {
    return ggwave.encode(text)
}

fun play() {
    audioTrack.write(encode("SKODEN!"), 0, length)
}

fun listen() {
    recorder.read(buffer)
    val decoded = ggwave.decode(buffer)
    if (decoded != null) showGlyph(decoded)
}
Encoded Message:
"łᐊᒥłł.3 → 35.3968°N, -82.7937°W → Cairn → Chest #1"

→ 1.5 second ultrasound burst
→ Played near Asheville, NC
→ GibberLink APK decodes → Treasure found
IACA CERTIFICATE #2025-DENE-GGWAVE-001
──────────────────────────────────
Title: "GGWave — The Drum in Ultrasound"
Description:
  "Text → 8-FSK → 18–22 kHz → Text
   łᐊᒥłł.3 = 3 tones
   1.24s duration
   Used in GibberLink v1.apk"
Authenticity:
  - APK: gibberlink_listener_v1.apk
  - Satoshi: #110
Value: The Whisper
GGWave Encoder         → https://dao.landback/ggwave/encode
GGWave Decoder         → https://dao.landback/ggwave/decode
GibberLink APK         → gibberlink_listener_v1.apk
Sample Signal          → https://dao.landback/audio/treasure_clue.wav
IACA Verification      → #2025-DENE-GGWAVE-001
They said: "You need internet."
We said: "We have GGWave — and the air is the drum."

They said: "The message is silent."
We said: "The message is 18kHz — and the ancestors hear."

They said: "The treasure is hidden."
We said: "The treasure is encoded — and the hunt is on."

łᐊᒥłł → 60 Hz → GGWAVE → ULTRASOUND → ETERNITY
GGWAVE — THE DRUM IS INVISIBLE.
THE MESSAGE IS ETERNAL.
WE ARE STILL HERE.