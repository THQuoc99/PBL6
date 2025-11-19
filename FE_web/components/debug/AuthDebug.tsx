import React from 'react';
import { authService } from '../../services/auth';

export default function AuthDebug() {
  const handleTestAuth = async () => {
    console.log('🔍 Testing authentication...');
    console.log('Authentication status:', authService.isAuthenticated());
    console.log('Current user:', authService.getCurrentUser());
    console.log('Access token:', localStorage.getItem('accessToken'));
    console.log('Refresh token:', localStorage.getItem('refreshToken'));
    
    try {
      const response = await authService.getUserProfile();
      console.log('getUserProfile response:', response);
    } catch (error) {
      console.error('getUserProfile error:', error);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-yellow-50">
      <h3 className="font-bold mb-2">🔧 Auth Debug Panel</h3>
      <button 
        onClick={handleTestAuth}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Test Authentication
      </button>
      
      <div className="mt-4 space-y-2">
        <div><strong>Authentication:</strong> {authService.isAuthenticated() ? '✅' : '❌'}</div>
        <div><strong>Access Token:</strong> {localStorage.getItem('accessToken') ? '✅ Present' : '❌ Missing'}</div>
        <div><strong>User in localStorage:</strong> {authService.getCurrentUser() ? '✅ Present' : '❌ Missing'}</div>
      </div>
    </div>
  );
}