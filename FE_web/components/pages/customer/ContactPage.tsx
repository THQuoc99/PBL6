import React, { useState } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { Phone, Mail, MapPin, Clock, Send, MessageCircle, Facebook, Instagram, Youtube } from 'lucide-react';

interface ContactPageProps {
  onNavigate?: (page: string) => void;
}

export default function ContactPage({ onNavigate }: ContactPageProps) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Cảm ơn bạn đã liên hệ! Chúng tôi sẽ phản hồi trong vòng 24h.');
    setFormData({ name: '', email: '', phone: '', subject: '', message: '' });
  };

  const contactInfo = [
    {
      icon: Phone,
      title: 'Điện thoại',
      info: '+84 123 456 789',
      subInfo: 'Hotline: +84 987 654 321'
    },
    {
      icon: Mail,
      title: 'Email',
      info: 'info@shoex.com',
      subInfo: 'support@shoex.com'
    },
    {
      icon: MapPin,
      title: 'Địa chỉ',
      info: '123 Đường Nguyễn Văn Linh',
      subInfo: 'Quận 7, TP.HCM'
    },
    {
      icon: Clock,
      title: 'Giờ làm việc',
      info: 'T2 - T7: 8:00 - 22:00',
      subInfo: 'CN: 9:00 - 21:00'
    }
  ];

  const faqItems = [
    {
      question: 'Làm thế nào để đổi trả sản phẩm?',
      answer: 'Bạn có thể đổi trả trong vòng 7 ngày kể từ ngày mua. Sản phẩm cần còn nguyên vẹn, chưa qua sử dụng và có hóa đơn mua hàng.'
    },
    {
      question: 'Phí vận chuyển là bao nhiêu?',
      answer: 'Miễn phí vận chuyển cho đơn hàng từ 299k. Dưới 299k: phí ship 30k nội thành, 50k ngoại thành.'
    },
    {
      question: 'Thời gian giao hàng?',
      answer: 'Nội thành: 1-2 ngày. Ngoại thành: 2-5 ngày. Các tỉnh xa: 3-7 ngày làm việc.'
    },
    {
      question: 'Có hỗ trợ tư vấn size giày không?',
      answer: 'Có! Liên hệ hotline hoặc chat với chúng tôi. Chúng tôi sẽ tư vấn size phù hợp dựa trên số đo chân của bạn.'
    }
  ];

  return (
    <CustomerLayout currentPage="contact" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">📞 Liên Hệ Với Chúng Tôi</h1>
          <p className="text-xl text-gray-600">Chúng tôi luôn sẵn sàng hỗ trợ bạn!</p>
        </div>

        {/* Contact Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {contactInfo.map((item, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <item.icon className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">{item.title}</h3>
              <p className="text-gray-700 font-medium">{item.info}</p>
              <p className="text-gray-500 text-sm">{item.subInfo}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Contact Form */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <MessageCircle className="h-6 w-6 mr-3 text-blue-600" />
              Gửi Tin Nhắn
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Họ tên *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Nhập họ tên"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Nhập email"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Số điện thoại
                  </label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Nhập số điện thoại"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chủ đề *
                  </label>
                  <select
                    required
                    value={formData.subject}
                    onChange={(e) => handleInputChange('subject', e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Chọn chủ đề</option>
                    <option value="product">Tư vấn sản phẩm</option>
                    <option value="order">Đơn hàng</option>
                    <option value="return">Đổi trả</option>
                    <option value="complaint">Khiếu nại</option>
                    <option value="other">Khác</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tin nhắn *
                </label>
                <textarea
                  required
                  rows={6}
                  value={formData.message}
                  onChange={(e) => handleInputChange('message', e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Nhập tin nhắn của bạn..."
                ></textarea>
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
              >
                <Send className="h-5 w-5 mr-2" />
                Gửi Tin Nhắn
              </button>
            </form>
          </div>

          {/* Map & Social */}
          <div className="space-y-8">
            {/* Map Placeholder */}
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="h-64 bg-gray-200 flex items-center justify-center">
                <div className="text-center">
                  <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Bản đồ cửa hàng</p>
                  <p className="text-sm text-gray-400">123 Đường Nguyễn Văn Linh, Q.7, TP.HCM</p>
                </div>
              </div>
            </div>

            {/* Social Media */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Theo Dõi Chúng Tôi</h3>
              <div className="flex space-x-4">
                <a href="#" className="flex items-center justify-center w-12 h-12 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <Facebook className="h-6 w-6" />
                </a>
                <a href="#" className="flex items-center justify-center w-12 h-12 bg-pink-600 text-white rounded-lg hover:bg-pink-700 transition-colors">
                  <Instagram className="h-6 w-6" />
                </a>
                <a href="#" className="flex items-center justify-center w-12 h-12 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                  <Youtube className="h-6 w-6" />
                </a>
              </div>
              <p className="text-gray-600 mt-4 text-sm">
                Cập nhật những xu hướng giày dép mới nhất và các chương trình khuyến mãi đặc biệt.
              </p>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-12 bg-gray-50 rounded-2xl p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">❓ Câu Hỏi Thường Gặp</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {faqItems.map((item, index) => (
              <div key={index} className="bg-white rounded-lg p-6">
                <h4 className="font-bold text-lg mb-3 text-gray-900">{item.question}</h4>
                <p className="text-gray-600">{item.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}