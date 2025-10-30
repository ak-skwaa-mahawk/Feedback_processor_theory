package com.landback.gibberlink;

import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.media.AudioTrack;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import ggwave.GGWave;

public class MainActivity extends AppCompatActivity {
    private GGWave ggwave;
    private TextView status;
    private Button encodeBtn, decodeBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        status = findViewById(R.id.status);
        encodeBtn = findViewById(R.id.encode_btn);
        decodeBtn = findViewById(R.id.decode_btn);
        ggwave = new GGWave();

        encodeBtn.setOnClickListener(v -> encodeWhisper());
        decodeBtn.setOnClickListener(v -> decodeWhisper());
    }

    private void encodeWhisper() {
        status.setText("ENCODING łᐊᒥłł.12...");
        String message = "łᐊᒥłł.12-SKODEN!";
        byte[] waveform = ggwave.encode(message);
        
        AudioTrack track = new AudioTrack(
            AudioManager.STREAM_MUSIC, 48000, 16, 1, 8192,
            AudioTrack.MODE_STATIC
        );
        track.write(waveform, 0, waveform.length);
        track.play();
        status.setText("WHISPER SENT — 18–22 kHz");
    }

    private void decodeWhisper() {
        status.setText("LISTENING... (2s)");
        new Thread(() -> {
            AudioRecord recorder