"""
Django management command để test GraphQL
"""
from django.core.management.base import BaseCommand
from graphene.test import Client
from graphql.api import schema

class Command(BaseCommand):
    help = 'Test GraphQL API - User module only'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Testing SHOEX GraphQL API - USER MODULE ONLY")
        self.stdout.write("=" * 50)
        
        client = Client(schema)
        
        # Test health check
        self.stdout.write("\n=== Health Check ===")
        health_query = 'query { health }'
        result = client.execute(health_query)
        self.stdout.write(f"Health result: {result}")
        
        # Test register
        self.stdout.write("\n=== Testing Register ===")
        register_mutation = '''
        mutation {
          register(input: {
            fullName: "Test User Via Command"
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
        self.stdout.write(f"Register result: {result}")
        
        # Check role default
        user_role = result.get('data', {}).get('register', {}).get('user', {}).get('role')
        if user_role == 'buyer':
            self.stdout.write(self.style.SUCCESS("✅ Role mặc định là 'buyer' - CORRECT!"))
        else:
            self.stdout.write(self.style.ERROR("❌ Role mặc định KHÔNG phải 'buyer'"))
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("🎉 GraphQL User module tests completed!")