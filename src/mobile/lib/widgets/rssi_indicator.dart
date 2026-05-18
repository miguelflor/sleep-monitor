import 'package:flutter/material.dart';

class RssiIndicator extends StatelessWidget {
  final int rssi;

  const RssiIndicator({super.key, required this.rssi});

  Color get _color {
    if (rssi >= -60) return const Color(0xFF63FFAA);
    if (rssi >= -80) return const Color(0xFFFFD663);
    return const Color(0xFFFF6363);
  }

  int get _bars {
    if (rssi >= -60) return 3;
    if (rssi >= -80) return 2;
    return 1;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: List.generate(3, (i) {
            return Container(
              width: 4,
              height: 6.0 + i * 4,
              margin: const EdgeInsets.only(left: 2),
              decoration: BoxDecoration(
                color: i < _bars ? _color : Colors.white12,
                borderRadius: BorderRadius.circular(2),
              ),
            );
          }),
        ),
        const SizedBox(height: 4),
        Text('$rssi dBm', style: TextStyle(color: _color, fontSize: 10)),
      ],
    );
  }
}
