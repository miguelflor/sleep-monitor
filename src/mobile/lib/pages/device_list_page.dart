import 'package:flutter/material.dart';
import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';
import 'package:mobile/colors.dart';
import 'package:mobile/services/bluetooth_service.dart';
import 'package:mobile/widgets/device_tile.dart';
import 'package:mobile/widgets/empty_scan_state.dart';
import 'package:mobile/widgets/scan_status_bar.dart';
import 'package:permission_handler/permission_handler.dart';

class DeviceListPage extends StatefulWidget {
  const DeviceListPage({super.key});

  @override
  State<DeviceListPage> createState() => _DeviceListPageState();
}

class _DeviceListPageState extends State<DeviceListPage>
    with SingleTickerProviderStateMixin {
  final _bt = BluetoothService.instance;

  late AnimationController _radarController;

  List<BluetoothDiscoveryResult> _devices = [];
  bool _isScanning = false;
  final Set<String> _seenAddresses = {};

  @override
  void initState() {
    super.initState();
    _radarController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    );

    _bt.devicesStream.listen((devices) {
      if (mounted) setState(() => _devices = devices);
    });

    _bt.scanningStream.listen((scanning) {
      if (!mounted) return;
      setState(() {
        _isScanning = scanning;
        if (scanning) _seenAddresses.clear();
      });
      if (scanning) {
        _radarController.repeat();
      } else {
        _radarController.stop();
        _radarController.reset();
      }
    });

    _requestPermissionsAndScan();
  }

  Future<void> _requestPermissionsAndScan() async {
    final statuses = await [
      Permission.bluetoothScan,
      Permission.bluetoothConnect,
      Permission.location,
    ].request();

    final denied = statuses.values.any(
      (s) => s.isDenied || s.isPermanentlyDenied,
    );

    if (!mounted) return;

    if (denied) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Bluetooth and location permissions are required to scan for devices.'),
          action: SnackBarAction(
            label: 'Settings',
            onPressed: openAppSettings,
          ),
        ),
      );
      return;
    }

    _bt.startScan();
  }

  @override
  void dispose() {
    _radarController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MyColors.bg,
      appBar: AppBar(
        backgroundColor: MyColors.bg,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white70),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text(
          'Devices',
          style: TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
            fontSize: 20,
          ),
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16),
            child: RotationTransition(
              turns: _radarController,
              child: IconButton(
                icon: Icon(
                  Icons.radar,
                  color: _isScanning ? MyColors.primary : Colors.white38,
                ),
                onPressed: _isScanning ? null : _requestPermissionsAndScan,
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          ScanStatusBar(isScanning: _isScanning, deviceCount: _devices.length),
          Expanded(
            child: _devices.isEmpty
                ? EmptyScanState(isScanning: _isScanning)
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    itemCount: _devices.length,
                    itemBuilder: (context, index) {
                      final address = _devices[index].device.address;
                      final isNew = _seenAddresses.add(address); // add() returns true if it was not already present
                      return DeviceTile(
                        key: ValueKey(address),
                        result: _devices[index],
                        index: index,
                        animate: isNew,
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
