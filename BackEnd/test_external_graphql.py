"""
Test GraphQL API - Chạy ngoài Django app để tránh import conflict
"""
import os
import sys
import django

# Add project path
project_path = r"d:\PBL6\BackEnd\SHOEX"
if project_path not in sys.path:
    sys.path.append(project_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import after Django setup
from graphene.test import Client
import sys
import importlib.util

# Import schema from graphql folder
spec = importlib.util.spec_from_file_location("api", r"d:\PBL6\BackEnd\SHOEX\graphql\api.py")
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)
schema = api_module.schema

from users.models import User

def test_graphql_user_api():
    print("🚀 Testing SHOEX GraphQL API - USER MODULE ONLY")
    print("=" * 50)
    
    client = Client(schema)
    
    # Test health check
    print("\n=== Health Check ===")
    health_query = 'query { health }'
    result = client.execute(health_query)
    print(f"Health result: {result}")
    
    # Clear test user if exists
    User.objects.filter(username="cmdtestuser").delete()
    
    # Test register
    print("\n=== Testing Register ===")
    register_mutation = '''
    mutation {
      register(input: {
        fullName: "Test User Via External Script"
        username: "cmdtestuser"
        email: "cmd@test.com"
        password: "testpass123"
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
        errors {
          username
          email
          password
          general
        }
      }
    }
    '''
    result = client.execute(register_mutation)
    print(f"Register result: {result}")
    
    # Check role default
    if 'data' in result and 'register' in result['data']:
        register_data = result['data']['register']
        if register_data.get('user', {}).get('role') == 'buyer':
            print("✅ Role mặc định là 'buyer' - CORRECT!")
        else:
            print("❌ Role mặc định KHÔNG phải 'buyer'")
        
        if register_data.get('success'):
            print("✅ Register thành công!")
        else:
            print("❌ Register thất bại!")
            print(f"Errors: {register_data.get('errors')}")
    
    # Test login
    print("\n=== Testing Login ===")
    login_mutation = '''
    mutation {
      login(input: {
        username: "cmdtestuser"
        password: "testpass123"
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
        token
        errors {
          username
          password
          general
        }
      }
    }
    '''
    result = client.execute(login_mutation)
    print(f"Login result: {result}")
    
    if 'data' in result and 'login' in result['data']:
        login_data = result['data']['login']
        if login_data.get('success') and login_data.get('token'):
            print("✅ Login thành công và có token!")
        else:
            print("❌ Login thất bại!")
            print(f"Errors: {login_data.get('errors')}")
    
    # Test query users
    print("\n=== Testing Query Users ===")
    users_query = '''
    query {
      users {
        id
        username
        email
        fullName
        role
      }
    }
    '''
    result = client.execute(users_query)
    print(f"Users query result: {result}")
    
    print("\n" + "=" * 50)
    print("🎉 GraphQL User module tests completed!")

if __name__ == "__main__":
    test_graphql_user_api()