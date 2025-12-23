import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ReviewFormScreen extends StatefulWidget {
  final int productId;
  const ReviewFormScreen({super.key, required this.productId});

  @override
  State<ReviewFormScreen> createState() => _ReviewFormScreenState();
}

class _ReviewFormScreenState extends State<ReviewFormScreen> {
  double _rating = 5.0;
  final TextEditingController _commentCtrl = TextEditingController();
  final List<XFile> _images = [];
  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;

  List<Map<String, dynamic>> _variants = [];
  int? _selectedVariantId;
  bool _loadingVariants = true;

  @override
  void initState() {
    super.initState();
    _fetchVariants();
  }

  Future<void> _fetchVariants() async {
    try {
      final uri = Uri.parse('http://10.0.2.2:8000/api/products/${widget.productId}/');
      final resp = await http.get(uri);
      if (resp.statusCode == 200) {
        final Map<String, dynamic> data = json.decode(resp.body);
        final v = data['variants'] as List<dynamic>? ?? [];
        setState(() {
          _variants = v.map((e) => {
            'variant_id': e['variant_id'],
            'sku': e['sku'] ?? '',
            'option_combinations': e['option_combinations'] ?? {}
          }).toList();
          _loadingVariants = false;
        });
      } else {
        setState(() => _loadingVariants = false);
      }
    } catch (_) {
      setState(() => _loadingVariants = false);
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      if (source == ImageSource.gallery) {
        final List<XFile>? picked = await _picker.pickMultiImage(imageQuality: 80);
        if (picked != null && picked.isNotEmpty) {
          setState(() => _images.addAll(picked));
        }
      } else {
        final XFile? img = await _picker.pickImage(source: ImageSource.camera, imageQuality: 80);
        if (img != null) setState(() => _images.add(img));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Lỗi chọn ảnh: $e')));
    }
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (ctx) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Chọn từ Thư viện'),
              onTap: () {
                Navigator.of(ctx).pop();
                _pickImage(ImageSource.gallery);
              },
            ),
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Chụp ảnh'),
              onTap: () {
                Navigator.of(ctx).pop();
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.close),
              title: const Text('Hủy'),
              onTap: () => Navigator.of(ctx).pop(),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _submit() async {
    setState(() => _isLoading = true);
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('token');

    if (token == null) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Vui lòng đăng nhập để gửi đánh giá.')));
      return;
    }

    final uri = Uri.parse('http://10.0.2.2:8000/api/reviews/');
    final request = http.MultipartRequest('POST', uri);
    request.headers['Authorization'] = 'Bearer $token';

    request.fields['product_id'] = widget.productId.toString();
    if (_selectedVariantId != null) {
      request.fields['variant_id'] = _selectedVariantId.toString();
    }
    request.fields['rating'] = _rating.toInt().toString();
    request.fields['comment'] = _commentCtrl.text;

    try {
      for (var i = 0; i < _images.length; i++) {
        final file = File(_images[i].path);
        request.files.add(await http.MultipartFile.fromPath('uploaded_images', file.path));
      }

      final resp = await request.send();
      final body = await http.Response.fromStream(resp);

      if (resp.statusCode == 201 || resp.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Gửi đánh giá thành công')));
        Navigator.of(context).pop(true);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Lỗi: ${body.body}')));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Lỗi: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _removeImageAt(int index) {
    setState(() => _images.removeAt(index));
  }

  @override
  void dispose() {
    _commentCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Viết đánh giá')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text('Đánh giá của bạn', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            RatingBar.builder(
              initialRating: _rating,
              minRating: 1,
              direction: Axis.horizontal,
              itemCount: 5,
              itemBuilder: (context, _) => const Icon(Icons.star, color: Colors.amber),
              onRatingUpdate: (r) => setState(() => _rating = r),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _commentCtrl,
              maxLines: 5,
              decoration: const InputDecoration(
                labelText: 'Nội dung đánh giá',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _showImageSourceDialog,
                  icon: const Icon(Icons.photo),
                  label: const Text('Thêm ảnh'),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: List.generate(_images.length, (index) {
                        final i = _images[index];
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Stack(
                            children: [
                              ClipRRect(
                                borderRadius: BorderRadius.circular(6),
                                child: Image.file(File(i.path), width: 60, height: 60, fit: BoxFit.cover),
                              ),
                              Positioned(
                                right: -8,
                                top: -8,
                                child: IconButton(
                                  icon: Container(
                                    decoration: BoxDecoration(
                                      color: Colors.black54,
                                      shape: BoxShape.circle,
                                    ),
                                    child: const Icon(Icons.close, size: 16, color: Colors.white),
                                  ),
                                  onPressed: () => _removeImageAt(index),
                                ),
                              ),
                            ],
                          ),
                        );
                      }),
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: 12),
            if (_loadingVariants)
              const SizedBox.shrink()
            else if (_variants.isNotEmpty)
              DropdownButtonFormField<int>(
                value: _selectedVariantId,
                items: _variants.map((v) {
                  final display = (v['option_combinations'] is Map && (v['option_combinations'] as Map).isNotEmpty)
                    ? (v['option_combinations'] as Map).entries.map((e) => '${e.key}:${e.value}').join(', ')
                    : v['sku'].toString();
                  return DropdownMenuItem<int>(
                    value: v['variant_id'] as int?,
                    child: Text(display),
                  );
                }).toList(),
                onChanged: (val) => setState(() => _selectedVariantId = val),
                decoration: const InputDecoration(labelText: 'Biến thể (Color/Size)'),
              ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _submit,
              child: _isLoading ? const SizedBox(width:18,height:18,child:CircularProgressIndicator(color: Colors.white, strokeWidth:2)) : const Text('Gửi đánh giá'),
            ),
          ],
        ),
      ),
    );
  }
}