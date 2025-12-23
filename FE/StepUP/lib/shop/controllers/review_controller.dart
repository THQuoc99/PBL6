import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/review_model.dart';

class ReviewController {
  final String baseUrl;
  ReviewController({this.baseUrl = 'http://10.0.2.2:8000/api/reviews/'});

  Future<List<ReviewModel>> fetchReviews(int productId) async {
    final uri = Uri.parse('$baseUrl?product_id=$productId');
    final resp = await http.get(uri);
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      if (data is List) {
        return data.map<ReviewModel>((e) => ReviewModel.fromJson(e)).toList();
      }
      return [];
    } else {
      throw Exception('Failed to load reviews (${resp.statusCode})');
    }
  }
}