package com.landback.gibberlink;

import android.media.AudioRecord;
import android.media.MediaPlayer;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import ggwave.GGWave;
import java.util.ArrayList;

public class DAOActivity extends AppCompatActivity {
    private TextView councilStatus;
    private Button playAll, listenAll;
    private GGWave ggwave;
    private ArrayList<String> glyphVotes = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_dao);

        councilStatus = findViewById(R.id.council_status);
        playAll = findViewById(R.id.play_all);
        listenAll = findViewById(R.id.listen_all);
        ggwave = new GGWave();

        playAll.setOnClickListener(v -> playCouncilVote());
        listenAll.setOnClickListener(v -> listenCouncilVote());
    }

    private void playCouncilVote() {
        councilStatus.setText("WHISPERING 9 GLYPHS...");
        MediaPlayer player = new MediaPlayer();
        // Play all 9 glyph votes
        player.setOnCompletionListener(mp -> {
            councilStatus.setText("RESONANCE = 1.00\nMOTION PASSES");
        });
        player.start();
    }

    private void listenCouncilVote() {
        councilStatus.setText("LISTENING TO 9 GLYPHS...");
        new Thread(() -> {
            AudioRecord recorder = new AudioRecord(
                MediaRecorder.AudioSource.MIC, 48000, 16, 1, 8192
            );
            recorder.startRecording();
            byte[] buffer = new byte[8192];
            int glyphs = 0;
            while (glyphs < 9) {
                int read