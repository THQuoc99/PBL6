from collections import defaultdict
from django.db.models import Prefetch
from promise import Promise
from promise.dataloader import DataLoader

from address.models import Province, Ward, Hamlet, Address


class ProvinceByIdLoader(DataLoader):
    """DataLoader để load Province theo ID"""
    
    def batch_load_fn(self, province_ids):
        """Batch load provinces theo list IDs"""
        provinces = Province.objects.filter(
            province_id__in=province_ids
        ).prefetch_related('wards', 'addresses')
        
        # Tạo dict mapping id -> province
        province_map = {
            province.province_id: province 
            for province in provinces
        }
        
        # Trả về theo đúng thứ tự input
        return Promise.resolve([
            province_map.get(province_id) 
            for province_id in province_ids
        ])


class WardByIdLoader(DataLoader):
    """DataLoader để load Ward theo ID"""
    
    def batch_load_fn(self, ward_ids):
        """Batch load wards theo list IDs"""
        wards = Ward.objects.filter(
            ward_id__in=ward_ids
        ).select_related('province').prefetch_related('hamlets', 'addresses')
        
        # Tạo dict mapping id -> ward
        ward_map = {
            ward.ward_id: ward 
            for ward in wards
        }
        
        # Trả về theo đúng thứ tự input
        return Promise.resolve([
            ward_map.get(ward_id) 
            for ward_id in ward_ids
        ])


class HamletByIdLoader(DataLoader):
    """DataLoader để load Hamlet theo ID"""
    
    def batch_load_fn(self, hamlet_ids):
        """Batch load hamlets theo list IDs"""
        hamlets = Hamlet.objects.filter(
            hamlet_id__in=hamlet_ids
        ).select_related('ward__province').prefetch_related('addresses')
        
        # Tạo dict mapping id -> hamlet
        hamlet_map = {
            hamlet.hamlet_id: hamlet 
            for hamlet in hamlets
        }
        
        # Trả về theo đúng thứ tự input
        return Promise.resolve([
            hamlet_map.get(hamlet_id) 
            for hamlet_id in hamlet_ids
        ])


class AddressByIdLoader(DataLoader):
    """DataLoader để load Address theo ID"""
    
    def batch_load_fn(self, address_ids):
        """Batch load addresses theo list IDs"""
        addresses = Address.objects.filter(
            address_id__in=address_ids
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        )
        
        # Tạo dict mapping id -> address
        address_map = {
            address.address_id: address 
            for address in addresses
        }
        
        # Trả về theo đúng thứ tự input
        return Promise.resolve([
            address_map.get(address_id) 
            for address_id in address_ids
        ])


class WardsByProvinceLoader(DataLoader):
    """DataLoader để load Wards theo Province ID"""
    
    def batch_load_fn(self, province_ids):
        """Batch load wards theo list province IDs"""
        wards = Ward.objects.filter(
            province_id__in=province_ids
        ).select_related('province').prefetch_related('hamlets', 'addresses')
        
        # Group wards theo province_id
        wards_by_province = defaultdict(list)
        for ward in wards:
            wards_by_province[ward.province_id].append(ward)
        
        # Trả về list wards cho mỗi province
        return Promise.resolve([
            wards_by_province.get(province_id, []) 
            for province_id in province_ids
        ])


class HamletsByWardLoader(DataLoader):
    """DataLoader để load Hamlets theo Ward ID"""
    
    def batch_load_fn(self, ward_ids):
        """Batch load hamlets theo list ward IDs"""
        hamlets = Hamlet.objects.filter(
            ward_id__in=ward_ids
        ).select_related('ward__province').prefetch_related('addresses')
        
        # Group hamlets theo ward_id
        hamlets_by_ward = defaultdict(list)
        for hamlet in hamlets:
            hamlets_by_ward[hamlet.ward_id].append(hamlet)
        
        # Trả về list hamlets cho mỗi ward
        return Promise.resolve([
            hamlets_by_ward.get(ward_id, []) 
            for ward_id in ward_ids
        ])


class AddressesByUserLoader(DataLoader):
    """DataLoader để load Addresses theo User ID"""
    
    def batch_load_fn(self, user_ids):
        """Batch load addresses theo list user IDs"""
        addresses = Address.objects.filter(
            user_id__in=user_ids
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        ).order_by('-is_default', 'address_id')
        
        # Group addresses theo user_id
        addresses_by_user = defaultdict(list)
        for address in addresses:
            addresses_by_user[address.user_id].append(address)
        
        # Trả về list addresses cho mỗi user
        return Promise.resolve([
            addresses_by_user.get(user_id, []) 
            for user_id in user_ids
        ])


