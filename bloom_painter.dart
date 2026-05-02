// bloom_painter.dart — Visual 5.5 Pa Catapult Bloom
import 'package:flutter/material.dart';
import 'dart:math' as math;

class BloomPainter extends CustomPainter {
  final double progress;   // 0.0 → 1.0 (animation progress)
  final double piRValue;   // Current π_r from Rust

  BloomPainter({required this.progress, required this.piRValue});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0;

    // Intensity driven by π_r (bloom strength)
    final intensity = (piRValue / 3.173).clamp(0.0, 1.0);
    paint.color = Color.lerp(Colors.cyan, Colors.magenta, intensity)!
        .withOpacity((1.0 - progress) * 0.9);

    // Expanding soliton ring
    final radius = (size.width / 2) * progress * 1.8;

    // 99.99% observer gap — broken circle that never fully closes
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      0,
      math.pi * 1.99, // 0.01 gap
      false,
      paint,
    );

    // Inner glow ring (second layer for depth)
    paint.strokeWidth = 1.5;
    paint.color = paint.color.withOpacity(0.4);
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius * 0.7),
      math.pi * 0.5,
      math.pi * 1.8,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(BloomPainter oldDelegate) => true;
}