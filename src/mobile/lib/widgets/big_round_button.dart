import 'package:flutter/material.dart';
import 'package:mobile/colors.dart';

class BigRoundButton extends StatefulWidget {
  final VoidCallback onPressed;
  final double size;
  final Color color;
  final IconData icon;

  const BigRoundButton({
    super.key,
    required this.onPressed,
    this.size = 200,
    this.color = MyColors.primary,
    this.icon = Icons.nightlight_round,
  });

  @override
  State<BigRoundButton> createState() => _BigRoundButtonState();
}

class _BigRoundButtonState extends State<BigRoundButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 150),
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.92,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    setState(() => _isPressed = true);
    _controller.forward();
  }

  void _onTapUp(TapUpDetails details) {
    setState(() => _isPressed = false);
    _controller.reverse();
    widget.onPressed();
  }

  void _onTapCancel() {
    setState(() => _isPressed = false);
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final darker = HSLColor.fromColor(widget.color)
        .withLightness(
          (HSLColor.fromColor(widget.color).lightness - 0.15).clamp(0.0, 1.0),
        )
        .toColor();
    final lighter = HSLColor.fromColor(widget.color)
        .withLightness(
          (HSLColor.fromColor(widget.color).lightness + 0.15).clamp(0.0, 1.0),
        )
        .toColor();

    return AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(scale: _scaleAnimation.value, child: child);
      },
      child: GestureDetector(
        onTapDown: _onTapDown,
        onTapUp: _onTapUp,
        onTapCancel: _onTapCancel,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [lighter, widget.color, darker],
            ),
            boxShadow: [
              BoxShadow(
                color: widget.color.withValues(alpha: _isPressed ? 0.3 : 0.5),
                blurRadius: _isPressed ? 15 : 30,
                spreadRadius: _isPressed ? 2 : 5,
                offset: Offset(0, _isPressed ? 5 : 12),
              ),
              BoxShadow(
                color: lighter.withValues(alpha: _isPressed ? 0.0 : 0.3),
                blurRadius: 20,
                spreadRadius: -5,
                offset: const Offset(0, -5),
              ),
            ],
          ),
          child: Center(
            child: Icon(
              widget.icon,
              size: widget.size * 0.4,
              color: Colors.white.withValues(alpha: 0.95),
            ),
          ),
        ),
      ),
    );
  }
}
