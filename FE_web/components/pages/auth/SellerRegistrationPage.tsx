import React, { useState } from 'react';
import AuthLayout from '../../layout/AuthLayout';
import { 
  Store, 
  Mail, 
  Phone, 
  MapPin, 
  Plus, 
  ArrowRight, 
  ArrowLeft,
  Upload,
  Camera,
  IdCard,
  Building,
  FileText,
  CheckCircle,
  User,
  Globe
} from 'lucide-react';

interface SellerRegistrationPageProps {
  onComplete?: () => void;
  onBackToCustomer?: () => void;
}

type RegistrationStep = 'store-info' | 'shipping-setup' | 'identity-verification' | 'tax-info' | 'complete';

interface StoreInfo {
  shopName: string;
  address: string;
  email: string;
  phone: string;
}

interface IdentityInfo {
  nationality: string;
  idCardFront: File | null;
  idCardBack: File | null;
  biometricVerified: boolean;
  idNumber: string;
  fullName: string;
}

interface TaxInfo {
  businessType: 'individual' | 'household' | 'company';
  businessAddress: string;
  invoiceEmail: string;
  taxCode: string;
  dataConfirmation: boolean;
}

export default function SellerRegistrationPage({ onComplete, onBackToCustomer }: SellerRegistrationPageProps) {
  const [currentStep, setCurrentStep] = useState<RegistrationStep>('store-info');
  const [storeInfo, setStoreInfo] = useState<StoreInfo>({
    shopName: '',
    address: '',
    email: '',
    phone: ''
  });
  const [identityInfo, setIdentityInfo] = useState<IdentityInfo>({
    nationality: 'Việt Nam',
    idCardFront: null,
    idCardBack: null,
    biometricVerified: false,
    idNumber: '',
    fullName: ''
  });
  const [taxInfo, setTaxInfo] = useState<TaxInfo>({
    businessType: 'individual',
    businessAddress: '',
    invoiceEmail: '',
    taxCode: '',
    dataConfirmation: false
  });

  const steps = [
    { key: 'store-info', title: 'Thông tin Shop', icon: Store },
    { key: 'shipping-setup', title: 'Cài đặt vận chuyển', icon: MapPin },
    { key: 'identity-verification', title: 'Thông tin định danh', icon: IdCard },
    { key: 'tax-info', title: 'Thông tin thuế', icon: FileText },
    { key: 'complete', title: 'Hoàn tất', icon: CheckCircle }
  ];

  const getCurrentStepIndex = () => steps.findIndex(step => step.key === currentStep);

  const handleNext = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1].key as RegistrationStep);
    }
  };

  const handlePrevious = () => {
    const currentIndex = getCurrentStepIndex();
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1].key as RegistrationStep);
    }
  };

  const handleFileUpload = (field: 'idCardFront' | 'idCardBack') => (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setIdentityInfo(prev => ({ ...prev, [field]: file }));
    }
  };

  const renderStoreInfoStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Thông tin Shop</h2>
        <p className="text-gray-600 mt-2">Cung cấp thông tin cơ bản về cửa hàng của bạn</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Tên Shop
          </label>
          <input
            type="text"
            value={storeInfo.shopName}
            onChange={(e) => setStoreInfo(prev => ({ ...prev, shopName: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="shopIT"
            maxLength={30}
          />
          <div className="text-right text-sm text-gray-500 mt-1">
            {storeInfo.shopName.length}/30
          </div>
          {storeInfo.shopName && (
            <p className="text-sm text-red-500 mt-1">Tên Shop đã được sử dụng</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Địa chỉ lấy hàng
          </label>
          <button className="w-full px-3 py-3 border border-gray-300 rounded-lg text-left text-gray-500 hover:bg-gray-50">
            <Plus className="inline h-4 w-4 mr-2" />
            Thêm
          </button>
          <p className="text-sm text-red-500 mt-1">Vui lòng thiết lập địa chỉ lấy hàng của bạn</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Email
          </label>
          <input
            type="email"
            value={storeInfo.email}
            onChange={(e) => setStoreInfo(prev => ({ ...prev, email: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="tranhuuquoc12a10@gmail.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Số điện thoại
          </label>
          <input
            type="tel"
            value={storeInfo.phone}
            onChange={(e) => setStoreInfo(prev => ({ ...prev, phone: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="+84911547697"
          />
        </div>
      </div>
    </div>
  );

  const renderShippingSetupStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Cài đặt vận chuyển</h2>
        <p className="text-gray-600 mt-2">Thiết lập các tùy chọn vận chuyển cho cửa hàng</p>
      </div>

      <div className="space-y-4">
        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="font-medium mb-4">Hoa Tốc</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-white rounded border">
              <span>Hoa Tốc - Trong Ngày</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-3 bg-white rounded border">
              <div>
                <span>Hoa Tốc - 4 Giờ</span>
                <span className="text-red-500 text-sm ml-2">(COD đã được kích hoạt)</span>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="font-medium mb-4">Nhanh</h3>
          <div className="flex items-center justify-between p-3 bg-white rounded border">
            <div>
              <span>Nhanh</span>
              <span className="text-red-500 text-sm ml-2">(COD đã được kích hoạt)</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
            </label>
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="font-medium mb-4">Tự Nhận Hàng</h3>
          <div className="flex items-center justify-between p-3 bg-white rounded border">
            <span>Tự Nhận Hàng</span>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
            </label>
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-lg">
          <h3 className="font-medium mb-4">Hàng Cồng Kềnh</h3>
          <div className="flex items-center justify-between p-3 bg-white rounded border">
            <div>
              <span>Hàng Cồng Kềnh</span>
              <span className="text-red-500 text-sm ml-2">(COD đã được kích hoạt)</span>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
            </label>
          </div>
        </div>

        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-medium mb-2">Thêm đơn vị vận chuyển</h3>
          <p className="text-sm text-blue-700 mb-3">
            Lưu ý: Shopee khuyến khích bạn kích hoạt các đơn vị vận chuyển không có từ khóa lọc và cung cấp thông tin chính trác cho khách hàng để đảm bảo trải nghiệm bán hàng tối ưu. 
          </p>
        </div>
      </div>
    </div>
  );

  const renderIdentityVerificationStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Thông tin định danh</h2>
        <p className="text-gray-600 mt-2">Xác minh danh tính của bạn để đảm bảo an toàn</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Quốc tịch
          </label>
          <div className="relative">
            <Globe className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <select
              value={identityInfo.nationality}
              onChange={(e) => setIdentityInfo(prev => ({ ...prev, nationality: e.target.value }))}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Việt Nam">Việt Nam</option>
              <option value="Other">Khác</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">
            <span className="text-red-500">*</span> Hình chụp Căn cước công dân
          </label>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-2">Mặt trước</label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload('idCardFront')}
                  className="hidden"
                  id="idcard-front"
                />
                <label htmlFor="idcard-front" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Chọn ảnh hoặc kéo thả</p>
                  <p className="text-xs text-gray-500 mt-1">PNG, JPG tối đa 5MB</p>
                </label>
              </div>
              {identityInfo.idCardFront && (
                <p className="text-sm text-green-600 mt-2">✓ Đã tải lên</p>
              )}
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-2">Mặt sau</label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload('idCardBack')}
                  className="hidden"
                  id="idcard-back"
                />
                <label htmlFor="idcard-back" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">Chọn ảnh hoặc kéo thả</p>
                  <p className="text-xs text-gray-500 mt-1">PNG, JPG tối đa 5MB</p>
                </label>
              </div>
              {identityInfo.idCardBack && (
                <p className="text-sm text-green-600 mt-2">✓ Đã tải lên</p>
              )}
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <Camera className="h-6 w-6 text-blue-600" />
            <div>
              <h3 className="font-medium text-blue-900">Xác thực sinh trắc học</h3>
              <p className="text-sm text-blue-700">Chụp ảnh khuôn mặt để xác minh danh tính</p>
            </div>
          </div>
          <button
            onClick={() => setIdentityInfo(prev => ({ ...prev, biometricVerified: true }))}
            className="mt-3 w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {identityInfo.biometricVerified ? '✓ Đã xác thực' : 'Bắt đầu xác thực'}
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Số CCCD
          </label>
          <input
            type="text"
            value={identityInfo.idNumber}
            onChange={(e) => setIdentityInfo(prev => ({ ...prev, idNumber: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nhập số căn cước công dân"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Họ và Tên
          </label>
          <div className="relative">
            <User className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={identityInfo.fullName}
              onChange={(e) => setIdentityInfo(prev => ({ ...prev, fullName: e.target.value }))}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nhập họ và tên đầy đủ"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderTaxInfoStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Thông tin thuế</h2>
        <p className="text-gray-600 mt-2">Cung cấp thông tin để xử lý thuế và hóa đơn</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            <span className="text-red-500">*</span> Loại hình kinh doanh
          </label>
          <div className="space-y-3">
            {[
              { value: 'individual', label: 'Cá nhân' },
              { value: 'household', label: 'Hộ kinh doanh' },
              { value: 'company', label: 'Công ty' }
            ].map((option) => (
              <label key={option.value} className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="businessType"
                  value={option.value}
                  checked={taxInfo.businessType === option.value}
                  onChange={(e) => setTaxInfo(prev => ({ ...prev, businessType: e.target.value as any }))}
                  className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                />
                <span className="text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Địa chỉ đăng ký kinh doanh
          </label>
          <div className="relative">
            <Building className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={taxInfo.businessAddress}
              onChange={(e) => setTaxInfo(prev => ({ ...prev, businessAddress: e.target.value }))}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nhập địa chỉ đăng ký kinh doanh"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <span className="text-red-500">*</span> Email xác nhận hóa đơn điện tử
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              type="email"
              value={taxInfo.invoiceEmail}
              onChange={(e) => setTaxInfo(prev => ({ ...prev, invoiceEmail: e.target.value }))}
              className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nhập email nhận hóa đơn điện tử"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mã số thuế
          </label>
          <input
            type="text"
            value={taxInfo.taxCode}
            onChange={(e) => setTaxInfo(prev => ({ ...prev, taxCode: e.target.value }))}
            className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nhập mã số thuế (nếu có)"
          />
          <p className="text-sm text-gray-500 mt-1">Chỉ cần thiết cho hộ kinh doanh và công ty</p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <label className="flex items-start space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={taxInfo.dataConfirmation}
              onChange={(e) => setTaxInfo(prev => ({ ...prev, dataConfirmation: e.target.checked }))}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-1"
            />
            <span className="text-sm text-gray-700">
              <span className="text-red-500">*</span> Tôi xác nhận rằng tất cả dữ liệu đã cung cấp là chính xác và trung thực. 
              Tôi hiểu rằng việc cung cấp thông tin sai lệch có thể dẫn đến việc từ chối đơn đăng ký hoặc chấm dứt tài khoản.
            </span>
          </label>
        </div>
      </div>
    </div>
  );

  const renderCompleteStep = () => (
    <div className="text-center space-y-6">
      <div className="mx-auto w-24 h-24 bg-green-100 rounded-full flex items-center justify-center">
        <CheckCircle className="h-12 w-12 text-green-600" />
      </div>
      
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Đăng ký thành công!</h2>
        <p className="text-gray-600 text-lg">
          Cảm ơn bạn đã đăng ký làm seller trên SHOEX. 
          Chúng tôi sẽ xem xét hồ sơ của bạn trong vòng 1-2 ngày làm việc.
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-left">
        <h3 className="font-semibold text-blue-900 mb-3">Các bước tiếp theo:</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Xem xét hồ sơ và xác minh thông tin</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Gửi email xác nhận khi được duyệt</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span>Hướng dẫn sử dụng tài khoản seller</span>
          </li>
        </ul>
      </div>

      <button
        onClick={() => {
          onComplete?.();
          setCurrentStep('store-info'); // Reset for demo
        }}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
      >
        Hoàn tất
      </button>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'store-info':
        return renderStoreInfoStep();
      case 'shipping-setup':
        return renderShippingSetupStep();
      case 'identity-verification':
        return renderIdentityVerificationStep();
      case 'tax-info':
        return renderTaxInfoStep();
      case 'complete':
        return renderCompleteStep();
      default:
        return renderStoreInfoStep();
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 'store-info':
        return storeInfo.shopName && storeInfo.email && storeInfo.phone;
      case 'shipping-setup':
        return true; // Always can proceed from shipping setup
      case 'identity-verification':
        return identityInfo.nationality && identityInfo.idNumber && identityInfo.fullName && 
               identityInfo.biometricVerified && identityInfo.idCardFront && identityInfo.idCardBack;
      case 'tax-info':
        return taxInfo.businessType && taxInfo.businessAddress && taxInfo.invoiceEmail && 
               taxInfo.dataConfirmation;
      default:
        return true;
    }
  };

  if (currentStep === 'complete') {
    return (
      <AuthLayout title="Hoàn tất đăng ký">
        <div className="w-full max-w-2xl mx-auto">
          {renderCompleteStep()}
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Đăng ký Seller">
      <div className="w-full max-w-4xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.slice(0, -1).map((step, index) => {
              const isActive = step.key === currentStep;
              const isCompleted = getCurrentStepIndex() > index;
              const StepIcon = step.icon;
              
              return (
                <div key={step.key} className="flex flex-col items-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 ${
                    isCompleted 
                      ? 'bg-green-500 text-white' 
                      : isActive 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-200 text-gray-400'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="h-6 w-6" />
                    ) : (
                      <StepIcon className="h-6 w-6" />
                    )}
                  </div>
                  <span className={`text-sm font-medium ${
                    isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-500'
                  }`}>
                    {step.title}
                  </span>
                </div>
              );
            })}
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(getCurrentStepIndex() / (steps.length - 2)) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {renderCurrentStep()}

          {/* Navigation Buttons */}
          {['store-info', 'shipping-setup', 'identity-verification', 'tax-info'].includes(currentStep) && (
            <div className="flex justify-between mt-8 pt-6 border-t">
              <div className="flex space-x-3">
                {getCurrentStepIndex() > 0 && (
                  <button
                    onClick={handlePrevious}
                    className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>Quay lại</span>
                  </button>
                )}
                
                <button
                  onClick={onBackToCustomer}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Quay lại trang khách hàng
                </button>
              </div>

              <button
                onClick={getCurrentStepIndex() === steps.length - 2 ? () => setCurrentStep('complete') : handleNext}
                disabled={!canProceed()}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span>{getCurrentStepIndex() === steps.length - 2 ? 'Hoàn tất' : 'Tiếp theo'}</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}