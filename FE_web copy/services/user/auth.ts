/**
 * Authentication Service - Quản lý JWT tokens và API calls
 */

import { apiClient } from '../callAPI/apiClient';

interface LoginResponse {
  success: boolean;
  message: string;
  user?: {
    id: string;
    username: string;
    email: string;
    fullName: string;
    role: string;
  };
  tokens?: {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
  errors?: any;
}

interface ApiResponse<T = any> {
  data: T;
  errors?: any;
}

export class AuthService {
  private static instance: AuthService;
  private readonly API_URL = 'http://127.0.0.1:8000/graphql/';
  private listeners: Array<() => void> = [];

  // Event listener system
  addAuthStateListener(listener: () => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyAuthStateChange() {
    this.listeners.forEach(listener => listener());
  }

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  // Lưu tokens vào localStorage
  private saveTokens(tokens: { accessToken: string; refreshToken: string }) {
    localStorage.setItem('accessToken', tokens.accessToken);
    localStorage.setItem('refreshToken', tokens.refreshToken);
  }

  // Lấy tokens từ localStorage
  private getTokens() {
    return {
      accessToken: localStorage.getItem('accessToken'),
      refreshToken: localStorage.getItem('refreshToken')
    };
  }

  // Xóa tokens
  private clearTokens() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  // Kiểm tra token có hết hạn không
  private isTokenExpired(token: string): boolean {
    if (!token) return true;

    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      const currentTime = Math.floor(Date.now() / 1000);
      return decoded.exp < currentTime;
    } catch {
      return true;
    }
  }

  // Lấy thông tin user từ token
  getUserFromToken(token: string) {
    try {
      const payload = token.split('.')[1];
      return JSON.parse(atob(payload));
    } catch {
      return null;
    }
  }

  // Đăng nhập
  async login(username: string, password: string): Promise<LoginResponse> {
    try {
      console.log('🚀 Attempting login to:', this.API_URL);

      const query = `
        mutation {
          login(input: {
            username: "${username}"
            password: "${password}"
          }) {
            success
            message
            user {
              id
              username
              email
              fullName
              role
            }
            tokens {
              accessToken
              refreshToken
              expiresIn
            }
            errors {
              field
              messages
            }
          }
        }
      `;

      console.log('📤 Sending GraphQL query:', query);

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        console.error('❌ Response not OK:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('❌ Error response body:', errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        console.error('❌ Response không phải JSON, content-type:', contentType);
        const responseText = await response.text();
        console.error('❌ Response body:', responseText.substring(0, 500));
        throw new Error('Server trả về HTML thay vì JSON. Có thể GraphQL endpoint sai hoặc server lỗi.');
      }

      const result: ApiResponse = await response.json();
      console.log('✅ Login response:', result);

      const loginData = result.data.login;

      if (loginData.success && loginData.tokens) {
        // Lưu tokens
        this.saveTokens(loginData.tokens);

        // Lưu thông tin user
        if (loginData.user) {
          localStorage.setItem('user', JSON.stringify(loginData.user));
        }
        
        // Notify auth state change
        this.notifyAuthStateChange();
      }

      return loginData;
    } catch (error) {
      console.error('💥 Login error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi kết nối server',
        errors: { general: 'Network error' }
      };
    }
  }

