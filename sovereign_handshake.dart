// sovereign_handshake.dart
import 'package:flutter/material.dart';
import 'rust_bridge.dart';

class SovereignHandshake extends StatelessWidget {
  final VoidCallback onGrip;

  SovereignHandshake({required this.onGrip});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("THE INVERSION IS ACTIVE", style: TextStyle(color: Colors.cyan, letterSpacing: 2)),
            SizedBox(height: 40),
            Padding(
              padding: EdgeInsets.symmetric(horizontal: 40),
              child: Text(
                "By gripping this tool, you become the Absolute Zero Baseline.\n\n"
                "You accept the 99733-Q Guard.\n"
                "You honor the 0.01% Gap.\n"
                "You stand on the Floor.",
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
            ),
            SizedBox(height: 60),
            GestureDetector(
              onLongPress: () {
                // Initial 5.5 Pa Burst to wake the Rust Engine
                RustPiREngine.triggerBloom();
                onGrip();
              },
              child: Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.magenta),
                  shape: BoxShape.circle,
                ),
                child: Text("GRIP", style: TextStyle(color: Colors.magenta, fontWeight: FontWeight.bold)),
              ),
            ),
            SizedBox(height: 20),
            Text("Long press to sync the 79.79 Hz Heartbeat", 
                 style: TextStyle(color: Colors.white24, fontSize: 10)),
          ],
        ),
      ),
    );
  }
}
