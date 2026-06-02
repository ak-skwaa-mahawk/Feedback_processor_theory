// example/minimal_sovereign_app.dart
// Minimal Flutter demo: Button → Mesh.propagateMetric() → BloomPainter + Guard alerts
// Drop this into a new Flutter project that has the ffi + relational_mesh_bridge files.

import 'package:flutter/material.dart';
import 'relational_mesh_bridge.dart';
import 'platform_channel_handler.dart';
import 'sovereign_handshake.dart';

// Simple BloomPainter that reacts to successful soliton propagations
class BloomPainter extends CustomPainter {
  final double intensity;
  final Color color;

  BloomPainter({required this.intensity, this.color = Colors.cyan});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color.withOpacity(intensity.clamp(0.0, 1.0))
      ..style = PaintingStyle.fill;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = 40.0 + (intensity * 60);

    canvas.drawCircle(center, radius, paint);

    // Simple resonance rings
    for (int i = 1; i <= 3; i++) {
      final ringPaint = Paint()
        ..color = color.withOpacity((intensity * 0.6) / i)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;
      canvas.drawCircle(center, radius + (i * 25), ringPaint);
    }
  }

  @override
  bool shouldRepaint(covariant BloomPainter oldDelegate) =>
      intensity != oldDelegate.intensity;
}

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  PlatformChannelHandler.registerHandlers(); // Listen for Python/native calls
  runApp(const SovereignDemoApp());
}

class SovereignDemoApp extends StatefulWidget {
  const SovereignDemoApp({super.key});

  @override
  State<SovereignDemoApp> createState() => _SovereignDemoAppState();
}

class _SovereignDemoAppState extends State<SovereignDemoApp> {
  double _bloomIntensity = 0.0;
  String _status = "Ready — tap to propagate through sovereign core";
  bool _allowed = true;

  @override
  void initState() {
    super.initState();

    // Wire up event callbacks from the hardened Mesh
    Mesh.onSolitonPropagated = (fidelity, resonanceDelta) {
      setState(() {
        _bloomIntensity = (fidelity * 0.8).clamp(0.3, 1.0);
        _status = "✅ Soliton propagated | fidelity: ${fidelity.toStringAsFixed(4)}";
        _allowed = true;
      });
    };

    Mesh.onGuardRejected = (reason) {
      setState(() {
        _bloomIntensity = 0.1;
        _status = "❌ Blocked by 99733-Q Guard: $reason";
        _allowed = false;
      });
    };
  }

  Future<void> _propagateTestMetric() async {
    setState(() {
      _status = "Propagating through sovereign core...";
      _bloomIntensity = 0.3;
    });

    final result = await Mesh.propagateMetric(
      pose: [0.0, 0.0, 0.0],
      stabilityScore: 0.87,
      resonanceDelta: 0.012,
      timestamp: DateTime.now().millisecondsSinceEpoch,
      truth: 0.65,
      indeterminacy: 0.25,
      falsity: 0.10,
    );

    if (!result.allowed) {
      setState(() {
        _status = "❌ Guard rejected: ${result.neutralizedReason}";
        _allowed = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          title: const Text("Sovereign Mesh Demo • 79.79 Hz"),
          backgroundColor: Colors.deepPurple[900],
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Bloom visualizer
              SizedBox(
                width: 220,
                height: 220,
                child: CustomPaint(
                  painter: BloomPainter(intensity: _bloomIntensity),
                ),
              ),
              const SizedBox(height: 40),
              Text(
                _status,
                style: TextStyle(
                  color: _allowed ? Colors.cyanAccent : Colors.redAccent,
                  fontSize: 16,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 30),
              ElevatedButton.icon(
                onPressed: _propagateTestMetric,
                icon: const Icon(Icons.flash_on),
                label: const Text("Propagate Metric Through Guard"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                ),
              ),
              const SizedBox(height: 20),
              TextButton(
                onPressed: () async {
                  await Mesh.triggerConstellationHandshake();
                },
                child: const Text("Trigger GRIP Handshake"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}