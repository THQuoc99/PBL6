# Admin Analytics Integration - Testing Guide

## Backend Setup

### 1. Query đã tạo
- File: `graphql_api/store/queries/admin_analytics.py`
- Query name: `adminAnalytics`
- Parameters:
  - `range`: String ('7d', '30d', '90d', '1y') - default: '30d'
  - `limit`: Int (số lượng data points) - default: 12

### 2. Data trả về
```graphql
{
  revenueTrend {
    month        # T1, T2, ..., T12
    revenue      # Decimal
    orders       # Int
    growth       # Float (%)
  }
  categoryPerformance {
    name         # Tên danh mục
    sales        # Decimal
    orders       # Int
  }
  regionalDistribution {
    region       # Tên thành phố
    value        # Float (%)
  }
  userGrowth {
    month        # T1, T2, ..., T12
    customers    # Int (số khách hàng mới)
    sellers      # Int (số người bán mới)
  }
}
```

### 3. Test Backend Query

#### Option 1: GraphQL Playground
1. Mở: http://127.0.0.1:8000/graphql/
2. Login để lấy token
3. Add header: `Authorization: Bearer <your-token>`
4. Chạy query từ file `test_admin_analytics.graphql`

#### Option 2: Python test
```python
python manage.py shell

from graphql_api.store.queries.admin_analytics import AdminAnalyticsQuery
from graphene.test import Client
from graphql_api.api import schema

# Test query
query = '''
  query {
    adminAnalytics(range: "30d") {
      revenueTrend { month revenue orders }
      categoryPerformance { name sales orders }
    }
  }
'''
client = Client(schema)
result = client.execute(query)
print(result)
```

## Frontend Setup

### 1. Service đã update
- File: `services/dasgboardAdmin/analytics.ts`
- Gọi API qua `apiClient.authenticatedApiCall()`
- Fallback: REST API → Mock data

### 2. Hook
- File: `hooks/dasgboardAdmin/useAnalytics.ts`
- Return: `{ data, loading, error, refetch }`

### 3. Component
- File: `components/pages/admin/AdminAnalyticsPage.tsx`
- Đã wire với `useAdminAnalytics` hook
- Hiển thị loading/error states
- Charts tự động update khi data thay đổi

### 4. Test Frontend

#### Development mode
```bash
cd "d:\PBL6\FE_web copy"
npm run dev
```

#### Test flow
1. Login với admin account
2. Navigate to: Admin → Phân tích
3. Check browser console for API calls
4. Verify charts render with real data

## Debugging

### Backend issues
```bash
# Check Django logs
cd "d:\PBL6\BackEnd"
python manage.py runserver

# Check for errors in console
```

### Frontend issues
```bash
# Open browser DevTools
# Check Network tab for GraphQL requests
# Check Console for errors
```

### Common issues

1. **Token expired**
   - Symptom: 401 Unauthorized
   - Fix: Re-login to get new token

2. **No data returned**
   - Check: Database có orders/products không?
   - Fallback: Service sẽ trả mock data

3. **GraphQL errors**
   - Check: Backend logs
   - Verify: Query syntax trong network tab

## Data Flow

```
User selects timeRange
    ↓
useAdminAnalytics({ range: timeRange })
    ↓
fetchAdminAnalytics(params)
    ↓
apiClient.authenticatedApiCall(query, variables)
    ↓
Backend: AdminAnalyticsQuery.resolve_admin_analytics()
    ↓
Query Orders, Products, Users from DB
    ↓
Calculate metrics & aggregate data
    ↓
Return JSON response
    ↓
Frontend: Update charts with real data
```

## Next Steps

1. ✅ Backend query created
2. ✅ Frontend service updated
3. ✅ Frontend component wired
4. ⏳ Test with real Django server
5. ⏳ Verify charts display correctly
6. ⏳ Test different time ranges
