#!/usr/bin/env python
"""
Script để generate GraphQL Schema Definition Language (SDL) file
Chạy: python manage.py export_schema
"""

import os
import django
from django.core.management.base import BaseCommand
from graphql import build_schema, print_schema

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from graphql_api.api import schema

class Command(BaseCommand):
    help = 'Export GraphQL schema to SDL file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output', 
            type=str, 
            default='schema.graphql',
            help='Output file path'
        )
    
    def handle(self, *args, **options):
        output_file = options['output']
        
        # Get schema SDL
        sdl = print_schema(schema.graphql_schema)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(sdl)
        
        self.stdout.write(
            self.style.SUCCESS(f'Schema exported to {output_file}')
        )