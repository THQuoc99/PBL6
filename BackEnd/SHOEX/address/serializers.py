from rest_framework import serializers
from .models import Province, Ward, Hamlet, Address

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['province_id', 'name']

class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = ['ward_id', 'name', 'province']
        
class HamletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hamlet
        fields = ['hamlet_id', 'name', 'ward']

class AddressSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    ward_name = serializers.CharField(source='ward.name', read_only=True)
    hamlet_name = serializers.CharField(source='hamlet.name', read_only=True, allow_null=True)
    
    # ⚠️ ĐÃ XÓA dòng name=... và phone=... để dùng field thực của model

    class Meta:
        model = Address
        fields = ['address_id', 'user', 'name', 'phone', 'detail', 'province', 'ward', 'hamlet', 
                  'province_name', 'ward_name', 'hamlet_name', 'is_default']
        read_only_fields = ['user'] # Chỉ user là read_only, name và phone được phép ghi