  // Refresh token
  async refreshToken(): Promise<boolean> {
    const { refreshToken } = this.getTokens();

    if (!refreshToken) {
      return false;
    }

    try {
      const query = `
        mutation {
          refreshToken(input: {
            refreshToken: "${refreshToken}"
          }) {
            success
            tokens {
              accessToken
              refreshToken
              expiresIn
            }
            errors {
              general
            }
          }
        }
      `;

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const result: ApiResponse = await response.json();
      const refreshData = result.data.refreshToken;

      if (refreshData.success && refreshData.tokens) {
        this.saveTokens(refreshData.tokens);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Refresh token error:', error);
      return false;
    }
  }

  // Gọi API không cần xác thực
  async publicApiCall(query: string, variables?: any): Promise<ApiResponse> {
    return apiClient.publicApiCall(query, variables);
  }

  // Gọi API với authentication tự động
  async apiCall(query: string, variables?: any): Promise<ApiResponse> {
    return apiClient.authenticatedApiCall(query, variables);
  }

  // Đăng xuất
  logout() {
    this.clearTokens();
    this.notifyAuthStateChange();
  }

  // Kiểm tra đã đăng nhập chưa
  isAuthenticated(): boolean {
    const { accessToken } = this.getTokens();
    return accessToken !== null && !this.isTokenExpired(accessToken);
  }

  // Lấy thông tin user hiện tại
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Đăng ký
  async register(userData: {
    fullName: string;
    username: string;
    email: string;
    password: string;
    birthDate?: string; // Format: YYYY-MM-DD
  }) {
    try {
      console.log('🚀 Attempting register to:', this.API_URL);

      const query = `
        mutation {
          register(input: {
            fullName: "${userData.fullName}"
            username: "${userData.username}"
            email: "${userData.email}"
            password: "${userData.password}"
            ${userData.birthDate ? `birthDate: "${userData.birthDate}"` : ''}
          }) {
            success
            message
            user {
              id
              username
              email
              fullName
              birthDate
              age
              role
            }
     
          }
        }
      `;

      console.log('📤 Sending GraphQL register query');

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      console.log('📥 Register response status:', response.status);

      if (!response.ok) {
        console.error('❌ Register response not OK:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('❌ Register error response body:', errorText.substring(0, 500));
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        console.error('❌ Register response không phải JSON, content-type:', contentType);
        const responseText = await response.text();
        console.error('❌ Register response body:', responseText.substring(0, 500));
        throw new Error('Server trả về HTML thay vì JSON cho register. Có thể GraphQL endpoint sai hoặc server lỗi.');
      }

      const result: ApiResponse = await response.json();
      console.log('✅ Register response:', result);

      return result.data.register;
    } catch (error) {
      console.error('💥 Register error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi kết nối server',
        errors: { general: 'Network error' }
      };
    }
  }

  // Lấy thông tin chi tiết user
  async getUserProfile(userId?: string): Promise<{ success: boolean, user?: any, message?: string }> {
    try {
      // Không cần userId nữa, dùng info.context.user từ backend
      const query = `
        query {
          userProfile {
            user {
              id
              username
              email
              fullName
              firstName
              lastName
              phone
              birthDate
              age
              role
              avatarUrl
              isActive
              dateJoined
              lastLogin
            }
          }
        }
      `;

      const result = await this.apiCall(query);
      console.log('Get user profile result:', result);

      if (result.data.userProfile) {
        const userProfile = result.data.userProfile.user;
        localStorage.setItem('user', JSON.stringify(userProfile));
        return {
          success: true,
          user: userProfile
        };
      }

      return {
        success: false,
        message: 'Không thể lấy thông tin user'
      };
    } catch (error) {
      console.error('Get user profile error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi khi lấy thông tin user'
      };
    }
  }

  // Xóa avatar
  async deleteAvatar(): Promise<{ success: boolean, message?: string }> {
    try {
      const query = `
        mutation {
          avatarDelete {
            success
            message
            user {
              id
              username
              email
              fullName
              firstName
              lastName
              phone
              birthDate
              age
              role
              avatarUrl
              isActive
              dateJoined
              lastLogin
            }
          }
        }
      `;

      const result = await this.apiCall(query);

      if (result.data?.avatarDelete?.success) {
        const deleteData = result.data.avatarDelete;

        // Cập nhật thông tin user trong localStorage
        if (deleteData.user) {
          localStorage.setItem('user', JSON.stringify(deleteData.user));
        }

        return {
          success: true,
          message: deleteData.message
        };
      }

      return {
        success: false,
        message: result.data?.avatarDelete?.message || 'Xóa avatar thất bại'
      };
    } catch (error) {
      console.error('Delete avatar error:', error);
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi khi xóa avatar'
      };
    }
  }

  // Cập nhật thông tin user
  async updateUserProfile(userData: {
    fullName?: string;
    firstName?: string;
    lastName?: string;
    phone?: string;
    email?: string;
    birthDate?: string; // Format: YYYY-MM-DD
  }): Promise<{ success: boolean, user?: any, message?: string }> {
    try {
      console.log('🔄 UpdateUserProfile được gọi với:', userData);

      // Lấy thông tin user hiện tại để có ID
      let currentUser = this.getCurrentUser();
      if (!currentUser || !currentUser.id) {
        // Thử lấy user ID từ token nếu localStorage không có
        const { accessToken } = this.getTokens();
        if (accessToken) {
          try {
            const payload = accessToken.split('.')[1];
            const decoded = JSON.parse(atob(payload));
            const tokenUserId = decoded.user_id || decoded.sub;
            
            if (tokenUserId) {
              console.log('🔍 Using user ID from token:', tokenUserId);
              currentUser = { id: tokenUserId.toString() };
            } else {
              return {
                success: false,
                message: 'Không tìm thấy thông tin user hiện tại (ID missing in token)'
              };
            }
          } catch (e) {
            return {
              success: false,
              message: 'Không thể decode token để lấy user ID'
            };
          }
        } else {
          return {
            success: false,
            message: 'Không tìm thấy thông tin user hiện tại (no token)'
          };
        }
      }

      console.log('🆔 FINAL USER ID WILL BE USED:', currentUser.id);
      console.log('📝 Raw Input userData:', userData);

      // Tạo dynamic input fields theo API chuẩn
      const inputFields = [];
      
      if (userData.fullName?.trim()) {
        inputFields.push(`fullName: "${userData.fullName.trim()}"`);
      }
      if (userData.firstName?.trim()) {
        inputFields.push(`firstName: "${userData.firstName.trim()}"`);
      }
      if (userData.lastName?.trim()) {
        inputFields.push(`lastName: "${userData.lastName.trim()}"`);
      }
      if (userData.phone?.trim()) {
        inputFields.push(`phone: "${userData.phone.trim()}"`);
      }
      if (userData.email?.trim()) {
        inputFields.push(`email: "${userData.email.trim()}"`);
      }
      
      // Handle birthDate với validation chi tiết
      if (userData.birthDate?.trim()) {
        const birthDateValue = userData.birthDate.trim();
        console.log('🗓️ Processing birthDate:', birthDateValue);
        
        // Validate YYYY-MM-DD format
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (dateRegex.test(birthDateValue)) {
          inputFields.push(`birthDate: "${birthDateValue}"`);
          console.log('✅ BirthDate đã được thêm vào query:', birthDateValue);
        } else {
          console.log('❌ BirthDate format không hợp lệ (cần YYYY-MM-DD):', birthDateValue);
        }
      } else {
        console.log('❌ BirthDate bị bỏ qua (empty hoặc undefined):', userData.birthDate);
      }

      console.log('📋 Danh sách fields sẽ gửi:', inputFields);

      if (inputFields.length === 0) {
        return {
          success: false,
          message: 'Không có dữ liệu để cập nhật'
        };
      }

      // Sử dụng userUpdate API chuẩn với ID
      const updateQuery = `
        mutation {
          userUpdate(
            id: "${currentUser.id}"
            input: {
              ${inputFields.join('\n              ')}
            }
          ) {
            success
            user {
              id
              username
              email
              fullName
              firstName
              lastName
              phone
              birthDate
              age
              role
              avatarUrl
              isActive
              dateJoined
              lastLogin
            }
            errors
          }
        }
      `;

      console.log('🔄 Sending userUpdate mutation query:', updateQuery);
      
      // Gửi mutation qua apiCall để luôn có token (giống getUserProfile)
      const result = await this.apiCall(updateQuery);

      // Nếu update thành công, gọi lại getUserProfile để đồng bộ user từ backend
      if (result.data?.userUpdate?.success) {
        await this.getUserProfile();
        return {
          success: true,
          user: result.data.userUpdate.user,
          message: 'Cập nhật thành công'
        };
      } else {
        return {
          success: false,
          message: result.data?.userUpdate?.errors || 'Cập nhật thất bại'
        };
      }
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Lỗi khi cập nhật thông tin'
      };
    }
  }

