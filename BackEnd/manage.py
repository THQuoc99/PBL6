import os
import sys

# Thêm đường dẫn tới project Django
sys.path.append(r"D:\Mobile\App_futter\test\PBL6\BackEnd\SHOEX")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SHOEX.config.settings")

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
