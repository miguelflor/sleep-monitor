import 'package:flutter/material.dart';
import 'package:mobile/colors.dart';

class ScanStatusBar extends StatelessWidget {
  final bool isScanning;
  final int deviceCount;

  const ScanStatusBar({
    super.key,
    required this.isScanning,
    required this.deviceCount,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      color: MyColors.primary.withValues(alpha: 0.08),
      child: Row(
        children: [
          if (isScanning)
            const SizedBox(
              width: 14,
              height: 14,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: MyColors.primary,
              ),
            )
          else
            const Icon(
              Icons.check_circle_outline,
              size: 14,
              color: Colors.white38,
            ),
          const SizedBox(width: 10),
          Text(
            isScanning
                ? 'Scanning for devices...'
                : 'Found $deviceCount device${deviceCount == 1 ? '' : 's'}',
            style: TextStyle(
              color: isScanning ? MyColors.primary : Colors.white54,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
