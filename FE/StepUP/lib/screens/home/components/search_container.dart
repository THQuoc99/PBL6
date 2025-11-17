import 'package:flutter/material.dart';

class SearchContainer extends StatelessWidget {
  final IconData icon;
  final String hintText;
  final bool showBG, showBorder;
  final VoidCallback? ontap;

  const SearchContainer({
    super.key,
    this.icon = Icons.search,
    this.hintText = "Search",
    this.showBG = true,
    this.showBorder = true,
    this.ontap
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: ontap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20),
        child: Container(
          width: double.infinity,
          padding: EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: showBG ? Colors.white : Colors.transparent,//.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(30),
            border: showBorder ? Border.all(color: Colors.white, width: 2) : null,
          ),
          child: Row(
            children: [
              Icon(icon, color: Colors.grey), 
              SizedBox(width: 10),
              Text(
                hintText,
                style: TextStyle(color: Colors.grey, fontSize: 18),
                
              ),
            ],
          ),
        ),
      ),
    );
  }
}