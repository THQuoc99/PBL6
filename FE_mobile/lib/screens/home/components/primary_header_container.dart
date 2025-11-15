import 'package:flutter/material.dart';

import 'package:flutter_app/screens/home/components/circular_container.dart ';
import 'package:flutter_app/screens/home/components/curved_edges_widget.dart';

class PrimaryHeaderContainer extends StatelessWidget {
  final Widget child;
  const PrimaryHeaderContainer({
    super.key,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return CurvedEdgeWidget(
      child: Container(
        color: Colors.blueAccent,
        child: Stack(
          children: [
            Positioned(
              top: -150,
              right: -250,
              child: CircularContainer(
                color: Colors.white.withValues(alpha: 0.3),
              ),
            ),
            Positioned(
              top: 100,
              right: -300,
              child: CircularContainer(
                color: Colors.white.withValues(alpha: 0.3),
              ),
            ),
            child,
          ],
        ),
      ),
    );
  }
}