class AddressesByProvinceLoader(DataLoader):
    """DataLoader để load Addresses theo Province ID"""
    
    def batch_load_fn(self, province_ids):
        """Batch load addresses theo list province IDs"""
        addresses = Address.objects.filter(
            province_id__in=province_ids
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        )
        
        # Group addresses theo province_id
        addresses_by_province = defaultdict(list)
        for address in addresses:
            addresses_by_province[address.province_id].append(address)
        
        # Trả về list addresses cho mỗi province
        return Promise.resolve([
            addresses_by_province.get(province_id, []) 
            for province_id in province_ids
        ])


class AddressesByWardLoader(DataLoader):
    """DataLoader để load Addresses theo Ward ID"""
    
    def batch_load_fn(self, ward_ids):
        """Batch load addresses theo list ward IDs"""
        addresses = Address.objects.filter(
            ward_id__in=ward_ids
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        )
        
        # Group addresses theo ward_id
        addresses_by_ward = defaultdict(list)
        for address in addresses:
            addresses_by_ward[address.ward_id].append(address)
        
        # Trả về list addresses cho mỗi ward
        return Promise.resolve([
            addresses_by_ward.get(ward_id, []) 
            for ward_id in ward_ids
        ])


class AddressesByHamletLoader(DataLoader):
    """DataLoader để load Addresses theo Hamlet ID"""
    
    def batch_load_fn(self, hamlet_ids):
        """Batch load addresses theo list hamlet IDs"""
        # Filter None values
        valid_hamlet_ids = [hid for hid in hamlet_ids if hid is not None]
        
        addresses = Address.objects.filter(
            hamlet_id__in=valid_hamlet_ids
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        )
        
        # Group addresses theo hamlet_id
        addresses_by_hamlet = defaultdict(list)
        for address in addresses:
            if address.hamlet_id:
                addresses_by_hamlet[address.hamlet_id].append(address)
        
        # Trả về list addresses cho mỗi hamlet (handle None values)
        return Promise.resolve([
            addresses_by_hamlet.get(hamlet_id, []) if hamlet_id is not None else []
            for hamlet_id in hamlet_ids
        ])


class DefaultAddressByUserLoader(DataLoader):
    """DataLoader để load Default Address theo User ID"""
    
    def batch_load_fn(self, user_ids):
        """Batch load default address theo list user IDs"""
        addresses = Address.objects.filter(
            user_id__in=user_ids,
            is_default=True
        ).select_related(
            'user', 'province', 'ward', 'hamlet', 'ward__province'
        )
        
        # Tạo dict mapping user_id -> default address
        default_address_map = {
            address.user_id: address 
            for address in addresses
        }
        
        # Trả về default address cho mỗi user (có thể None)
        return Promise.resolve([
            default_address_map.get(user_id) 
            for user_id in user_ids
        ])


# Context class để quản lý tất cả dataloaders
class AddressDataLoaders:
    """Class chứa tất cả dataloaders cho address"""
    
    def __init__(self):
        # Single entity loaders
        self.province_by_id = ProvinceByIdLoader()
        self.ward_by_id = WardByIdLoader()
        self.hamlet_by_id = HamletByIdLoader()
        self.address_by_id = AddressByIdLoader()
        
        # Relationship loaders
        self.wards_by_province = WardsByProvinceLoader()
        self.hamlets_by_ward = HamletsByWardLoader()
        self.addresses_by_user = AddressesByUserLoader()
        self.addresses_by_province = AddressesByProvinceLoader()
        self.addresses_by_ward = AddressesByWardLoader()
        self.addresses_by_hamlet = AddressesByHamletLoader()
        self.default_address_by_user = DefaultAddressByUserLoader()
    
    def clear_all(self):
        """Clear cache của tất cả dataloaders"""
        for loader_name in dir(self):
            if not loader_name.startswith('_') and loader_name != 'clear_all':
                loader = getattr(self, loader_name)
                if hasattr(loader, 'clear_all'):
                    loader.clear_all()


# Helper function để lấy dataloaders từ context
def get_address_dataloaders(info):
    """Lấy address dataloaders từ GraphQL context"""
    if not hasattr(info.context, 'address_dataloaders'):
        info.context.address_dataloaders = AddressDataLoaders()
    return info.context.address_dataloaders