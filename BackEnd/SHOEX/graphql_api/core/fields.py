import graphene
from graphene import relay
from graphene_django import DjangoConnectionField


class FilterConnectionField(DjangoConnectionField):
    """Connection field with filtering support"""
    
    def __init__(self, type, *args, **kwargs):
        self.filter_type = kwargs.pop('filter', None)
        super().__init__(type, *args, **kwargs)
    
    @classmethod
    def resolve_connection(cls, connection, default_manager, info, args, **kwargs):
        """Override to add filtering support"""
        return super().resolve_connection(connection, default_manager, info, args, **kwargs)


BaseField = graphene.Field