  // Lấy thông tin user từ API
  async getUserInfo(): Promise<LoginResponse> {
    try {
      const query = `
        query {
          me {
            id
            username
            email
            fullName: full_name
            firstName: first_name
            lastName: last_name
            phone
            role
            avatarUrl: avatar_url
            isActive: is_active
            dateJoined: date_joined
            lastLogin: last_login
          }
        }
      `;

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.getTokens().accessToken}`
        },
        body: JSON.stringify({ query })
      });

      const result: ApiResponse = await response.json();

      if (result.errors) {
        console.error('❌ GraphQL errors:', result.errors);
        return {
          success: false,
          message: result.errors[0]?.message || 'Lỗi lấy thông tin user',
          errors: result.errors
        };
      }

      return {
        success: true,
        message: 'Lấy thông tin user thành công',
        user: result.data.me
      };

    } catch (error) {
      console.error('💥 getUserInfo error:', error);
      return {
        success: false,
        message: 'Lỗi kết nối server'
      };
    }
  }

  // Upload avatar
  async uploadAvatar(file: File): Promise<{ success: boolean; message: string; avatarUrl?: string }> {
    try {
      const formData = new FormData();

      // Tạo operations cho GraphQL multipart request
      const operations = {
        query: `
          mutation($input: AvatarUploadInput!) {
            avatarUpload(input: $input) {
              success
              message
              avatarUrl
              user {
                id
                avatarUrl: avatar_url
              }
            }
          }
        `,
        variables: {
          input: {
            avatar: null
          }
        }
      };

      const map = {
        '0': ['variables.input.avatar']
      };

      formData.append('operations', JSON.stringify(operations));
      formData.append('map', JSON.stringify(map));
      formData.append('0', file);

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getTokens().accessToken}`
        },
        body: formData
      });

      const result: ApiResponse = await response.json();

      if (result.errors) {
        console.error('❌ Upload avatar errors:', result.errors);
        return {
          success: false,
          message: result.errors[0]?.message || 'Lỗi upload avatar'
        };
      }

      const uploadResult = result.data.avatarUpload;
      return {
        success: uploadResult.success,
        message: uploadResult.message,
        avatarUrl: uploadResult.avatarUrl
      };

    } catch (error) {
      console.error('💥 uploadAvatar error:', error);
      return {
        success: false,
        message: 'Lỗi kết nối server'
      };
    }
  }
}

  // Export singleton instance
