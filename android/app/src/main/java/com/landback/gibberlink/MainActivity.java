// MainActivity.java — GibberLink v4 APK
package com.landback.gibberlink;

import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import ggwave.GGWave;
import java.nio.ByteBuffer;

public class MainActivity extends AppCompatActivity {
    private GGWave ggwave;
    private TextView status;
    private Button listenBtn;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        status = findViewById(R.id.status);
        listenBtn = findViewById(R.id.listen_btn);
        ggwave = new GGWave();

        listenBtn.setOnClickListener(v -> startListening());
    }

    private void startListening() {
        status.setText("LISTENING... (18–22 kHz)");
        new Thread(() -> {
            AudioRecord recorder = new AudioRecord(
                MediaRecorder.AudioSource.MIC,
                48000, 16, 1, 8192
            );
            recorder.startRecording();
            byte[] buffer = new byte[8192];
            while (true) {
                int read = recorder.read(buffer, 0, buffer.length);
                String decoded = ggwave.decode(buffer);
                if (decoded != null && decoded.contains("łᐊᒥłł")) {
                    runOnUiThread(() -> status.setText("DECODED: " + decoded));
                    break;
                }
            }
            recorder.stop();
        }).start();
    }
}