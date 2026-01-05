# Address Integration - AccountPage

## ✅ Hoàn thành tích hợp API địa chỉ thực vào AccountPage

### **Backend GraphQL API**

#### Types
- `AddressType`: Địa chỉ với fields `addressId`, `name`, `phoneNumber`, `province`, `ward`, `hamlet`, `detail`, `fullAddress`, `isDefault`

#### Queries
- `myAddresses`: Lấy tất cả địa chỉ của user (tự động từ `info.context.user`)
- `myDefaultAddress`: Lấy địa chỉ mặc định
- `address(addressId)`: Lấy địa chỉ theo ID

#### Mutations
- `addAddress`: Thêm địa chỉ mới
- `updateAddress`: Cập nhật địa chỉ
- `deleteAddress`: Xóa địa chỉ
- `setDefaultAddress`: Đặt địa chỉ làm mặc định

---

### **Frontend Implementation**

#### Services (`services/user/address.ts`)
```typescript
addressService.getAddresses()
addressService.addAddress(input)
addressService.updateAddress(input)
addressService.deleteAddress(addressId)
addressService.setDefaultAddress(addressId)
```

#### Hook (`hooks/user/address.tsx`)
```typescript
const {
  addresses,           // Address[]
  loading,            // boolean
  error,              // string | null
  fetchAddresses,     // () => Promise<void>
  addAddress,         // (input) => Promise<Result>
  updateAddress,      // (input) => Promise<Result>
  deleteAddress,      // (addressId) => Promise<Result>
  setDefaultAddress,  // (addressId) => Promise<Result>
  defaultAddress      // Address | null
} = useAddresses();
```

#### Address API (`services/callAPI/apiAddress.ts`)
```typescript
// Lấy danh sách tỉnh/thành phố
getProvinces(): Promise<Province[]>

// Lấy danh sách phường/xã theo tỉnh
getWards(provinceId): Promise<Ward[]>

// Lấy thôn/khu/ấp từ GHTK
getHamlets(provinceName, wardName): Promise<Result>
```

---

### **AccountPage Integration**

#### State Management
```typescript
// Real API data
const { addresses, loading, addAddress, updateAddress, deleteAddress, setDefaultAddress } = useAddresses();

// Address form state
const [provinces, setProvinces] = useState<any[]>([]);
const [wards, setWards] = useState<any[]>([]);
const [hamlets, setHamlets] = useState<any[]>([]);
const [newAddress, setNewAddress] = useState({
  name: '',
  phoneNumber: '',
  province: '',
  provinceId: '',
  ward: '',
  wardId: '',
  hamlet: '',
  detail: ''
});
```

#### Features Implemented
✅ **Hiển thị danh sách địa chỉ** - Load từ backend qua `useAddresses()`
✅ **Thêm địa chỉ mới** - Form với cascading dropdowns (Tỉnh → Phường → Thôn)
✅ **Cập nhật địa chỉ** - Edit inline với API call
✅ **Xóa địa chỉ** - Với confirmation dialog
✅ **Đặt mặc định** - Set default address
✅ **Loading states** - Hiển thị spinner khi đang tải
✅ **Empty state** - UI khi chưa có địa chỉ
✅ **API địa chỉ Việt Nam** - Tích hợp provinces.open-api.vn và GHTK

---

### **Address Form Flow**

1. **Load Provinces** - Auto load on mount từ `provinces.open-api.vn`
2. **Select Province** - User chọn → Load wards
3. **Select Ward** - User chọn → Load hamlets từ GHTK
4. **Select Hamlet** (optional) - User chọn hoặc bỏ qua
5. **Enter Detail** - Nhập số nhà, tầng, căn hộ
6. **Submit** - Call API `addAddress()` hoặc `updateAddress()`

---

### **UI/UX Improvements**

- **Form Position**: 
  - Top: Khi thêm mới
  - Bottom (inline): Khi edit địa chỉ cụ thể
  
- **Address Display**:
  - Name + Phone + Default badge
  - Full address từ backend (`fullAddress`)
  - Edit/Delete buttons (góc phải)
  - "Đặt làm mặc định" button (nếu chưa default)

- **Validation**:
  - Required fields: name, phoneNumber, province, ward, detail
  - Disabled submit khi loading

---

### **Testing**

1. ✅ Load addresses from API on page mount
2. ✅ Add new address → Success toast
3. ✅ Edit address → Update in list
4. ✅ Delete address → Confirmation → Remove from list
5. ✅ Set default → Update default badge
6. ✅ Province/Ward/Hamlet cascading works
7. ✅ Form validation prevents empty submission

---

### **Next Steps**

- [ ] Add avatar upload cho address (optional)
- [ ] Add map integration (Google Maps / OpenStreetMap)
- [ ] Add address suggestion based on GPS
- [ ] Cache provinces/wards data in localStorage
- [ ] Add address validation (geocoding)

---

### **Backend Notes**

- `Address.save()` automatically handles unique default per user
- `Address.set_as_default()` method available
- `full_address` property computed: `detail, hamlet, ward, province`
- Unique constraint: Only 1 default address per user
