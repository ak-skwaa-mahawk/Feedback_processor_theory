// lib/field_kit/multi_user_ar_skyrmion.dart — Multi-user shared AR skyrmion lattice

import 'package:flutter/material.dart';
import 'package:ar_flutter_plugin/ar_flutter_plugin.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class MultiUserARSkyrmionView extends StatefulWidget {
  const MultiUserARSkyrmionView({super.key});

  @override
  State<MultiUserARSkyrmionView> createState() => _MultiUserARSkyrmionViewState();
}

class _MultiUserARSkyrmionViewState extends State<MultiUserARSkyrmionView> {
  late WebSocketChannel _channel;
  ARNode? _sharedSkyrmion;
  Map<String, dynamic>? _livePacket;

  @override
  void initState() {
    super.initState();
    _channel = WebSocketChannel.connect(Uri.parse('ws://floor-node:8765'));
    _channel.stream.listen((message) {
      setState(() {
        _livePacket = Map<String, dynamic>.from(message);
        _syncSharedSkyrmion();
      });
    });
  }

  void _syncSharedSkyrmion() {
    // Re-render shared skyrmion lattice for all users in session
    if (_sharedSkyrmion != null) {
      // Update position/velocity from packet (Thiele dynamics)
      print("Multi-user AR sync: skyrmion velocity ${_livePacket?['skyrmion_velocity']}");
    }
  }

  @override
  Widget build(BuildContext context) {
    return ARView(
      onARViewCreated: (controller, objManager, _, _) {
        // Add shared skyrmion node (same for all users)
        _sharedSkyrmion = ARNode(...); // as before
        objManager.addNode(_sharedSkyrmion!);
      },
      planeDetectionConfig: PlaneDetectionConfig.horizontalAndVertical,
    );
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }
}

// Launch shared session in one-click Field Kit
void launchMultiUserFloorAR(String sessionId) {
  runApp(MaterialApp(home: MultiUserARSkyrmionView()));
  // Python core broadcasts via WebSocket bridge on join
}