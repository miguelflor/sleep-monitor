import 'package:flutter/material.dart';
import 'package:mobile/colors.dart';

class EmptyScanState extends StatelessWidget {
  final bool isScanning;

  const EmptyScanState({super.key, required this.isScanning});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.bluetooth_searching,
            size: 64,
            color: MyColors.primary.withValues(alpha: 0.3),
          ),
          const SizedBox(height: 16),
          Text(
            isScanning ? 'Looking for devices...' : 'No devices found',
            style: const TextStyle(color: Colors.white38, fontSize: 15),
          ),
        ],
      ),
    );
  }
}
