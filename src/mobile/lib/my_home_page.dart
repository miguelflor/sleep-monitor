import 'package:flutter/material.dart';
import 'package:mobile/colors.dart';
import 'package:mobile/list_scan.dart';
import 'package:mobile/widgets/big_round_button.dart';

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: MyColors.bg,
      body: Center(
        child: BigRoundButton(
          onPressed: () {
            Navigator.of(context).push(_toListRoute());
          },
        ),
      ),
    );
  }
}

Route<void> _toListRoute() {
  return PageRouteBuilder(
    pageBuilder: (context, animation, secondaryAnimation) =>
        const DeviceListPage(),
    transitionsBuilder: (context, animation, secondaryAnimation, child) {
      final slideIn = Tween<Offset>(
        begin: const Offset(1.0, 0.0),
        end: Offset.zero,
      ).animate(CurvedAnimation(parent: animation, curve: Curves.easeInOut));

      final slideOut = Tween<Offset>(
        begin: Offset.zero,
        end: const Offset(-1.0, 0.0),
      ).animate(CurvedAnimation(parent: animation, curve: Curves.easeInOut));

      return Stack(
        children: [
          SlideTransition(position: slideOut, child: const MyHomePage()),
          SlideTransition(position: slideIn, child: child),
        ],
      );
    },
  );
}
