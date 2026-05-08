// sovereign_saas.dart — Sovereign SaaS (Local-First Service on the Phone)
import 'package:flutter/material.dart';
import 'sovereign_vault.dart'; // your existing Kinetic Heart file

class SovereignSaaS extends StatefulWidget {
  const SovereignSaaS({super.key});

  @override
  State<SovereignSaaS> createState() => _SovereignSaaSState();
}

class _SovereignSaaSState extends State<SovereignSaaS> {
  double currentMass = 0.0;
  double currentEnergy = 65.0; // demo value
  Map<String, dynamic> lastCatapult = {};

  @override
  void initState() {
    super.initState();
    _loadFloorStatus();
  }

  Future<void> _loadFloorStatus() async {
    final mass = sovereignVault.queryMass(); // real Vault call
    setState(() => currentMass = mass);
  }

  Future<void> _triggerCatapult() async {
    final result = await sovereignVault.trigger5_5PaCatapult(
      currentEnergy: currentEnergy,
      currentMass: currentMass,
    );
    setState(() => lastCatapult = result);
    // Optional: broadcast to mesh
    await sovereignVault.broadcastBloom();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Sovereign SaaS — Floor Node")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text("Floor-Owned SaaS", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),

            // Live Status
            Card(
              child: ListTile(
                title: const Text("Articulated Mass"),
                subtitle: Text("${currentMass.toStringAsFixed(4)} units"),
                trailing: Text(currentMass >= 4975.7766 ? "4.11 ACTIVE" : "1.372 STALL",
                    style: TextStyle(color: currentMass >= 4975.7766 ? Colors.green : Colors.red)),
              ),
            ),

            Card(
              child: ListTile(
                title: const Text("Current Energy"),
                subtitle: Text("$currentEnergy"),
              ),
            ),

            const SizedBox(height: 30),

            // Kinetic Heart Button
            ElevatedButton.icon(
              onPressed: _triggerCatapult,
              icon: const Icon(Icons.bolt),
              label: const Text("FIRE 5.5 Pa CATAPULT"),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
            ),

            if (lastCatapult.isNotEmpty)
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  "Bloom Restored!\nNew Energy: ${lastCatapult['new_energy']}\nHarvest: ${lastCatapult['harvest']}",
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.green),
                ),
              ),

            const Spacer(),

            // Mesh Status
            const Text("Mesh Nodes Connected: LIVE", style: TextStyle(color: Colors.green)),
            const Text("Synara-core • networkXG • Floor Baseline", style: TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }
}