import requests
from django.conf import settings


def calculate_ghtk_fee(
    *,
    pick_address_id,
    pick_address,
    pick_province,
    pick_district="",
    pick_ward=None,
    pick_street=None,
    address,
    province,
    district="",
    ward=None,
    street=None,
    weight,
    value=0,
    transport=None,
    tags=None,
):
    """
    Gọi API tính phí GHTK
    """

    url = f"{settings.GHTK_BASE_URL}/services/shipment/fee"

    headers = {
        "Token": settings.GHTK_API_TOKEN,
        "X-Client-Source": settings.GHTK_PARTNER_CODE,
    }

    params = {
        "pick_address_id": pick_address_id,
        "pick_address": pick_address,
        "pick_province": pick_province,
        "pick_district": pick_district or "",
        "pick_ward": pick_ward or "",
        "pick_street": pick_street or "",

        "address": address,
        "province": province,
        "district": district or "",
        "ward": ward or "",
        "street": street or "",

        "weight": weight,
        "value": value,
    }

    if transport:
        params["transport"] = transport

    if tags:
        params["tags"] = tags

    response = requests.get(url, headers=headers, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"GHTK HTTP error {response.status_code}")

    data = response.json()

    if not data.get("success"):
        raise Exception(f"GHTK error: {data.get('message')}")

    fee = data["fee"]

    # ===============================
    # Normalize response cho GraphQL
    # ===============================
    base_fee = fee.get("fee", 0)
    insurance_fee = fee.get("insurance_fee", 0)

    extra_fees = []
    for ef in fee.get("extFees", []):
        extra_fees.append({
            "title": ef.get("title"),
            "amount": ef.get("amount", 0),
            "type": ef.get("type"),
        })

    total_fee = base_fee + insurance_fee + sum(
        ef["amount"] for ef in extra_fees
    )
    print(fee.get("delivery"))
    return {
        "name": fee.get("name"),
        "base_fee": base_fee,
        "insurance_fee": insurance_fee,
        "extra_fees": extra_fees,
        "total_fee": total_fee,
        "delivery_supported": fee.get("delivery") is True,
    }