export const authService = AuthService.getInstance();

// Thêm function helper để test token và debug
export const debugTokenStatus = () => {
  const token = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  const user = localStorage.getItem('user');

  console.log('=== TOKEN STATUS DEBUG ===');
  
  if (!token) {
    console.log('❌ Không có access token');
    return false;
  }

  try {
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    const currentTime = Math.floor(Date.now() / 1000);
    const timeLeft = decoded.exp - currentTime;
    
    console.log('📊 Token Info:', {
      userId: decoded.user_id || decoded.sub,
      username: decoded.username,
      expiresAt: new Date(decoded.exp * 1000).toLocaleString('vi-VN'),
      currentTime: new Date().toLocaleString('vi-VN'),
      timeLeftSeconds: timeLeft,
      timeLeftMinutes: Math.round(timeLeft / 60),
      isExpired: timeLeft <= 0,
      hasRefreshToken: !!refreshToken,
      currentUser: user ? JSON.parse(user).username : 'No user info'
    });

    if (timeLeft <= 0) {
      console.log('⚠️ TOKEN ĐÃ HẾT HẠN!');
      return false;
    } else if (timeLeft < 300) { // < 5 phút
      console.log('⚠️ Token sắp hết hạn trong ' + Math.round(timeLeft / 60) + ' phút');
    } else {
      console.log('✅ Token còn hiệu lực');
    }
    
    return true;
  } catch (e) {
    console.error('❌ Lỗi decode token:', e);
    return false;
  }
};

// Function test refresh token
export const testRefreshToken = async () => {
  console.log('🔄 Testing refresh token...');
  const result = await authService.refreshToken();
  console.log('Refresh result:', result);
  
  if (result) {
    console.log('✅ Refresh thành công, token mới:');
    debugTokenStatus();
  } else {
    console.log('❌ Refresh thất bại');
  }
  
  return result;
};

// Test trực tiếp với fetch để so sánh
export const testDirectUserUpdate = async () => {
  console.log('🧪 Testing direct fetch userUpdate...');
  
  const currentUser = authService.getCurrentUser();
  const token = localStorage.getItem('accessToken');
  
  if (!currentUser?.id || !token) {
    console.error('❌ Missing user ID or token');
    return;
  }
  
  const query = `
    mutation {
      userUpdate(
        id: "${currentUser.id}"
        input: {
          fullName: "Test Direct Fetch"
        }
      ) {
        success
        user {
          id
          fullName
        }
        errors
      }
    }
  `;
  
  console.log('📤 Direct fetch query:', query);
  console.log('🔐 Using token:', token.substring(0, 20) + '...');
  
  try {
    const response = await fetch('http://127.0.0.1:8000/graphql/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        // Thử thêm headers khác nếu cần
        'Accept': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ query })
    });
    
    console.log('📡 Direct response status:', response.status);
    console.log('📡 Direct response headers:', Object.fromEntries(response.headers.entries()));
    
    const result = await response.json();
    console.log('📥 Direct result:', result);
    
    return result;
  } catch (error) {
    console.error('💥 Direct fetch error:', error);
    return null;
  }
};

