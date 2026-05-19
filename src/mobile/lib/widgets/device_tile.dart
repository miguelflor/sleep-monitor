import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:mobile/colors.dart';
import 'package:mobile/widgets/rssi_indicator.dart';

class DeviceTile extends StatefulWidget {
  final BluetoothDiscoveryResult result;
  final int index;
  final bool animate;

  const DeviceTile({super.key, required this.result, required this.index, this.animate = true});

  @override
  State<DeviceTile> createState() => _DeviceTileState();
}

class _DeviceTileState extends State<DeviceTile>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _fadeAnim = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
      begin: const Offset(0.18, 0),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));

    if (widget.animate) {
      Future.delayed(Duration(milliseconds: widget.index * 40), () {
        if (mounted) _controller.forward();
      });
    } else {
      _controller.value = 1.0;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final device = widget.result.device;
    final rssi = widget.result.rssi;
    final isNamed = device.name != null && device.name!.isNotEmpty;

    return FadeTransition(
      opacity: _fadeAnim,
      child: SlideTransition(
        position: _slideAnim,
        child: Container(
          margin: const EdgeInsets.only(bottom: 10),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.04),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: MyColors.primary.withValues(alpha: 0.15),
              width: 1,
            ),
          ),
          child: ListTile(
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 6,
            ),
            leading: Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: MyColors.primary.withValues(alpha: isNamed ? 0.2 : 0.08),
              ),
              child: Icon(
                isNamed ? Icons.bluetooth : Icons.bluetooth_disabled,
                color: isNamed ? MyColors.primary : Colors.white24,
                size: 22,
              ),
            ),
            title: Text(
              isNamed ? device.name! : 'Unknown Device',
              style: TextStyle(
                color: isNamed ? Colors.white : Colors.white38,
                fontWeight: isNamed ? FontWeight.w600 : FontWeight.w400,
                fontSize: 15,
              ),
            ),
            subtitle: Text(
              device.address,
              style: const TextStyle(color: Colors.white38, fontSize: 12),
            ),
            trailing: rssi != null ? RssiIndicator(rssi: rssi) : null,
          ),
        ),
      ),
    );
  }
}
