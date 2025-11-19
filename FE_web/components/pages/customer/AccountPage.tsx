import React, { useState, useEffect } from 'react';
import CustomerLayout from '../../layout/CustomerLayout';
import { authService } from '../../../services/auth';
import { 
  User, ShoppingBag, Heart, Settings, LogOut, Edit, Camera, MapPin, 
  Phone, Mail, Gift, Calendar, Plus, Trash2, Check, Star, Upload, Store,
  Truck, Clock, MapPinIcon, X, Package, CheckCircle, Ticket, Tag
} from 'lucide-react';

interface AccountPageProps {
  onNavigate?: (page: string, data?: any) => void;
}

interface Address {
  id: string;
  name: string;
  phone: string;
  province: string;
  ward: string;
  street: string;
  specificAddress: string;
  address: string;
  isDefault: boolean;
}

interface Voucher {
  voucher_id: number;
  code: string;
  type: 'platform' | 'seller';
  seller?: {
    id: number;
    name: string;
    logo?: string;
  };
  discount_type: 'percent' | 'fixed';
  discount_value: number;
  min_order_amount: number;
  max_discount?: number;
  start_date: string;
  end_date: string;
  usage_limit?: number;
  per_user_limit: number;
  is_active: boolean;
  is_auto: boolean;
  description?: string;
  // User voucher specific fields
  saved_at: string;
  used_count: number;
  can_use: boolean;
}

