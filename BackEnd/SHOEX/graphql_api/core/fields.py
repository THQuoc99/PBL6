import graphene
from graphene import relay
from graphene_django import DjangoConnectionField


class FilterConnectionField(DjangoConnectionField):
    """Connection field with filtering support"""
    
    def __init__(self, type_, *args, **kwargs):
        # Extract filter argument before calling super
        self.filter_type = kwargs.pop('filter', None)
        super().__init__(type_, *args, **kwargs)
    
    def get_resolver(self, parent_resolver):
        """Get the resolver for this connection field"""
        resolver = super().get_resolver(parent_resolver)
        
        def custom_resolver(root, info, **args):
            # Call the original resolver which should return a queryset
            return resolver(root, info, **args)
        
        return custom_resolver


BaseField = graphene.Field