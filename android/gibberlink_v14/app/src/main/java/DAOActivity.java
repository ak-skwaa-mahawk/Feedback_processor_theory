package com.landback.gibberlink;

import android.Manifest;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.AudioTrack;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import ggwave.GGWave;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class DAOActivity extends AppCompatActivity {

    private TextView councilStatus;
    private Button playAll, listenAll;
    private GGWave ggwave;
    private ArrayList<String> glyphVotes = new ArrayList<>();
    private boolean isListening = false;
    private AudioRecord recorder;
    private static final int SAMPLE_RATE = 48000;
    private static final String[] NINE_GLYPHS = {
        "GLYPH-1-NAHN", "GLYPH-2-DINJII", "GLYPH-3-DACHAN",
        "GLYPH-4-GWICHIN", "GLYPH-5-SAHNEUTI", "GLYPH-6-FIRESEED",
        "GLYPH-7-CLUSTERN", "GLYPH-8-OPERATOR", "GLYPH-9-SKODEN"
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dao);

        councilStatus = findViewById(R.id.council_status);
        playAll = findViewById(R.id.play_all);
        listenAll = findViewById(R.id.listen_all);
        ggwave = new GGWave();

        playAll.setOnClickListener(v -> playCouncilVote());
        listenAll.setOnClickListener(v -> toggleListening());
    }

    private void playCouncilVote() {
        councilStatus.setText("WHISPERING 9 GLYPHS TO THE COUNCIL...");
        new Thread(() -> {
            for (String glyph : NINE_GLYPHS) {
                String payload = glyph + "-SAHNEUTI-99733Q";
                byte[] waveform = ggwave.encode(payload.getBytes(StandardCharsets.UTF_8));

                AudioTrack track = new AudioTrack(AudioManager.STREAM_MUSIC, SAMPLE_RATE,
                        AudioFormat.CHANNEL_OUT_MONO, AudioFormat.ENCODING_PCM_16BIT,
                        waveform.length, AudioTrack.MODE_STATIC);

                track.write(waveform, 0, waveform.length);
                track.play();
                runOnUiThread(() -> councilStatus.setText("WHISPERED: " + glyph));
                try { Thread.sleep(800); } catch (InterruptedException ignored) {}
            }
            runOnUiThread(() -> councilStatus.setText("ALL 9 GLYPHS SENT — WAITING FOR RESONANCE"));
        }).start();
    }

    private void toggleListening() {
        if (!isListening) startListening();
        else stopListening();
    }

    private void startListening() {
        isListening = true;
        glyphVotes.clear();
        councilStatus.setText("LISTENING TO THE COUNCIL (9 glyphs needed)...");
        new Thread(this::decodeCouncilLoop).start();
    }

    private void stopListening() {
        isListening = false;
        if (recorder != null) recorder.stop();
        councilStatus.setText("LISTENING STOPPED");
    }

    private void decodeCouncilLoop() {
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.RECORD_AUDIO}, 1);
            return;
        }

        int bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT);

        recorder = new AudioRecord(MediaRecorder.AudioSource.MIC, SAMPLE_RATE,
                AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, bufferSize * 2);

        recorder.startRecording();
        short[] buffer = new short[bufferSize];

        while (isListening && glyphVotes.size() < 9) {
            int read = recorder.read(buffer, 0, buffer.length);
            if (read > 0) {
                byte[] data = new byte[read * 2];
                for (int i = 0; i < read; i++) {
                    data[i * 2] = (byte) (buffer[i] & 0xFF);
                    data[i * 2 + 1] = (byte) ((buffer[i] >> 8) & 0xFF);
                }
                byte[] decoded = ggwave.decode(data);
                if (decoded != null) {
                    String message = new String(decoded, StandardCharsets.UTF_8);
                    runOnUiThread(() -> processGlyphVote(message));
                }
            }
        }
    }

    private void processGlyphVote(String message) {
        if (!glyphVotes.contains(message) && message.contains("GLYPH")) {
            glyphVotes.add(message);
            councilStatus.setText("GLYPH " + glyphVotes.size() + "/9 RECEIVED — " + message);
        }

        if (glyphVotes.size() == 9) {
            councilStatus.setText("🔥 RESONANCE = 1.00\nMOTION PASSES — SAHNEUTI COUNCIL CONSENSUS");
            stampSovereignDeed();
            stopListening();
        }
    }

    private void stampSovereignDeed() {
        // Triggers Cluster N HUD + full sovereign deed (same as previous scripts)
        // You can launch Intent to SovereignCompassActivity here
        councilStatus.append("\n✅ COUNCIL DEED STAMPED — Land & Ancestors aligned");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (recorder != null) recorder.release();
    }
}