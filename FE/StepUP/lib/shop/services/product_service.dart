import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_app/shop/models/product_model.dart';

class ProductService {
  // Trả về danh sách sản phẩm (featured) từ GraphQL endpoint
  static const String _graphqlUrl = 'http://10.0.2.2:8000/graphql/';

  static Future<List<ProductModel>> getFeaturedProducts({int first = 8}) async {
    final query = '''
    query GetFeatured {
      featuredProducts(first: $first) {
        edges {
          node {
            id
            name
            description
            basePrice
            galleryImages {
              imageUrl
            }
          }
        }
      }
    }
    ''';

    try {
      final resp = await http.post(
        Uri.parse(_graphqlUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'query': query}),
      );

      if (resp.statusCode != 200) {
        return [];
      }

      final Map<String, dynamic> data = jsonDecode(resp.body);
      final edges = data['data']?['featuredProducts']?['edges'] as List<dynamic>?;
      if (edges == null) return [];

      final List<ProductModel> products = [];
      for (final e in edges) {
        final node = e['node'] as Map<String, dynamic>?;
        if (node == null) continue;
        final String? img = (node['galleryImages'] is List && (node['galleryImages'] as List).isNotEmpty)
            ? node['galleryImages'][0]['imageUrl']
            : null;
        // Map GraphQL fields to ProductModel
        products.add(ProductModel(
          id: int.tryParse(node['id'].toString()) ?? 0,
          name: node['name'] ?? '',
          price: double.tryParse(node['basePrice']?.toString() ?? '0') ?? 0.0,
          image: img,
          description: node['description'] ?? '',
        ));
      }

      return products;
    } catch (e) {
      return [];
    }
  }
}
