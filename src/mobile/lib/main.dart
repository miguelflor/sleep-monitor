import 'package:flutter/material.dart';
import 'package:mobile/colors.dart';
import 'package:mobile/my_home_page.dart';
import 'package:mobile/widgets/big_round_button.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sleep Monitor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: MyColors.bg),
      ),
      home: const MyHomePage(),
    );
  }
}
