// lib/platform_channel_handler.dart
// Handles incoming MethodChannel calls from Python backend or native platform.
// This is the "Rust ← Dart ← Python" direction.

import 'package:flutter/services.dart';
import 'relational_mesh_bridge.dart';

class PlatformChannelHandler {
  static const _channel = MethodChannel('networkxg/relational_mesh');

  static void registerHandlers() {
    _channel.setMethodCallHandler(_handleMethodCall);
    print("📡 PlatformChannelHandler registered for networkxg/relational_mesh");
  }

  static Future<dynamic> _handleMethodCall(MethodCall call) async {
    switch (call.method) {
      case 'startRelationalMesh':
        print("📡 Python requested: startRelationalMesh");
        await Mesh.initialize();
        return {'status': 'ok', 'message': 'Relational mesh started'};

      case 'propagateSoliton':
        print("📡 Python sent soliton propagation event");
        final args = call.arguments as Map?;
        if (args != null) {
          // You can react here (e.g. update UI state, trigger BloomPainter, etc.)
          print("   fidelity: ${args['fidelity']}, resonance: ${args['resonance']}");
        }
        return {'status': 'received'};

      case 'constellationHandshake':
        print("📡 Python requested constellation handshake");
        await Mesh.triggerConstellationHandshake();
        return {'status': 'grip_sealed'};

      case 'run_fpt_omega_cycle':
        print("📡 Python requested Trinity cycle");
        final tIf = (call.arguments as Map?)?['t_i_f'] as Map<String, double>? ?? {};
        final result = await Mesh.runTrinityCycle(tIf);
        return {
          'w_state': result.wState,
          'fidelity': result.fidelity,
        };

      default:
        print("⚠️ Unknown MethodChannel call: ${call.method}");
        return {'status': 'error', 'message': 'Unknown method'};
    }
  }
}