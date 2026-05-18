import 'dart:async';

import 'package:flutter_bluetooth_serial/flutter_bluetooth_serial.dart';

class BluetoothService {
  BluetoothService._();
  static final BluetoothService instance = BluetoothService._();

  final List<BluetoothDiscoveryResult> _devices = [];
  List<BluetoothDiscoveryResult> get devices => List.unmodifiable(_devices);

  bool _isScanning = false;
  bool get isScanning => _isScanning;

  StreamSubscription<BluetoothDiscoveryResult>? _scanSubscription;

  final _devicesController = StreamController<List<BluetoothDiscoveryResult>>.broadcast();
  Stream<List<BluetoothDiscoveryResult>> get devicesStream => _devicesController.stream;

  final _scanningController = StreamController<bool>.broadcast();
  Stream<bool> get scanningStream => _scanningController.stream;

  void startScan() {
    _devices.clear();
    _isScanning = true;
    _devicesController.add(List.unmodifiable(_devices));
    _scanningController.add(true);

    _scanSubscription?.cancel();
    _scanSubscription = FlutterBluetoothSerial.instance.startDiscovery().listen(
      (result) {
        final idx = _devices.indexWhere(
          (d) => d.device.address == result.device.address,
        );
        if (idx >= 0) {
          _devices[idx] = result;
        } else {
          _devices.add(result);
        }
        _devicesController.add(List.unmodifiable(_devices));
      },
      onDone: () {
        _isScanning = false;
        _scanningController.add(false);
      },
    );
  }

  void stopScan() {
    _scanSubscription?.cancel();
    _isScanning = false;
    _scanningController.add(false);
  }

  void dispose() {
    stopScan();
    _devicesController.close();
    _scanningController.close();
  }
}
