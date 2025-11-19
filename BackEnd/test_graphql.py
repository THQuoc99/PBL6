"""
GraphQL Test Script - USER MODULE ONLY

Test các mutations và queries cho User authentication
Focus phát triển từng module một
"""

import os
import sys
import django

# Setup Django
sys.path.append('d:/PBL6/BackEnd/SHOEX')  # Thêm path đến SHOEX
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from graphql import build_schema, validate, parse
from graphene.test import Client
from graphql.api import schema

def test_health_check():
    """Test health check query"""
    client = Client(schema)
    
    query = '''
    query {
      health
    }
    '''
    
    result = client.execute(query)
    print("Health check result:", result)
    return result

def test_register_mutation():
    client = Client(schema)
    
    mutation = '''
    mutation {
      register(input: {
        fullName: "Test User Default Role"
        username: "testuser3"
        email: "test3@example.com"
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
          roleDisplay
          isActive
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
    
    result = client.execute(mutation)
    print("Register result:", result)
    
    # Kiểm tra role mặc định là 'buyer'
    if result.get('data', {}).get('register', {}).get('user', {}).get('role') == 'buyer':
        print("✅ Role mặc định là 'buyer' - CORRECT!")
    else:
        print("❌ Role mặc định KHÔNG phải 'buyer' - ERROR!")
    
    return result

def test_login_mutation():
    client = Client(schema)
    
    mutation = '''
    mutation {
      login(input: {
        username: "testuser3"
        password: "testpass123"
        rememberMe: false
      }) {
        success
        message
        user {
          id
          username
          email
          fullName
          role
          roleDisplay
          displayName
          initials
        }
        tokens {
          accessToken
          refreshToken
          expiresIn
        }
        errors {
          username
          password
          general
        }
      }
    }
    '''
    
    result = client.execute(mutation)
    print("Login result:", result)
    return result

def test_users_query():
    """Test query all users"""
    client = Client(schema)
    
    query = '''
    query {
      users {
        id
        username
        email
        fullName
        role
        roleDisplay
        isActive
        dateJoined
      }
    }
    '''
    
    result = client.execute(query)
    print("Users query result:", result)
    return result

if __name__ == "__main__":
    print("🚀 Testing SHOEX GraphQL API - USER MODULE ONLY")
    print("=" * 50)
    
    print("\n=== Health Check ===")
    test_health_check()
    
    print("\n=== Testing Register ===")
    test_register_mutation()
    
    print("\n=== Testing Login ===")
    test_login_mutation()
    
    print("\n=== Testing Users Query ===") 
    test_users_query()
    
    print("\n" + "=" * 50)
    print("🎉 All User module tests completed!")
    print("Ready for development and testing user authentication features.")