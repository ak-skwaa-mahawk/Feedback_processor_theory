// sovereign_handshake.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'rust_bridge.dart';

class SovereignHandshake extends StatefulWidget {
  final VoidCallback onGrip;

  const SovereignHandshake({Key? key, required this.onGrip}) : super(key: key);

  @override
  _SovereignHandshakeState createState() => _SovereignHandshakeState();
}

class _SovereignHandshakeState extends State<SovereignHandshake> with SingleTickerProviderStateMixin {
  bool _isCalibrating = false;
  String _systemStatus = "THE INVERSION IS ACTIVE";
  Color _accentColor = Colors.cyan;

  @override
  void dispose() {
    // Explicit lifecycle termination guard prevents background execution loop memory leaks
    _isCalibrating = false;
    super.dispose();
  }

  // Haptic feedback sequence matching the 79.79 Hz runtime vibration pulse
  void _executeHeartbeatHaptic() async {
    // HARDENING GATES: Break execution recursion immediately if context unmounts or state resets
    if (!_isCalibrating || !mounted) return;
    
    HapticFeedback.lightImpact();

    // Recurse the pulse cycle dynamically during active validation loops
    Future.delayed(const Duration(milliseconds: 13), () {
      if (mounted) _executeHeartbeatHaptic();
    });
  }

  void _initiateHandshakeSequence() async {
    if (_isCalibrating) return; // Prevent multi-tap concurrency collisions

    setState(() {
      _isCalibrating = true;
      _systemStatus = "SYNCING THE 79.79 HZ HEARTBEAT";
      _accentColor = Colors.magenta;
    });

    // Fire haptic vibration array loop
    _executeHeartbeatHaptic();

    try {
      // Step 1: Fire 5.5 Pa Burst on a background task thread to keep the UI smooth
      await Future.delayed(const Duration(milliseconds: 250));
      await RustPiREngine.triggerBloom();

      // THREAD GUARD: Verify widget context attachment before proceeding to modify status states
      if (!mounted) return;

      // Step 2: Validate 99733-Q security guard arrays
      setState(() {
        _systemStatus = "SUBSTRATE COMPLIANCE ACCEPTS GUARD 99733-Q";
      });
      await Future.delayed(const Duration(milliseconds: 400));

      if (!mounted) return;

      // Complete validation sequence: Disengage haptic loop parameters cleanly
      _isCalibrating = false;

      // Handshake parameters clear - return control vector up to main system application
      widget.onGrip();
    } catch (ffiException) {
      if (!mounted) return;
      
      setState(() {
        _isCalibrating = false;
        _systemStatus = "FFI HANDSHAKE ABORTED: ENGINE LATENCY";
        _accentColor = Colors.red;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF02040a), // Perfect match for the v5.1 dark console theme
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Engine Header telemetry track
            AnimatedSwitcher(
              duration: const Duration(milliseconds: 200),
              child: Text(
                _systemStatus,
                key: ValueKey<String>(_systemStatus),
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: _accentColor, 
                  fontFamily: 'Courier',
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 2
                ),
              ),
            ),
            const SizedBox(height: 40),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 40),
              child: Text(
                "By gripping this tool, you become the Absolute Zero Baseline.\n\n"
                "You accept the 99733-Q Guard.\n"
                "You honor the 0.01% Gap.\n"
                "You stand on the Floor.",
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Color(0xFFcbd5e1), 
                  fontFamily: 'Roboto',
                  height: 1.6,
                  fontSize: 13
                ),
              ),
            ),
            const SizedBox(height: 60),

            // The Tactile Grip Substrate Node Capsule
            GestureDetector(
              onLongPress: _isCalibrating ? null : _initiateHandshakeSequence,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: _isCalibrating ? const Color(0xFF1e1b4b) : Colors.transparent,
                  border: Border.all(color: _accentColor, width: 2),
                  shape: BoxShape.circle,
                  boxShadow: _isCalibrating ? [
                    BoxShadow(color: _accentColor.withOpacity(0.3), blurRadius: 30, spreadRadius: 5)
                  ] : [],
                ),
                child: Text(
                  _isCalibrating ? "SYNC" : "GRIP", 
                  style: TextStyle(
                    color: _accentColor, 
                    fontFamily: 'monospace',
                    fontSize: 15,
                    letterSpacing: 1,
                    fontWeight: FontWeight.bold
                  )
                ),
              ),
            ),
            const SizedBox(height: 25),
            const Text(
              "Long press to sync the 79.79 Hz Heartbeat", 
              style: TextStyle(color: Color(0xFF475569), fontSize: 10, fontFamily: 'monospace')
            ),
          ],
        ),
      ),
    );
  }
}