// Debug function để kiểm tra user ID và permissions
export const debugUserPermissions = async () => {
  console.log('🔍 Debugging User Permissions...');
  
  // 1. Check current user info
  const currentUser = authService.getCurrentUser();
  console.log('Current user from localStorage:', currentUser);
  
  // 2. Check token payload
  const token = localStorage.getItem('accessToken');
  if (token) {
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      console.log('Token payload:', decoded);
      console.log('User ID from token:', decoded.user_id || decoded.sub);
    } catch (e) {
      console.error('Cannot decode token:', e);
    }
  }
  
  // 3. Get fresh user profile
  const profileResult = await authService.getUserProfile();
  console.log('Fresh user profile:', profileResult);
  
  // 4. Test update current user vs other user
  const currentUserId = currentUser?.id || '3'; // Default to 3 if not found
  
  console.log(`\n--- Testing Current User ID (${currentUserId}) ---`);
  const selfResult = await debugUserUpdate(currentUserId);
  console.log('Self update result:', selfResult);
  
  console.log(`\n--- Testing Other User ID (1) ---`);
  const otherResult = await debugUserUpdate('1');
  console.log('Other user update result:', otherResult);
  
  console.log(`\n--- Testing Other User ID (2) ---`);
  const other2Result = await debugUserUpdate('2');
  console.log('Other user update result:', other2Result);
  
  return {
    currentUser,
    profileResult,
    selfResult,
    otherResult,
    other2Result
  };
};

// Debug function để test nhiều ID
export const debugUserUpdate = async (testId: string) => {
  console.log(`🧪 Testing userUpdate with ID: ${testId}`);
  
  try {
    const testQuery = `
      mutation {
        userUpdate(
          id: "${testId}"
          input: {
            fullName: "Test Update ID ${testId}"
          }
        ) {
          success
          user {
            id
            username
            fullName
          }
          errors
        }
      }
    `;
    
    console.log('Query:', testQuery);
    
    const result = await authService.apiCall(testQuery);
    console.log(`Result for ID ${testId}:`, result);
    
    if (result.data?.userUpdate?.success) {
      console.log(`✅ ID ${testId}: SUCCESS`);
      return { success: true, data: result.data.userUpdate };
    } else {
      console.log(`❌ ID ${testId}: FAILED`);
      console.log('Error:', result.data?.userUpdate?.errors);
      return { success: false, error: result.data?.userUpdate?.errors };
    }
    
  } catch (error) {
    console.error(`💥 ID ${testId}: EXCEPTION`, error);
    return { success: false, exception: error };
  }
};

// Test nhiều ID một lúc
export const testMultipleIds = async () => {
  console.log('🔍 Testing multiple user IDs...');
  
  // Lấy ID của user hiện tại
  const currentUser = authService.getCurrentUser();
  console.log('Current user:', currentUser);
  
  // Test các ID khác nhau
  const testIds = ['1', '2', '3', '4', '5'];
  
  for (const id of testIds) {
    console.log(`\n--- Testing ID: ${id} ---`);
    const result = await debugUserUpdate(id);
    
    if (id === currentUser?.id) {
      console.log(`👤 This is current user's ID`);
    }
    
    // Đợi một chút để không spam server
    await new Promise(resolve => setTimeout(resolve, 500));
  }
};

// Test API với token hiện tại
export const testCurrentAPI = async () => {
  console.log('🧪 Testing current API...');
  
  // Test 0: Debug token trước
  console.log('0️⃣ Current token status:');
  debugTokenStatus();
  
  // Test 1: getUserProfile (đã hoạt động)
  console.log('1️⃣ Testing getUserProfile (should work):');
  const profileResult = await authService.getUserProfile();
  console.log('getUserProfile result:', profileResult);
  
  // Test 2: Raw userUpdate API call để test authentication
  console.log('2️⃣ Testing raw userUpdate mutation with minimal data:');
  try {
    const currentUser = authService.getCurrentUser();
    if (currentUser && currentUser.id) {
      const simpleQuery = `
        mutation {
          userUpdate(
            id: "${currentUser.id}"
            input: {
              fullName: "Test Name API"
            }
          ) {
            success
            user {
              id
              fullName
              birthDate
            }
            errors
          }
        }
      `;
      console.log('Sending raw userUpdate mutation:', simpleQuery);
      
      const rawResult = await authService.apiCall(simpleQuery);
      console.log('Raw userUpdate result:', rawResult);
    } else {
      console.log('❌ No current user found for raw test');
    }
  } catch (error) {
    console.error('Raw userUpdate error:', error);
  }
  
  // Test 3: updateUserProfile wrapper với API mới
  console.log('3️⃣ Testing updateUserProfile wrapper with userUpdate API:');
  const updateResult = await authService.updateUserProfile({
    fullName: 'Test Update Name Wrapper'
  });
  console.log('updateUserProfile wrapper result:', updateResult);
  
  // Test 4: Test với birthDate
  console.log('4️⃣ Testing updateUserProfile with birthDate:');
  const birthDateResult = await authService.updateUserProfile({
    fullName: 'Test Birth Date',
    birthDate: '1990-05-15'
  });
  console.log('updateUserProfile birthDate result:', birthDateResult);
  
  return { profileResult, updateResult, birthDateResult };
};