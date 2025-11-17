import 'package:flutter/material.dart';

class VirticalImageText extends StatelessWidget {
  final String image, title;
  final Color textcolor;
  final Color? bgcolor;
  final VoidCallback? ontap;
  const VirticalImageText({
    super.key,
    this.bgcolor,
    this.image = "assets/images/category/boots.png",
    this.textcolor = Colors.black,
    this.title = "boots",
    this.ontap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: ontap,
      child: Padding(
        padding: const EdgeInsets.only(right: 16),
        child: Column(
          children: [
            //Circular icon
            Container(
              width: 56,
              height: 56,
              padding: EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: bgcolor,
                borderRadius: BorderRadius.circular(100)
              ),
              child: Image(image: AssetImage(image), fit: BoxFit.cover,),
            ),
            //Name Tag
            SizedBox(height: 8),
            SizedBox(
              width: 55,
              child: Text(
                title,
                style: Theme.of(context).textTheme.labelMedium!.apply(color: textcolor),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                
                ),
                
              )
          ],
        ),
      ),
    );
  }
}


