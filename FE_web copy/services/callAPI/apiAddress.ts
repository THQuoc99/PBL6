const GHTK_TOKEN = "2P8zJRNHjCwAoNCRzzUXDJMJgiJZzPnoZfQqZic";

// Local fallback dataset (used when external APIs are unavailable)
import vietnamAddresses from './vietnam_addresses.json';

// Dùng Next.js proxy để bypass CORS
const BASE_URL = "/api/ghtk/address/getAddressLevel4";
const PROVINCES_API = "/api/provinces/v2/p/";


// ================================================
// 1. LẤY DANH SÁCH TỈNH
// ================================================
export async function getProvinces() {
  try {
    console.log('🌍 Fetching provinces from:', PROVINCES_API);
    const resp = await fetch(PROVINCES_API, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      }
    });
    
    if (!resp.ok) {
      console.warn(`⚠️ Provinces API returned ${resp.status}`);
      // If server error (5xx), fall back to local dataset immediately
      if (resp.status >= 500) {
        try {
          if (Array.isArray(vietnamAddresses) && vietnamAddresses.length > 0) {
            console.log('ℹ️ Using local vietnam_addresses.json as provinces fallback (server error)');
            return vietnamAddresses.map((p: any) => ({ code: p.province_code, name: p.province_name }));
          }
        } catch (e) {
          console.warn('⚠️ Unable to load local provinces fallback', e);
        }
      }
      return [];
    }
    
    const data = await resp.json();
    console.log('✅ Provinces loaded:', data.length);
    return data;
  } catch (err) {
    console.error("❌ Error fetching provinces:", err);
    // Fallback: read from local vietnam_addresses.json
    try {
      if (Array.isArray(vietnamAddresses) && vietnamAddresses.length > 0) {
        console.log('ℹ️ Using local vietnam_addresses.json as provinces fallback');
        return vietnamAddresses.map((p: any) => ({ code: p.province_code, name: p.province_name }));
      }
    } catch (e) {
      console.warn('⚠️ Unable to load local provinces fallback', e);
    }
    return [];
  }
}


// ================================================
// 2. LẤY DANH SÁCH PHƯỜNG/XÃ THEO TỈNH
// ================================================
export async function getWards(provinceId: number | string, retries = 2) {
  if (!provinceId) {
    console.log('⚠️ getWards called without provinceId');
    return [];
  }
  
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const url = `${PROVINCES_API}${provinceId}?depth=2`;
      if (attempt > 0) {
        console.log(`🔄 Retry ${attempt}/${retries} - Fetching wards from:`, url);
      } else {
        console.log('🏘️ Fetching wards from:', url);
      }
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
      
      const resp = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json; charset=utf-8'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!resp.ok) {
        console.warn(`⚠️ Wards API returned ${resp.status} for province ${provinceId}`);
        // If server error, try local fallback immediately
        if (resp.status >= 500) {
          try {
            const prov = (vietnamAddresses as any[]).find(p => String(p.province_code) === String(provinceId) || (p.province_name || '').toLowerCase().includes(String(provinceId).toLowerCase()));
            if (prov && Array.isArray(prov.wards)) {
              console.log('ℹ️ Using local vietnam_addresses.json as wards fallback (server error) for', provinceId);
              return prov.wards.map((w: any) => ({ code: w.ward_code ?? w.code ?? '', name: w.ward_name ?? w.name ?? '', hamlets: w.hamlets ?? [] }));
            }
          } catch (e) {
            console.warn('⚠️ Local wards fallback failed', e);
          }
        }
        if (attempt < retries) {
          await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s before retry
          continue;
        }
        // fall through to final fallback below
        return [];
      }
      
      const data = await resp.json();
      console.log('✅ Wards loaded:', data.wards?.length || 0, 'for province', provinceId);
      return data.wards ?? [];
      
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.error(`⏱️ Timeout fetching wards for ${provinceId} (attempt ${attempt + 1})`);
      } else {
        console.error(`❌ Error fetching wards for ${provinceId} (attempt ${attempt + 1}):`, err.message);
      }
      
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s before retry
        continue;
      }
        // After retries, fallback to local file
        try {
          const prov = (vietnamAddresses as any[]).find(p => String(p.province_code) === String(provinceId) || (p.province_name || '').toLowerCase().includes(String(provinceId).toLowerCase()));
          if (prov && Array.isArray(prov.wards)) {
            console.log('ℹ️ Using local vietnam_addresses.json as wards fallback for', provinceId);
            return prov.wards.map((w: any) => ({ code: w.ward_code ?? w.code ?? '', name: w.ward_name ?? w.name ?? '', hamlets: w.hamlets ?? [] }));
          }
        } catch (e) {
          console.warn('⚠️ Local wards fallback failed', e);
        }
        return [];
    }
  }
  
  return [];
}


// ================================================
// 3. LẤY THÔN/KHU ẤP TỪ GHTK
// ================================================
export async function getHamlets(
  provinceName: string,
  wardName: string
) {
  if (!provinceName || !wardName) {
    console.log('⚠️ getHamlets called without province or ward');
    return [];
  }
  console.log(`🏘️ Fetching hamlets for Province: "${provinceName}", Ward: "${wardName}"`);
  try {
    const params = new URLSearchParams({
      province: provinceName,
      district: "",
      ward_street: wardName
    });

    const url = `${BASE_URL}?${params.toString()}`;
    console.log('🏠 Fetching hamlets from GHTK:', url);

    const resp = await fetch(url, {
      headers: { Token: GHTK_TOKEN },
      mode: 'cors'
    });

    if (!resp.ok) {
      console.warn(`⚠️ GHTK API returned ${resp.status} for ${provinceName} - ${wardName}`);
      return [];
    }

    const result = await resp.json();
    console.log('✅ GHTK Response:', result);
    
    // GHTK API format: { success: true/false, data: [...] }
    if (result.success && Array.isArray(result.data)) {
      const hamlets = result.data;
      
      // Nếu chỉ có ["Khác"] thì không có hamlet thực tế
      if (hamlets.length === 1 && hamlets[0] === 'Khác') {
        console.log('⚠️ No real hamlets found (only "Khác")');
        return [];
      }
      
      console.log(`✅ Found ${hamlets.length} hamlets:`, hamlets);
      return hamlets;
    }
    
    console.warn('⚠️ GHTK API returned no data or invalid format');
    return [];
    
  } catch (err) {
    // CORS error or network error - không phải lỗi fatal
    console.warn(`❌ GHTK API unavailable (CORS/Network):`, err);
    // Fallback: try to read from local vietnam_addresses.json
    try {
      const province = (vietnamAddresses as any[]).find(p => (p.province_name || '').toLowerCase().includes((provinceName || '').toLowerCase()) || String(p.province_code) === String(provinceName));
      if (province && Array.isArray(province.wards)) {
        const ward = province.wards.find((w: any) => (w.ward_name || '').toLowerCase().includes((wardName || '').toLowerCase()) || String(w.ward_code) === String(wardName));
        if (ward && Array.isArray(ward.hamlets)) {
          console.log('ℹ️ Using local vietnam_addresses.json hamlets fallback for', provinceName, wardName);
          return ward.hamlets;
        }
      }
    } catch (e) {
      console.warn('⚠️ Local hamlets fallback failed', e);
    }
    return [];
  }
}
