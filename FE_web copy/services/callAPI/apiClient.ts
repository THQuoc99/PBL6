/**
 * API Client - Centralized API communication
 * Handles GraphQL requests với authentication và error handling
 */

interface ApiResponse<T = any> {
  data: T;
  errors?: any;
}

export class ApiClient {
  private static instance: ApiClient;
  private readonly API_URL = 'http://127.0.0.1:8000/graphql/';

  static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  /**
   * Gọi API công khai (không cần authentication)
   */
  async publicApiCall(query: string, variables?: any): Promise<ApiResponse> {
    try {
      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ query, variables }),
      });
      
      return await response.json();
    } catch (error) {
      console.error('Public API call error:', error);
      throw error;
    }
  }

  /**
   * Gọi API với authentication (requires token)
   */
  async authenticatedApiCall(query: string, variables?: any): Promise<ApiResponse> {
    const accessToken = localStorage.getItem('accessToken');
    
    if (!accessToken) {
      throw new Error('No access token available');
    }

    // Check token expiration
    if (this.isTokenExpired(accessToken)) {
      const refreshed = await this.refreshToken();
      if (!refreshed) {
        throw new Error('Token expired and refresh failed');
      }
    }

    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        credentials: 'include',
        body: JSON.stringify({ query, variables }),
      });

      // Handle 401 - try refresh
      if (response.status === 401) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          // Retry with new token
          const newToken = localStorage.getItem('accessToken');
          const retryResponse = await fetch(this.API_URL, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${newToken}`,
            },
            credentials: 'include',
            body: JSON.stringify({ query, variables }),
          });
          return await retryResponse.json();
        } else {
          this.clearTokens();
          throw new Error('Authentication failed');
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Authenticated API call error:', error);
      throw error;
    }
  }

  /**
   * Gửi mutation/query với Uploads (GraphQL multipart request)
   * files: { variableName: File }
   */
  async authenticatedMultipartCall(query: string, variables: any = {}, files: { [key: string]: File | null } = {}): Promise<ApiResponse> {
    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
      throw new Error('No access token available');
    }

    if (this.isTokenExpired(accessToken)) {
      const refreshed = await this.refreshToken();
      if (!refreshed) {
        throw new Error('Token expired and refresh failed');
      }
    }

    try {
      const token = localStorage.getItem('accessToken');

      // Ensure variables contain placeholders for file vars (must be null in operations)
      // Support nested variable paths like 'input.images.0.image'
      const opsVariables = { ...(variables || {}) };
      const setNestedNull = (obj: any, path: string) => {
        const parts = path.split('.');
        let cur = obj;
        for (let i = 0; i < parts.length - 1; i++) {
          const p = parts[i];
          // if index numeric, treat as array
          const idx = Number(p);
          if (!isNaN(idx)) {
            if (!Array.isArray(cur)) cur = cur[parts.slice(0, i).join('.')] = [];
            if (!cur[idx]) cur[idx] = {};
            cur = cur[idx];
          } else {
            if (!(p in cur) || typeof cur[p] !== 'object') cur[p] = {};
            cur = cur[p];
          }
        }
        const last = parts[parts.length - 1];
        const lastIdx = Number(last);
        if (!isNaN(lastIdx)) {
          if (!Array.isArray(cur)) cur = cur[parts.slice(0, parts.length - 1).join('.')] = [];
          cur[lastIdx] = null;
        } else {
          cur[last] = null;
        }
      };
      Object.keys(files || {}).forEach((varName) => {
        setNestedNull(opsVariables, varName);
      });

      const operations = JSON.stringify({ query, variables: opsVariables });

      // Build map according to GraphQL multipart request spec
      const map: { [key: string]: string[] } = {};
      const form = new FormData();
      let fileIndex = 0;
      for (const varName of Object.keys(files || {})) {
        const f = files[varName];
        if (!f) continue;
        map[String(fileIndex)] = [`variables.${varName}`];
        form.append(String(fileIndex), f);
        fileIndex += 1;
      }

      form.append('operations', operations);
      form.append('map', JSON.stringify(map));

      // Debug: log operations/map and FormData file names to help diagnose upload issues
      try {
        console.debug('authenticatedMultipartCall operations:', operations);
        console.debug('authenticatedMultipartCall map:', map);
        for (const entry of (form as any).entries()) {
          const [key, value] = entry as [string, any];
          if (value instanceof File) {
            console.debug(`FormData entry: ${key} -> File name=${value.name} type=${value.type} size=${value.size}`);
          } else {
            console.debug(`FormData entry: ${key} ->`, value);
          }
        }
      } catch (e) {
        // ignore logging errors
      }

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        credentials: 'include',
        body: form,
      });

      // Handle 401 similar to authenticatedApiCall
      if (response.status === 401) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          const newToken = localStorage.getItem('accessToken');
          const retry = await fetch(this.API_URL, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${newToken}` },
            credentials: 'include',
            body: form,
          });
          return await retry.json();
        } else {
          this.clearTokens();
          throw new Error('Authentication failed');
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Authenticated multipart call error:', error);
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  private async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refreshToken');
    
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
          }
        }
      `;

      const response = await fetch(this.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ query }),
      });

      const result: ApiResponse = await response.json();
      const refreshData = result.data.refreshToken;

      if (refreshData.success && refreshData.tokens) {
        localStorage.setItem('accessToken', refreshData.tokens.accessToken);
        localStorage.setItem('refreshToken', refreshData.tokens.refreshToken);
        return true;
      }

      return false;
    } catch (error) {
      console.error('Refresh token error:', error);
      return false;
    }
  }

  /**
   * Check if token is expired
   */
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

  /**
   * Clear tokens (for logout)
   */
  private clearTokens(): void {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }
}

// Export singleton instance
export const apiClient = ApiClient.getInstance();
