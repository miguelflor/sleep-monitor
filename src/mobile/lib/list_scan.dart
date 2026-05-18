import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:mobile/colors.dart';

class DeviceListPage extends StatefulWidget {
  const DeviceListPage({super.key});

  @override
  State<StatefulWidget> createState() => _DeviceListPage();
}

class _DeviceListPage extends State<DeviceListPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MyColors.bg,
      // body: Center(),
    );
  }
}
