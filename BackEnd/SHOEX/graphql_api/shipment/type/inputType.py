import graphene
from graphene import ObjectType, InputObjectType, List, String, Int, Boolean


    # street đã bỏ
class ExtraFeeType(ObjectType):
    title = String()
    amount = Int()
    type = String()
class ShippingFeeResult(ObjectType):
    totalFee = Int()
    baseFee = Int()
    insuranceFee = Int()
    deliverySupported = Boolean()
    extraFees = List(ExtraFeeType)
    name = String()  # tên gói cước: area1, area2, ...
class ShippingFeeInput(graphene.InputObjectType):
    storeId = graphene.String(required=True)
    weight = graphene.Float(required=True)
    value = graphene.Int()
    transport = graphene.String()
    tags = graphene.List(graphene.String)
