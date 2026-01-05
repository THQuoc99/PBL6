from .ultis.callAPI_ghtk import calculate_ghtk_fee
import graphene
from .type.inputType import ShippingFeeResult, ExtraFeeType,ShippingFeeInput
from store.models import AddressStore
from address.models import Address
class ShipmentQuery(graphene.ObjectType):
    calculateShippingFee = graphene.Field(
        ShippingFeeResult,
        input=ShippingFeeInput(required=True)
    )

    def resolve_calculateShippingFee(self, info, input):
        user = info.context.user
        print(input)
        if not user or not user.is_authenticated:
            raise Exception("Authentication required")

        pick_address = AddressStore.objects.filter(
            store_id=input.storeId,
            is_default=True
        ).first()

        if not pick_address:
            raise Exception("Store has no default address")

        to_address = Address.objects.filter(
            user=user,
            is_default=True
        ).first()

        if not to_address:
            raise Exception("User has no default address")

        payload = {
            "pick_address_id": str(pick_address.address_id),

            "pick_address": pick_address.detail,
            "pick_province": pick_address.province,
            "pick_district": "",
            "pick_ward": pick_address.ward,
            "pick_street": pick_address.hamlet or "",

            "address": to_address.detail,
            "province": to_address.province,
            "district": "",
            "ward": to_address.ward,
            "street": to_address.hamlet or "",

            "weight": input.weight,
            "value": input.value or 0,
            "transport": input.transport,
            "tags": input.tags,
        }

        try:
            # Debug: log payload sent to GHTK
            print('GHTK fee calculation payload:', payload)
            result = calculate_ghtk_fee(**payload)
        except Exception as e:
            # Raise a clearer error including provider message for easier debugging
            msg = str(e)
            print('GHTK call failed:', msg)
            raise Exception(f"GHTK error when calculating fee: {msg}")

        return ShippingFeeResult(
            name=result["name"],
            totalFee=result["total_fee"],
            baseFee=result["base_fee"],
            insuranceFee=result["insurance_fee"],
            deliverySupported=result["delivery_supported"],
            extraFees=[
                ExtraFeeType(
                    title=ef["title"],
                    amount=ef["amount"],
                    type=ef["type"]
                )
                for ef in result.get("extra_fees", [])
            ]
        )