export default function AccountPage({ onNavigate }: AccountPageProps) {
  const [activeTab, setActiveTab] = useState('profile');
  const [userInfo, setUserInfo] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    birthday: '',
    gender: 'male',
    memberSince: '',
    avatar: ''
  });

  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);

  // Load user profile on component mount
  useEffect(() => {
    if (authService.isAuthenticated()) {
      loadUserProfile();
    } else {
      // Thử lấy thông tin từ localStorage
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        setUserInfo({
          name: currentUser.fullName || currentUser.username || 'Người dùng',
          email: currentUser.email || '',
          phone: currentUser.phone || '',
          address: '',
          birthday: '',
          gender: 'male',
          memberSince: currentUser.dateJoined || '',
          avatar: currentUser.avatarUrl || ''
        });
      }
      setLoading(false);
    }
  }, []);

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      const response = await authService.getUserProfile();
      
      if (response.success && response.user) {
        const user = response.user;
        setUserInfo({
          name: user.fullName || `${user.firstName || ''} ${user.lastName || ''}`.trim() || user.username || 'Người dùng',
          email: user.email || '',
          phone: user.phone || '',
          address: '', // Có thể lấy từ address API riêng
          birthday: user.birthDate || '', // ✅ Load birthDate từ backend
          gender: 'male', // Có thể thêm field này vào backend
          memberSince: user.dateJoined || '',
          avatar: user.avatarUrl || ''
        });
      } else {
        // Fallback: Lấy thông tin từ localStorage
        const currentUser = authService.getCurrentUser();
        if (currentUser) {
          setUserInfo({
            name: currentUser.fullName || currentUser.username || 'Người dùng',
            email: currentUser.email || '',
            phone: currentUser.phone || '',
            address: '',
            birthday: '',
            gender: 'male',
            memberSince: currentUser.dateJoined || '',
            avatar: currentUser.avatarUrl || ''
          });
        }
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
      // Fallback: Lấy thông tin từ localStorage
      const currentUser = authService.getCurrentUser();
      if (currentUser) {
        setUserInfo({
          name: currentUser.fullName || currentUser.username || 'Người dùng',
          email: currentUser.email || '',
          phone: currentUser.phone || '',
          address: '',
          birthday: '',
          gender: 'male',
          memberSince: currentUser.dateJoined || '',
          avatar: currentUser.avatarUrl || ''
        });
      }
    } finally {
      setLoading(false);
    }
  };
  const [editingAddress, setEditingAddress] = useState<Address | null>(null);
  const [orderTab, setOrderTab] = useState('all'); // Tab đơn hàng hiện tại
  const [formPosition, setFormPosition] = useState<'top' | 'bottom' | null>(null); // Vị trí hiển thị form
  const [showTrackingModal, setShowTrackingModal] = useState(false);
  const [selectedOrderTracking, setSelectedOrderTracking] = useState<string | null>(null);
  const [voucherTab, setVoucherTab] = useState('available'); // available, used, expired
  
  // Address management state
  const [addresses, setAddresses] = useState<Address[]>([
    {
      id: '1',
      name: 'Nguyễn Văn A',
      phone: '0901234567',
      province: 'TP.Hồ Chí Minh',
      ward: 'Phường Bến Nghé',
      street: 'Đường Lê Lợi',
      specificAddress: 'Số 123, Tầng 2',
      address: 'TP.Hồ Chí Minh, Phường Bến Nghé, Đường Lê Lợi, Số 123, Tầng 2',
      isDefault: true
    },
    {
      id: '2',
      name: 'Nguyễn Văn A',
      phone: '0901234567',
      province: 'TP.Hồ Chí Minh',
      ward: 'Phường Bến Thành',
      street: 'Đường Nguyễn Huệ',
      specificAddress: 'Số 456, Chung cư ABC',
      address: 'TP.Hồ Chí Minh, Phường Bến Thành, Đường Nguyễn Huệ, Số 456, Chung cư ABC',
      isDefault: false
    }
  ]);

  const [newAddress, setNewAddress] = useState({
    name: '',
    phone: '',
    province: '',
    ward: '',
    street: '',
    specificAddress: ''
  });

  const recentOrders = [
    {
      id: 'ORD001',
      date: '2024-11-10',
      status: 'completed',
      statusText: 'Hoàn thành',
      total: 2490000,
      shop: {
        name: 'SHOEX Official Store',
        logo: '/api/placeholder/32/32'
      },
      items: [
        {
          id: 1,
          name: 'Nike Air Max 270 Premium',
          image: '/api/placeholder/80/80',
          price: 2490000,
          quantity: 1,
          variant: 'Đen - Size 42'
        }
      ]
    },
    {
      id: 'ORD002',
      date: '2024-11-12',
      status: 'shipping',
      statusText: 'Vận chuyển',
      total: 1200000,
      shop: {
        name: 'Sneaker Hub Vietnam',
        logo: '/api/placeholder/32/32'
      },
      items: [
        {
          id: 2,
          name: 'Converse Chuck Taylor All Star',
          image: '/api/placeholder/80/80',
          price: 1200000,
          quantity: 1,
          variant: 'Trắng - Size 40'
        }
      ]
    },
    {
      id: 'ORD003',
      date: '2024-11-14',
      status: 'pending',
      statusText: 'Chờ xác nhận',
      total: 3200000,
      shop: {
        name: 'Sport Fashion Store',
        logo: '/api/placeholder/32/32'
      },
      items: [
        {
          id: 3,
          name: 'Adidas Ultraboost 22',
          image: '/api/placeholder/80/80',
          price: 2800000,
          quantity: 1,
          variant: 'Trắng/Xám - Size 43'
        },
        {
          id: 4,
          name: 'Vớt thể thao Adidas',
          image: '/api/placeholder/80/80',
          price: 400000,
          quantity: 1,
          variant: 'Trắng - Size M'
        }
      ]
    },
    {
      id: 'ORD004',
      date: '2024-11-08',
      status: 'cancelled',
      statusText: 'Đã hủy',
      total: 800000,
      shop: {
        name: 'Fashion Accessories',
        logo: '/api/placeholder/32/32'
      },
      items: [
        {
          id: 5,
          name: 'Giày thể thao Vans Old Skool',
          image: '/api/placeholder/80/80',
          price: 800000,
          quantity: 1,
          variant: 'Đen/Trắng - Size 41'
        }
      ]
    },
    {
      id: 'ORD005',
      date: '2024-11-13',
      status: 'delivering',
      statusText: 'Chờ giao hàng',
      total: 1500000,
      shop: {
        name: 'SHOEX Official Store',
        logo: '/api/placeholder/32/32'
      },
      items: [
        {
          id: 6,
          name: 'Puma RS-X Sneakers',
          image: '/api/placeholder/80/80',
          price: 1500000,
          quantity: 1,
          variant: 'Xanh/Trắng - Size 42'
        }
      ]
    },
    {
      id: 'ORD006',
      date: '2024-11-05',
      status: 'refund',
      statusText: 'Trả hàng/Hoàn tiền',
      total: 2100000,
      shop: {
        name: 'Premium Shoes',
        logo: '/api/placeholder/32/32'
      },
      items: [
        {
          id: 7,
          name: 'New Balance 574 Classic',
          image: '/api/placeholder/80/80',
          price: 2100000,
          quantity: 1,
          variant: 'Xám - Size 44'
        }
      ]
    }
  ];

  // Mock voucher data mapping với backend
  const userVouchers: Voucher[] = [
    {
      voucher_id: 1,
      code: 'WELCOME10',
      type: 'platform',
      discount_type: 'percent',
      discount_value: 10,
      min_order_amount: 500000,
      max_discount: 100000,
      start_date: '2024-11-01',
      end_date: '2024-12-31',
      per_user_limit: 1,
      is_active: true,
      is_auto: false,
      description: 'Voucher chào mừng thành viên mới',
      saved_at: '2024-11-10T09:00:00Z',
      used_count: 0,
      can_use: true
    },
    {
      voucher_id: 2,
      code: 'SHOEX50K',
      type: 'seller',
      seller: {
        id: 1,
        name: 'SHOEX Official Store',
        logo: '/api/placeholder/32/32'
      },
      discount_type: 'fixed',
      discount_value: 50000,
      min_order_amount: 1000000,
      start_date: '2024-11-01',
      end_date: '2024-11-30',
      per_user_limit: 2,
      is_active: true,
      is_auto: false,
      description: 'Giảm 50K cho đơn hàng từ 1 triệu',
      saved_at: '2024-11-12T14:30:00Z',
      used_count: 1,
      can_use: true
    },
    {
      voucher_id: 3,
      code: 'FREESHIP',
      type: 'platform',
      discount_type: 'fixed',
      discount_value: 25000,
      min_order_amount: 300000,
      start_date: '2024-11-15',
      end_date: '2024-11-20',
      per_user_limit: 1,
      is_active: true,
      is_auto: false,
      description: 'Miễn phí vận chuyển cho đơn từ 300K',
      saved_at: '2024-11-15T10:00:00Z',
      used_count: 1,
      can_use: false
    },
    {
      voucher_id: 4,
      code: 'EXPIRED20',
      type: 'platform',
      discount_type: 'percent',
      discount_value: 20,
      min_order_amount: 800000,
      max_discount: 200000,
      start_date: '2024-10-01',
      end_date: '2024-10-31',
      per_user_limit: 1,
      is_active: false,
      is_auto: false,
      description: 'Voucher đã hết hạn',
      saved_at: '2024-10-15T08:00:00Z',
      used_count: 0,
      can_use: false
    }
  ];

  const stats = {
    totalOrders: 15,
    totalSpent: 12500000,
    savedItems: 8,
    loyaltyPoints: 2450
  };

  // Order management functions
  const orderTabs = [
    { id: 'all', label: 'Tất cả', count: recentOrders.length },
    { id: 'pending', label: 'Chờ xác nhận', count: recentOrders.filter(o => o.status === 'pending').length },
    { id: 'shipping', label: 'Vận chuyển', count: recentOrders.filter(o => o.status === 'shipping').length },
    { id: 'delivering', label: 'Chờ giao hàng', count: recentOrders.filter(o => o.status === 'delivering').length },
    { id: 'completed', label: 'Hoàn thành', count: recentOrders.filter(o => o.status === 'completed').length },
    { id: 'cancelled', label: 'Đã hủy', count: recentOrders.filter(o => o.status === 'cancelled').length },
    { id: 'refund', label: 'Trả hàng/Hoàn tiền', count: recentOrders.filter(o => o.status === 'refund').length }
  ];

  const filteredOrders = orderTab === 'all' 
    ? recentOrders 
    : recentOrders.filter(order => order.status === orderTab);

  // Dữ liệu tracking cho đơn hàng
  const trackingData: { [key: string]: any } = {
    'ORD005': {
      currentStatus: 'Chờ giao hàng',
      estimatedDelivery: '2024-11-16 14:00',
      carrier: 'Giao Hàng Nhanh',
      trackingNumber: 'GHN123456789',
      timeline: [
        {
          id: 5,
          status: 'Giao thành công',
          location: 'Địa chỉ nhận hàng',
          time: 'Dự kiến 2024-11-16 14:00',
          description: 'Hàng sẽ được giao đến tay người nhận',
          completed: false,
          needsConfirmation: true,
          deliveryProof: {
            receiverName: 'Nguyễn Văn A',
            receiverPhone: '0901234567',
            deliveryImages: [
              '/api/placeholder/300/200?text=H%C3%ACnh+giao+h%C3%A0ng+1',
              '/api/placeholder/300/200?text=H%C3%ACnh+x%C3%A1c+nh%E1%BA%ADn+2'
            ],
            signature: '/api/placeholder/200/100?text=Ch%E1%BB%AF+k%C3%BD',
            note: 'Hàng đã được giao thành công. Vui lòng xác nhận đã nhận hàng.'
          }
        },
        {
          id: 4,
          status: 'Đang giao hàng',
          location: 'Đang trên đường giao',
          time: 'Dự kiến 2024-11-15 16:00',
          description: 'Shipper đang trên đường giao hàng đến bạn',
          completed: true,
          current: true,
          detailedRoute: [
            {
              location: 'Địa chỉ giao hàng - 123 Lê Lợi, Q.1',
              time: 'Dự kiến 2024-11-16 14:00',
              status: 'Sắp tới',
              description: 'Shipper sẽ giao hàng đến địa chỉ của bạn'
            },
            {
              location: 'Đang di chuyển trên đường Nguyễn Huệ',
              time: '2024-11-15 15:30',
              status: 'Hiện tại',
              description: 'Shipper đang di chuyển và sẽ liên hệ với bạn trước khi đến'
            },
            {
              location: 'Xuất phát từ Hub GHN Quận 7',
              time: '2024-11-15 14:45',
              status: 'Đã qua',
              description: 'Shipper đã nhận hàng và bắt đầu quá trình giao hàng'
            },
            {
              location: 'Chuẩn bị giao hàng tại Hub',
              time: '2024-11-15 14:20',
              status: 'Đã qua',
              description: 'Hàng đã được chuẩn bị và phân công cho shipper'
            }
          ]
        },
        {
          id: 3,
          status: 'Đang vận chuyển',
          location: 'Trung tâm phân loại - TP.HCM',
          time: '2024-11-14 08:20',
          description: 'Hàng đã hoàn thành vận chuyển',
          completed: true
        },
        {
          id: 2,
          status: 'Đã giao cho đơn vị vận chuyển',
          location: 'Kho SHOEX Official Store - Quận 1',
          time: '2024-11-13 15:45',
          description: 'Hàng đã được chuyển đến kho vận chuyển',
          completed: true
        },
        {
          id: 1,
          status: 'Đã xác nhận đơn hàng',
          location: 'SHOEX Official Store - TP.HCM',
          time: '2024-11-13 09:30',
          description: 'Đơn hàng đã được xác nhận và chuẩn bị hàng',
          completed: true
        }
      ]
    },
    'ORD001': {
      currentStatus: 'Hoàn thành',
      estimatedDelivery: '2024-11-10 15:30',
      carrier: 'Giao Hàng Nhanh',
      trackingNumber: 'GHN987654321',
      timeline: [
        {
          id: 5,
          status: 'Giao thành công',
          location: 'Địa chỉ nhận hàng - 123 Lê Lợi, Q.1',
          time: '2024-11-10 15:30',
          description: 'Hàng đã được giao thành công và khách hàng đã xác nhận nhận hàng',
          completed: true,
          current: false
        },
        {
          id: 4,
          status: 'Đang giao hàng',
          location: 'Shipper đang giao hàng',
          time: '2024-11-10 14:45',
          description: 'Shipper đã liên hệ và đang trên đường giao hàng',
          completed: true
        },
        {
          id: 3,
          status: 'Đang vận chuyển',
          location: 'Trung tâm phân loại - TP.HCM',
          time: '2024-11-09 16:20',
          description: 'Hàng đã hoàn thành vận chuyển',
          completed: true
        },
        {
          id: 2,
          status: 'Đã giao cho đơn vị vận chuyển',
          location: 'Kho SHOEX Official Store - Quận 1',
          time: '2024-11-08 10:15',
          description: 'Hàng đã được chuyển đến đơn vị vận chuyển',
          completed: true
        },
        {
          id: 1,
          status: 'Đã xác nhận đơn hàng',
          location: 'SHOEX Official Store - TP.HCM',
          time: '2024-11-08 09:00',
          description: 'Đơn hàng đã được xác nhận và chuẩn bị hàng',
          completed: true
        }
      ]
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  // Avatar upload handler
  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        setLoading(true);
        
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
          alert('Kích thước file không được vượt quá 5MB!');
          return;
        }
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
          alert('Vui lòng chọn file hình ảnh!');
          return;
        }
        
        const response = await authService.uploadAvatar(file);
        
        if (response.success) {
          // Update local state immediately for better UX
          setUserInfo({
            ...userInfo,
            avatar: response.avatarUrl || ''
          });
          alert('Tải lên avatar thành công!');
          // Reload user profile to get updated data
          await loadUserProfile();
        } else {
          alert(`Tải lên thất bại: ${response.message}`);
        }
      } catch (error) {
        console.error('Error uploading avatar:', error);
        alert('Có lỗi xảy ra khi tải lên avatar!');
      } finally {
        setLoading(false);
      }
    }
  };

  // Avatar delete handler
  const handleAvatarDelete = async () => {
    if (!userInfo.avatar) {
      alert('Không có avatar để xóa!');
      return;
    }

    if (confirm('Bạn có chắc chắn muốn xóa avatar?')) {
      try {
        setLoading(true);
        
        const response = await authService.deleteAvatar();
        
        if (response.success) {
          // Update local state immediately for better UX
          setUserInfo({
            ...userInfo,
            avatar: ''
          });
          alert('Xóa avatar thành công!');
          // Reload user profile to get updated data
          await loadUserProfile();
        } else {
          alert(`Xóa avatar thất bại: ${response.message}`);
        }
      } catch (error) {
        console.error('Error deleting avatar:', error);
        alert('Có lỗi xảy ra khi xóa avatar!');
      } finally {
        setLoading(false);
      }
    }
  };

  // Address management functions
  const handleAddAddress = () => {
    if (newAddress.name && newAddress.phone && newAddress.province && newAddress.ward && newAddress.street && newAddress.specificAddress) {
      const fullAddress = `${newAddress.province}, ${newAddress.ward}, ${newAddress.street}, ${newAddress.specificAddress}`;
      const address: Address = {
        id: Date.now().toString(),
        name: newAddress.name,
        phone: newAddress.phone,
        province: newAddress.province,
        ward: newAddress.ward,
        street: newAddress.street,
        specificAddress: newAddress.specificAddress,
        address: fullAddress,
        isDefault: addresses.length === 0
      };
      setAddresses([...addresses, address]);
      setNewAddress({ name: '', phone: '', province: '', ward: '', street: '', specificAddress: '' });
      setShowAddressForm(false);
      setFormPosition(null);
    }
  };

  const handleEditAddress = (address: Address) => {
    setEditingAddress(address);
    setNewAddress({
      name: address.name,
      phone: address.phone,
      province: address.province,
      ward: address.ward,
      street: address.street,
      specificAddress: address.specificAddress
    });
    setShowAddressForm(true);
    setFormPosition('bottom'); // Form chỉnh sửa ở dưới
  };

  const handleUpdateAddress = () => {
    if (editingAddress && newAddress.name && newAddress.phone && newAddress.province && newAddress.ward && newAddress.street && newAddress.specificAddress) {
      const fullAddress = `${newAddress.province}, ${newAddress.ward}, ${newAddress.street}, ${newAddress.specificAddress}`;
      setAddresses(addresses.map(addr => 
        addr.id === editingAddress.id 
          ? { 
              ...addr, 
              name: newAddress.name, 
              phone: newAddress.phone,
              province: newAddress.province,
              ward: newAddress.ward,
              street: newAddress.street,
              specificAddress: newAddress.specificAddress,
              address: fullAddress
            }
          : addr
      ));
      setEditingAddress(null);
      setNewAddress({ name: '', phone: '', province: '', ward: '', street: '', specificAddress: '' });
      setShowAddressForm(false);
      setFormPosition(null);
    }
  };

  const handleCancelForm = () => {
    setShowAddressForm(false);
    setEditingAddress(null);
    setNewAddress({ name: '', phone: '', province: '', ward: '', street: '', specificAddress: '' });
    setFormPosition(null);
  };

  const handleShowTracking = (orderId: string) => {
    setSelectedOrderTracking(orderId);
    setShowTrackingModal(true);
  };

  const handleCloseTracking = () => {
    setShowTrackingModal(false);
    setSelectedOrderTracking(null);
  };

  const handleConfirmDelivery = (orderId: string) => {
    // Cập nhật trạng thái đơn hàng thành completed
    alert('Xác nhận nhận hàng thành công! Đơn hàng đã hoàn thành.');
    setShowTrackingModal(false);
    setSelectedOrderTracking(null);
    // Thực tế sẽ cập nhật database và refresh data
  };

  const handleDeleteAddress = (id: string) => {
    setAddresses(addresses.filter(addr => addr.id !== id));
  };

  const handleSetDefaultAddress = (id: string) => {
    setAddresses(addresses.map(addr => ({
      ...addr,
      isDefault: addr.id === id
    })));
  };

  const tabs = [
    { id: 'profile', label: 'Thông tin cá nhân', icon: User },
    { id: 'orders', label: 'Đơn hàng', icon: ShoppingBag },
    { id: 'addresses', label: 'Địa chỉ', icon: MapPin },
    { id: 'vouchers', label: 'Voucher', icon: Ticket },
    { id: 'settings', label: 'Cài đặt', icon: Settings }
  ];

  const handleSave = async () => {
    try {
      setLoading(true);
      
      // Parse fullName into firstName and lastName
      const nameParts = userInfo.name.trim().split(' ');
      const firstName = nameParts[0] || '';
      const lastName = nameParts.slice(1).join(' ') || '';
      
      // Format birthDate để đảm bảo format YYYY-MM-DD
      const formatBirthDate = (dateValue: string) => {
        if (!dateValue || !dateValue.trim()) return undefined;
        
        // Nếu đã là format YYYY-MM-DD thì giữ nguyên
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
          return dateValue;
        }
        
        // Nếu là format DD/MM/YYYY, convert thành YYYY-MM-DD
        if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateValue)) {
          const [day, month, year] = dateValue.split('/');
          return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
        }
        
        // Nếu là Date object hoặc các format khác
        try {
          const date = new Date(dateValue);
          if (isNaN(date.getTime())) return undefined;
          return date.toISOString().split('T')[0];
        } catch {
          return undefined;
        }
      };
      
      const birthDate = formatBirthDate(userInfo.birthday);
      
      console.log('📝 Preparing update data:', {
        originalBirthday: userInfo.birthday,
        formattedBirthDate: birthDate,
        fullName: userInfo.name,
        phone: userInfo.phone,
        email: userInfo.email
      });
      
      const updateData = {
        fullName: userInfo.name,
        firstName: firstName,
        lastName: lastName,
        phone: userInfo.phone,
        email: userInfo.email,
        ...(birthDate && { birthDate: birthDate }) // Chỉ thêm nếu có giá trị
      };
      
      console.log('📤 Final updateData being sent:', updateData);
      
      const response = await authService.updateUserProfile(updateData);
      
      if (response.success) {
        setIsEditing(false);
        alert('Cập nhật thông tin thành công!');
        // Reload user profile to get updated data
        await loadUserProfile();
      } else {
        alert(`Cập nhật thất bại: ${response.message}`);
      }
    } catch (error) {
      console.error('Error updating user profile:', error);
      alert('Có lỗi xảy ra khi cập nhật thông tin!');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (confirm('Bạn có chắc chắn muốn đăng xuất?')) {
      onNavigate?.('home');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'shipping': return 'text-blue-600 bg-blue-100';
      case 'delivering': return 'text-purple-600 bg-purple-100';
      case 'pending': return 'text-orange-600 bg-orange-100';
      case 'cancelled': return 'text-red-600 bg-red-100';
      case 'refund': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  // TrackingModal component
  const TrackingModal = ({ orderId }: { orderId: string }) => {
    const tracking = trackingData[orderId];
    if (!tracking) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold mb-2">Chi tiết vận chuyển</h3>
                <p className="text-blue-100">Đơn hàng #{orderId}</p>
                <p className="text-sm text-blue-100">Mã vận đơn: {tracking.trackingNumber}</p>
              </div>
              <button
                onClick={handleCloseTracking}
                className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Truck className="h-4 w-4" />
                  <span className="text-sm font-medium">Đơn vị vận chuyển</span>
                </div>
                <p className="text-white font-semibold">{tracking.carrier}</p>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="h-4 w-4" />
                  <span className="text-sm font-medium">Dự kiến giao hàng</span>
                </div>
                <p className="text-white font-semibold">{tracking.estimatedDelivery}</p>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="p-6 overflow-y-auto max-h-96">
            <div className="space-y-4">
              {tracking.timeline.map((step: any, index: number) => (
                <div key={step.id} className="relative">
                  {/* Connector Line */}
                  {index > 0 && (
                    <div className={`absolute left-4 top-0 w-0.5 h-4 ${
                      tracking.timeline[index - 1].completed ? 'bg-green-300' : 'bg-gray-200'
                    }`} />
                  )}
                  
                  <div className="flex items-start gap-4">
                    {/* Status Icon */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      step.current 
                        ? 'bg-blue-500 text-white animate-pulse' 
                        : step.completed 
                        ? 'bg-green-500 text-white' 
                        : 'bg-gray-200 text-gray-400'
                    }`}>
                      {step.completed ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : step.current ? (
                        <Truck className="h-4 w-4" />
                      ) : (
                        <Package className="h-4 w-4" />
                      )}
                    </div>
                    
                    {/* Content */}
                    <div className="flex-1 pb-4">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className={`font-semibold ${
                            step.current ? 'text-blue-600' : step.completed ? 'text-green-600' : 'text-gray-600'
                          }`}>
                            {step.status}
                            {step.current && (
                              <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded-full">
                                Hiện tại
                              </span>
                            )}
                          </h4>
                          <span className={`text-sm ${
                            step.completed || step.current ? 'text-gray-700' : 'text-gray-400'
                          }`}>
                            {step.time}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                          <MapPinIcon className="h-4 w-4" />
                          <span>{step.location}</span>
                        </div>
                        
                        <p className={`text-sm ${
                          step.completed || step.current ? 'text-gray-700' : 'text-gray-400'
                        }`}>
                          {step.description}
                        </p>
                        
                        {/* Detailed Route for shipping status */}
                        {step.detailedRoute && (
                          <div className="mt-4 border-l-2 border-blue-200 pl-4">
                            <h5 className="text-sm font-semibold text-blue-600 mb-3 flex items-center">
                              <MapPinIcon className="h-4 w-4 mr-1" />
                              Chi tiết lộ trình vận chuyển
                            </h5>
                            <div className="space-y-3">
                              {step.detailedRoute.map((route: any, routeIndex: number) => (
                                <div key={routeIndex} className="relative">
                                  {routeIndex > 0 && (
                                    <div className="absolute left-3 top-0 w-0.5 h-4 bg-blue-200" />
                                  )}
                                  
                                  <div className="flex items-start gap-3">
                                    <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                                      route.status === 'Hiện tại'
                                        ? 'bg-blue-500 text-white animate-pulse'
                                        : route.status === 'Đã qua'
                                        ? 'bg-green-400 text-white'
                                        : 'bg-gray-300 text-gray-600'
                                    }`}>
                                      {route.status === 'Đã qua' ? '✓' : route.status === 'Hiện tại' ? '●' : '○'}
                                    </div>
                                    
                                    <div className="flex-1">
                                      <div className="flex justify-between items-start">
                                        <h6 className={`text-sm font-medium ${
                                          route.status === 'Hiện tại' ? 'text-blue-600' :
                                          route.status === 'Đã qua' ? 'text-green-600' : 'text-gray-500'
                                        }`}>
                                          {route.location}
                                          {route.status === 'Hiện tại' && (
                                            <span className="ml-2 bg-blue-100 text-blue-600 text-xs px-1.5 py-0.5 rounded">
                                              Hiện tại
                                            </span>
                                          )}
                                        </h6>
                                        <span className={`text-xs ${
                                          route.status === 'Sắp tới' ? 'text-gray-400' : 'text-gray-600'
                                        }`}>
                                          {route.time}
                                        </span>
                                      </div>
                                      <p className={`text-xs mt-1 ${
                                        route.status === 'Sắp tới' ? 'text-gray-400' : 'text-gray-600'
                                      }`}>
                                        {route.description}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Delivery Proof for completed orders */}
                        {step.deliveryProof && (
                          <div className="mt-4 border border-green-200 rounded-lg p-4 bg-green-50">
                            <h5 className="text-sm font-semibold text-green-700 mb-3 flex items-center">
                              <CheckCircle className="h-4 w-4 mr-1" />
                              {step.needsConfirmation ? 'Xác nhận nhận hàng' : 'Xác nhận giao hàng thành công'}
                            </h5>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {/* Receiver Info */}
                              <div>
                                <div className="mb-3">
                                  <p className="text-sm text-green-700">
                                    <strong>Người nhận:</strong> {step.deliveryProof.receiverName}
                                  </p>
                                  <p className="text-sm text-green-700">
                                    <strong>SĐT:</strong> {step.deliveryProof.receiverPhone}
                                  </p>
                                </div>
                                
                                {step.deliveryProof.note && (
                                  <div className="bg-white rounded-lg p-3">
                                    <p className="text-xs text-gray-600 mb-1"><strong>Ghi chú:</strong></p>
                                    <p className="text-sm text-gray-800">{step.deliveryProof.note}</p>
                                  </div>
                                )}
                              </div>
                              
                              {/* Delivery Images */}
                              <div>
                                <p className="text-sm font-medium text-green-700 mb-2">Hình ảnh xác nhận:</p>
                                <div className="grid grid-cols-2 gap-2">
                                  {step.deliveryProof.deliveryImages.map((image: string, imgIndex: number) => (
                                    <div key={imgIndex} className="relative group cursor-pointer">
                                      <img 
                                        src={image} 
                                        alt={`Hình giao hàng ${imgIndex + 1}`}
                                        className="w-full h-20 object-cover rounded border border-green-300 hover:border-green-500 transition-colors"
                                      />
                                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity rounded" />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                            
                            {/* Signature */}
                            {step.deliveryProof.signature && (
                              <div className="mt-4 pt-3 border-t border-green-200">
                                <p className="text-sm font-medium text-green-700 mb-2">Chữ ký xác nhẫn:</p>
                                <div className="bg-white rounded border border-green-300 p-2 inline-block">
                                  <img 
                                    src={step.deliveryProof.signature}
                                    alt="Chữ ký người nhận" 
                                    className="h-12 w-auto"
                                  />
                                </div>
                              </div>
                            )}
                            
                            {/* Confirmation Button */}
                            {step.needsConfirmation && (
                              <div className="mt-4 pt-3 border-t border-green-200">
                                <div className="flex justify-between items-center">
                                  <p className="text-sm text-green-700">
                                    Vui lòng xác nhận bạn đã nhận hàng thành công
                                  </p>
                                  <button
                                    onClick={() => handleConfirmDelivery(orderId)}
                                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                                  >
                                    <Check className="h-4 w-4" />
                                    Xác nhận nhận hàng
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                <p>Có thắc mắc? Liên hệ hotline: <span className="font-semibold text-blue-600">1900-1234</span></p>
              </div>
              <button
                onClick={handleCloseTracking}
                className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // AddressForm component để tái sử dụng
  const AddressForm = () => (
    <div className="border border-gray-300 rounded-lg p-6 bg-gray-50">
      <h3 className="font-semibold mb-4">
        {editingAddress ? 'Chỉnh sửa địa chỉ' : 'Thêm địa chỉ mới'}
      </h3>
      <div className="space-y-4">
        {/* Thông tin liên hệ */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Họ và tên *
            </label>
            <input
              type="text"
              value={newAddress.name}
              onChange={(e) => setNewAddress({...newAddress, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nhập họ và tên"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Số điện thoại *
            </label>
            <input
              type="tel"
              value={newAddress.phone}
              onChange={(e) => setNewAddress({...newAddress, phone: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nhập số điện thoại"
            />
          </div>
        </div>
        
        {/* Địa chỉ hành chính theo thứ tự: Tỉnh/TP → Phường/Xã → Đường/Khu/Ấp → Địa chỉ đặc biệt */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tỉnh/Thành phố *
            </label>
            <select
              value={newAddress.province}
              onChange={(e) => setNewAddress({...newAddress, province: e.target.value, ward: '', street: ''})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Chọn Tỉnh/Thành phố</option>
              <option value="TP.Hồ Chí Minh">TP.Hồ Chí Minh</option>
              <option value="Hà Nội">Hà Nội</option>
              <option value="Đà Nẵng">Đà Nẵng</option>
              <option value="Cần Thơ">Cần Thơ</option>
              <option value="Hải Phòng">Hải Phòng</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phường/Xã *
            </label>
            <select
              value={newAddress.ward}
              onChange={(e) => setNewAddress({...newAddress, ward: e.target.value, street: ''})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={!newAddress.province}
            >
              <option value="">Chọn Phường/Xã</option>
              {newAddress.province === 'TP.Hồ Chí Minh' && (
                <>
                  <option value="Phường Bến Nghé">Phường Bến Nghé</option>
                  <option value="Phường Bến Thành">Phường Bến Thành</option>
                  <option value="Phường Cô Giang">Phường Cô Giang</option>
                  <option value="Phường Nguyễn Thái Bình">Phường Nguyễn Thái Bình</option>
                </>
              )}
              {newAddress.province === 'Hà Nội' && (
                <>
                  <option value="Phường Lê Đại Hành">Phường Lê Đại Hành</option>
                  <option value="Phường Bách Khoa">Phường Bách Khoa</option>
                  <option value="Phường Hàng Bạc">Phường Hàng Bạc</option>
                </>
              )}
            </select>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Đường/Khu/Ấp *
          </label>
          <select
            value={newAddress.street}
            onChange={(e) => setNewAddress({...newAddress, street: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={!newAddress.ward}
          >
            <option value="">Chọn Đường/Khu/Ấp</option>
            {newAddress.ward === 'Phường Bến Nghé' && (
              <>
                <option value="Đường Lê Lợi">Đường Lê Lợi</option>
                <option value="Đường Nguyễn Huệ">Đường Nguyễn Huệ</option>
                <option value="Đường Đồng Khởi">Đường Đồng Khởi</option>
              </>
            )}
            {newAddress.ward === 'Phường Bến Thành' && (
              <>
                <option value="Đường Lê Thị Riêng">Đường Lê Thị Riêng</option>
                <option value="Đường Tôn Thất Đạm">Đường Tôn Thất Đạm</option>
              </>
            )}
            {newAddress.ward === 'Phường Lê Đại Hành' && (
              <>
                <option value="Đường Bà Triệu">Đường Bà Triệu</option>
                <option value="Đường Lê Đại Hành">Đường Lê Đại Hành</option>
              </>
            )}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Địa chỉ đặc biệt *
          </label>
          <textarea
            value={newAddress.specificAddress}
            onChange={(e) => setNewAddress({...newAddress, specificAddress: e.target.value})}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Số nhà, tầng, căn hộ, ghi chú thêm..."
          />
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={editingAddress ? handleUpdateAddress : handleAddAddress}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {editingAddress ? 'Cập nhật' : 'Thêm địa chỉ'}
          </button>
          <button
            onClick={handleCancelForm}
            className="border border-gray-300 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Hủy
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <CustomerLayout currentPage="account" onNavigate={onNavigate}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl text-white p-8 mb-8">
          <div className="flex flex-col md:flex-row items-center">
            <div className="relative mb-4 md:mb-0 md:mr-6">
              <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full overflow-hidden">
                {userInfo.avatar ? (
                  <img 
                    src={userInfo.avatar} 
                    alt="Avatar" 
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <User className="h-12 w-12" />
                  </div>
                )}
              </div>
              <label className="absolute -bottom-1 -right-1 w-8 h-8 bg-white text-blue-600 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-100 transition-colors">
                <Camera className="h-4 w-4" />
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleAvatarUpload}
                  className="hidden"
                />
              </label>
              
              {/* Nút xóa avatar - chỉ hiển thị khi có avatar */}
              {userInfo.avatar && (
                <button
                  onClick={handleAvatarDelete}
                  className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center cursor-pointer hover:bg-red-600 transition-colors"
                  title="Xóa avatar"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
            
            <div className="text-center md:text-left flex-1">
              <h1 className="text-3xl font-bold mb-2">{userInfo.name || 'Người dùng'}</h1>
              <p className="text-blue-100 mb-4">
                Thành viên từ {userInfo.memberSince ? new Date(userInfo.memberSince).getFullYear() : 'N/A'}
              </p>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold">{stats.totalOrders}</div>
                  <div className="text-sm text-blue-100">Đơn hàng</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{(stats.totalSpent / 1000000).toFixed(1)}M</div>
                  <div className="text-sm text-blue-100">Đã mua</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{stats.savedItems}</div>
                  <div className="text-sm text-blue-100">Yêu thích</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">{stats.loyaltyPoints}</div>
                  <div className="text-sm text-blue-100">Điểm tích lũy</div>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="mt-4 md:mt-0 bg-white bg-opacity-20 hover:bg-opacity-30 px-4 py-2 rounded-lg transition-colors flex items-center"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Đăng xuất
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <tab.icon className="h-5 w-5" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-lg p-8">
              {activeTab === 'profile' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Thông tin cá nhân</h2>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => loadUserProfile()}
                        disabled={loading}
                        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Tải lại</span>
                      </button>
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        disabled={loading}
                        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Edit className="h-4 w-4" />
                        <span>{loading ? 'Đang tải...' : isEditing ? 'Hủy' : 'Chỉnh sửa'}</span>
                      </button>
                    </div>
                  </div>

                  {loading ? (
                    <div className="flex justify-center items-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      <span className="ml-2 text-gray-600">Đang tải thông tin...</span>
                    </div>
                  ) : (
                    <>


                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Họ tên</label>
                      <div className="flex items-center space-x-3">
                        <User className="h-5 w-5 text-gray-400" />
                        <input
                          type="text"
                          value={userInfo.name}
                          disabled={!isEditing || loading}
                          onChange={(e) => setUserInfo({...userInfo, name: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                          placeholder="Nhập họ tên"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <div className="flex items-center space-x-3">
                        <Mail className="h-5 w-5 text-gray-400" />
                        <input
                          type="email"
                          value={userInfo.email}
                          disabled={!isEditing || loading}
                          onChange={(e) => setUserInfo({...userInfo, email: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                          placeholder="Nhập email"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Số điện thoại</label>
                      <div className="flex items-center space-x-3">
                        <Phone className="h-5 w-5 text-gray-400" />
                        <input
                          type="tel"
                          value={userInfo.phone}
                          disabled={!isEditing || loading}
                          onChange={(e) => setUserInfo({...userInfo, phone: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                          placeholder="Nhập số điện thoại"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Ngày sinh</label>
                      <div className="flex items-center space-x-3">
                        <Calendar className="h-5 w-5 text-gray-400" />
                        <input
                          type="date"
                          value={userInfo.birthday}
                          disabled={!isEditing}
                          onChange={(e) => setUserInfo({...userInfo, birthday: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                        />
                      </div>
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">Địa chỉ</label>
                      <div className="flex items-center space-x-3">
                        <MapPin className="h-5 w-5 text-gray-400" />
                        <input
                          type="text"
                          value={userInfo.address}
                          disabled={!isEditing}
                          onChange={(e) => setUserInfo({...userInfo, address: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-50"
                        />
                      </div>
                    </div>
                  </div>

                  {isEditing && (
                    <div className="mt-8 flex space-x-4">
                      <button
                        onClick={handleSave}
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? 'Đang lưu...' : 'Lưu thay đổi'}
                      </button>
                      <button
                        onClick={() => setIsEditing(false)}
                        className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Hủy bỏ
                      </button>
                    </div>
                  )}
                  </>
                  )}
                </div>
              )}

              {activeTab === 'orders' && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Lịch sử đơn hàng</h2>
                  
                  {/* Order Tabs */}
                  <div className="border-b border-gray-200 mb-6">
                    <div className="flex space-x-8 overflow-x-auto">
                      {orderTabs.map((tab) => (
                        <button
                          key={tab.id}
                          onClick={() => setOrderTab(tab.id)}
                          className={`py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors ${
                            orderTab === tab.id
                              ? 'border-blue-500 text-blue-600'
                              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                          }`}
                        >
                          {tab.label}
                          {tab.count > 0 && (
                            <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                              orderTab === tab.id
                                ? 'bg-blue-100 text-blue-600'
                                : 'bg-gray-100 text-gray-600'
                            }`}>
                              {tab.count}
                            </span>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Orders List */}
                  {filteredOrders.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="text-gray-400 mb-4">
                        <ShoppingBag className="h-16 w-16 mx-auto" />
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Không có đơn hàng nào</h3>
                      <p className="text-gray-500 mb-6">
                        {orderTab === 'all' 
                          ? 'Bạn chưa có đơn hàng nào. Hãy bắt đầu mua sắm ngay!' 
                          : `Bạn không có đơn hàng nào ở trạng thái "${orderTabs.find(t => t.id === orderTab)?.label}".`
                        }
                      </p>
                      <button 
                        onClick={() => onNavigate?.('home')}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Tiếp tục mua sắm
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {filteredOrders.map((order) => (
                        <div key={order.id} className="border border-gray-200 rounded-lg overflow-hidden">
                          {/* Order Header */}
                          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center gap-4">
                                <div>
                                  <h3 className="font-bold text-lg">Đơn hàng #{order.id}</h3>
                                  <p className="text-sm text-gray-600">Ngày đặt: {order.date}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <button
                                    onClick={() => onNavigate?.('store')}
                                    className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-colors group"
                                  >
                                    <img 
                                      src={order.shop.logo} 
                                      alt={order.shop.name}
                                      className="w-8 h-8 rounded-full object-cover"
                                    />
                                    <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600 transition-colors">{order.shop.name}</span>
                                  </button>
                                </div>
                              </div>
                              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                                {order.statusText}
                              </span>
                            </div>
                          </div>

                          {/* Products List */}
                          <div className="p-6">
                            <div className="space-y-4">
                              {order.items.map((item) => (
                                <div key={item.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors group">
                                  <img 
                                    src={item.image} 
                                    alt={item.name}
                                    className="w-20 h-20 object-cover rounded-lg border border-gray-200 group-hover:border-blue-300 transition-colors"
                                    onClick={() => onNavigate?.('product-detail', { productId: item.id })}
                                  />
                                  <div className="flex-1" onClick={() => onNavigate?.('product-detail', { productId: item.id })}>
                                    <h4 className="font-medium text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">{item.name}</h4>
                                    <p className="text-sm text-gray-600 mb-2">Phân loại: {item.variant}</p>
                                    <div className="flex items-center justify-between">
                                      <span className="text-sm text-gray-600">Số lượng: x{item.quantity}</span>
                                      <span className="font-bold text-lg text-blue-600">{formatPrice(item.price)}</span>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>

                            {/* Order Footer */}
                            <div className="mt-6 pt-4 border-t border-gray-200">
                              <div className="flex justify-between items-center">
                                <div className="text-sm text-gray-600">
                                  Tổng cộng: {order.items.length} sản phẩm
                                </div>
                                <div className="flex items-center gap-4">
                                  <div className="text-right">
                                    <p className="text-sm text-gray-600">Thành tiền:</p>
                                    <p className="font-bold text-xl text-red-600">{formatPrice(order.total)}</p>
                                  </div>
                                  <div className="flex gap-2">
                                    {order.status === 'pending' && (
                                      <button className="px-4 py-2 text-sm border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors">
                                        Hủy đơn
                                      </button>
                                    )}
                                    {order.status === 'completed' && (
                                      <>
                                        <button className="px-4 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                                          Mua lại
                                        </button>
                                        <button className="px-4 py-2 text-sm border border-yellow-300 text-yellow-600 rounded-lg hover:bg-yellow-50 transition-colors">
                                          Đánh giá
                                        </button>
                                      </>
                                    )}
                                    {order.status === 'delivering' && (
                                      <button 
                                        onClick={() => handleShowTracking(order.id)}
                                        className="px-4 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                                      >
                                        Theo dõi
                                      </button>
                                    )}
                                    {(order.status === 'shipping' || order.status === 'completed') && (
                                      <button 
                                        onClick={() => handleShowTracking(order.id)}
                                        className="px-4 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                                      >
                                        {order.status === 'completed' ? 'Xem chi tiết' : 'Theo dõi'}
                                      </button>
                                    )}
                                    {order.status === 'cancelled' && (
                                      <button className="px-4 py-2 text-sm border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors">
                                        Mua lại
                                      </button>
                                    )}
                                    {order.status === 'refund' && (
                                      <button className="px-4 py-2 text-sm border border-green-300 text-green-600 rounded-lg hover:bg-green-50 transition-colors">
                                        Liên hệ hỗ trợ
                                      </button>
                                    )}
                                    <button className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                      Chi tiết
                                    </button>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'addresses' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Địa chỉ giao hàng</h2>
                      <button
                      onClick={() => {
                        setEditingAddress(null);
                        setNewAddress({ name: '', phone: '', province: '', ward: '', street: '', specificAddress: '' });
                        setShowAddressForm(true);
                        setFormPosition('top'); // Form thêm mới ở trên
                      }}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                    >
                      <Plus className="h-4 w-4" />
                      Thêm địa chỉ mới
                    </button>
                  </div>

                  {/* Add Form at Top */}
                  {showAddressForm && formPosition === 'top' && <AddressForm />}

                  {/* Address List */}
                  <div className="space-y-4 mb-6">
                    {addresses.map((address) => (
                      <div key={address.id}>
                        <div className="border border-gray-200 rounded-lg p-6 relative">
                          <div className="pr-16">
                            <div className="flex items-center gap-3 mb-2">
                              <h4 className="font-semibold">{address.name}</h4>
                              <span className="text-gray-400">|</span>
                              <span className="text-gray-600">{address.phone}</span>
                              {address.isDefault && (
                                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center gap-1">
                                  <Check className="h-3 w-3" />
                                  Mặc định
                                </span>
                              )}
                            </div>
                            <p className="text-gray-700 mb-3">{address.address}</p>
                            
                            {!address.isDefault && (
                              <button
                                onClick={() => handleSetDefaultAddress(address.id)}
                                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                              >
                                Đặt làm mặc định
                              </button>
                            )}
                          </div>
                          
                          {/* Nút chỉnh sửa/xóa ở góc phải */}
                          <div className="absolute bottom-4 right-4 flex gap-2">
                            <button
                              onClick={() => handleEditAddress(address)}
                              className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                              title="Chỉnh sửa"
                            >
                              <Edit className="h-4 w-4" />
                            </button>
                            {!address.isDefault && (
                              <button
                                onClick={() => handleDeleteAddress(address.id)}
                                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Xóa"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            )}
                          </div>
                        </div>
                        
                        {/* Edit Form Below Address */}
                        {showAddressForm && formPosition === 'bottom' && editingAddress?.id === address.id && (
                          <div className="mt-4">
                            <AddressForm />
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                </div>
              )}

              {activeTab === 'vouchers' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Quản lý Voucher</h2>
                    <div className="text-sm text-gray-600">
                      Tổng: {userVouchers.length} voucher đã lưu
                    </div>
                  </div>

                  {/* Voucher Tabs */}
                  <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
                    {[
                      { id: 'available', label: 'Có thể dùng', count: userVouchers.filter(v => v.can_use && v.is_active && new Date(v.end_date) > new Date()).length },
                      { id: 'used', label: 'Đã sử dụng', count: userVouchers.filter(v => !v.can_use && v.used_count > 0).length },
                      { id: 'expired', label: 'Hết hạn', count: userVouchers.filter(v => !v.is_active || new Date(v.end_date) <= new Date()).length }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setVoucherTab(tab.id)}
                        className={`flex-1 py-3 px-4 rounded-md text-sm font-medium transition-colors ${
                          voucherTab === tab.id
                            ? 'bg-white text-blue-600 shadow-sm'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        {tab.label} ({tab.count})
                      </button>
                    ))}
                  </div>

                  {/* Voucher List */}
                  <div className="space-y-4">
                    {userVouchers
                      .filter(voucher => {
                        if (voucherTab === 'available') {
                          return voucher.can_use && voucher.is_active && new Date(voucher.end_date) > new Date();
                        } else if (voucherTab === 'used') {
                          return !voucher.can_use && voucher.used_count > 0;
                        } else if (voucherTab === 'expired') {
                          return !voucher.is_active || new Date(voucher.end_date) <= new Date();
                        }
                        return true;
                      })
                      .map((voucher) => {
                        const isExpired = new Date(voucher.end_date) <= new Date();
                        const isUsedUp = !voucher.can_use && voucher.used_count >= voucher.per_user_limit;
                        
                        return (
                          <div
                            key={voucher.voucher_id}
                            className={`border rounded-xl p-6 transition-all ${
                              voucher.can_use && !isExpired
                                ? 'border-blue-200 bg-blue-50 hover:shadow-md'
                                : 'border-gray-200 bg-gray-50 opacity-75'
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                {/* Voucher Header */}
                                <div className="flex items-center gap-3 mb-3">
                                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                                    voucher.type === 'platform' 
                                      ? 'bg-purple-100 text-purple-700' 
                                      : 'bg-green-100 text-green-700'
                                  }`}>
                                    <Tag className="h-3 w-3 mr-1" />
                                    {voucher.type === 'platform' ? 'Platform' : voucher.seller?.name}
                                  </div>
                                  
                                  {/* Status badges */}
                                  {isExpired && (
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700">
                                      Hết hạn
                                    </span>
                                  )}
                                  {isUsedUp && (
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                                      Đã hết lượt
                                    </span>
                                  )}
                                </div>

                                {/* Voucher Code */}
                                <div className="flex items-center gap-2 mb-2">
                                  <code className="bg-gray-800 text-white px-3 py-1 rounded font-mono text-lg font-bold">
                                    {voucher.code}
                                  </code>
                                  <button 
                                    onClick={() => navigator.clipboard.writeText(voucher.code)}
                                    className="text-blue-600 hover:text-blue-700 text-sm"
                                  >
                                    Sao chép
                                  </button>
                                </div>

                                {/* Voucher Details */}
                                <div className="text-gray-900 font-semibold text-lg mb-1">
                                  {voucher.discount_type === 'percent' 
                                    ? `Giảm ${voucher.discount_value}%${voucher.max_discount ? ` (tối đa ${formatPrice(voucher.max_discount)})` : ''}`
                                    : `Giảm ${formatPrice(voucher.discount_value)}`
                                  }
                                </div>

                                <p className="text-gray-600 mb-3">{voucher.description}</p>

                                {/* Voucher Info Grid */}
                                <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                  <div>
                                    <span className="font-medium">Đơn tối thiểu:</span> {formatPrice(voucher.min_order_amount)}
                                  </div>
                                  <div>
                                    <span className="font-medium">Hết hạn:</span> {new Date(voucher.end_date).toLocaleDateString('vi-VN')}
                                  </div>
                                  <div>
                                    <span className="font-medium">Đã dùng:</span> {voucher.used_count}/{voucher.per_user_limit}
                                  </div>
                                  <div>
                                    <span className="font-medium">Lưu từ:</span> {new Date(voucher.saved_at).toLocaleDateString('vi-VN')}
                                  </div>
                                </div>
                              </div>

                              {/* Action Button */}
                              <div className="ml-6">
                                {voucher.can_use && !isExpired ? (
                                  <button
                                    onClick={() => onNavigate?.('cart')}
                                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                                  >
                                    Dùng ngay
                                  </button>
                                ) : (
                                  <div className="text-gray-400 text-sm font-medium px-6 py-2">
                                    {isExpired ? 'Đã hết hạn' : isUsedUp ? 'Hết lượt dùng' : 'Không khả dụng'}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                  </div>

                  {/* Empty State */}
                  {userVouchers.filter(voucher => {
                    if (voucherTab === 'available') {
                      return voucher.can_use && voucher.is_active && new Date(voucher.end_date) > new Date();
                    } else if (voucherTab === 'used') {
                      return !voucher.can_use && voucher.used_count > 0;
                    } else if (voucherTab === 'expired') {
                      return !voucher.is_active || new Date(voucher.end_date) <= new Date();
                    }
                    return true;
                  }).length === 0 && (
                    <div className="text-center py-12">
                      <Gift className="h-16 w-16 mx-auto text-gray-300 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {voucherTab === 'available' && 'Không có voucher khả dụng'}
                        {voucherTab === 'used' && 'Chưa sử dụng voucher nào'}
                        {voucherTab === 'expired' && 'Không có voucher hết hạn'}
                      </h3>
                      <p className="text-gray-600 mb-6">
                        {voucherTab === 'available' && 'Hãy khám phá các voucher mới tại trang chính'}
                        {voucherTab === 'used' && 'Voucher đã sử dụng sẽ hiển thị ở đây'}
                        {voucherTab === 'expired' && 'Voucher hết hạn sẽ hiển thị ở đây'}
                      </p>
                      {voucherTab === 'available' && (
                        <button
                          onClick={() => onNavigate?.('promotions')}
                          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Khám phá voucher
                        </button>
                      )}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'settings' && (
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Cài đặt tài khoản</h2>
                  <div className="space-y-6">
                    <div className="border border-gray-200 rounded-lg p-6">
                      <h3 className="font-bold mb-2">Thông báo</h3>
                      <div className="space-y-3">
                        <label className="flex items-center">
                          <input type="checkbox" className="mr-3" defaultChecked />
                          <span>Nhận email về đơn hàng</span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="mr-3" defaultChecked />
                          <span>Nhận thông báo khuyến mãi</span>
                        </label>
                        <label className="flex items-center">
                          <input type="checkbox" className="mr-3" />
                          <span>Nhận SMS thông báo</span>
                        </label>
                      </div>
                    </div>

                    <div className="border border-gray-200 rounded-lg p-6">
                      <h3 className="font-bold mb-4">Bảo mật</h3>
                      <div className="space-y-3">
                        <button className="w-full text-left p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                          Đổi mật khẩu
                        </button>
                        <button className="w-full text-left p-3 border border-gray-300 rounded-lg hover:bg-gray-50">
                          Xác thực hai yếu tố
                        </button>
                      </div>
                    </div>

                    <div className="border border-red-200 rounded-lg p-6">
                      <h3 className="font-bold text-red-600 mb-2">Vùng nguy hiểm</h3>
                      <p className="text-gray-600 mb-4">Hành động này không thể hoàn tác</p>
                      <button className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                        Xóa tài khoản
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Loyalty Program */}
        <div className="mt-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl text-white p-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center mb-2">
                <Gift className="h-6 w-6 mr-2" />
                <h3 className="text-xl font-bold">Chương trình thành viên</h3>
              </div>
              <p className="mb-4">Bạn có {stats.loyaltyPoints} điểm tích lũy</p>
              <div className="w-64 bg-white bg-opacity-20 rounded-full h-2 mb-2">
                <div className="bg-white rounded-full h-2" style={{width: '65%'}}></div>
              </div>
              <p className="text-sm text-purple-100">Còn 550 điểm nữa để lên hạng Vàng</p>
            </div>
            <button className="bg-white text-purple-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition-colors font-medium">
              Đổi điểm
            </button>
          </div>
        </div>
      </div>

      {/* Tracking Modal */}
      {showTrackingModal && selectedOrderTracking && (
        <TrackingModal orderId={selectedOrderTracking} />
      )}
    </CustomerLayout>
  );
}