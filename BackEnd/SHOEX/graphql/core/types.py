import graphene
from graphene import relay
from graphene_django import DjangoConnectionField


class FilterInputObjectType(graphene.InputObjectType):
    """Base filter input type"""
    pass


class BaseField(graphene.Field):
    """Base field with default description"""
    pass


class FilterConnectionField(DjangoConnectionField):
    """Connection field with filtering support"""
    pass


class BaseObjectType(graphene.ObjectType):
    """Base object type for SHOEX GraphQL"""
    pass


class BaseInputObjectType(graphene.InputObjectType):
    """Base input object type for SHOEX GraphQL"""
    pass