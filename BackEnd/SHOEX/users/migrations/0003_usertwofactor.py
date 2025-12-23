"""Empty migration placeholder after removing UserTwoFactor model.

This migration intentionally has no operations to keep migration numbering stable.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_alter_user_phone'),
    ]

    operations = []
