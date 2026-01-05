import { apiClient } from '../callAPI/apiClient';

export async function createOrder(input: any) {
  const mutation = `mutation CreateOrder($input: CreateOrderInput!) {
    createOrder(input: $input) {
      success
      message
      orderId
    }
  }`;

  const variables = { input };
  const res = await apiClient.authenticatedApiCall(mutation, variables);
  return res;
}

export async function fetchMyOrders() {
  const query = `query MyOrders {
    myOrders {
      orderId
      totalAmount
      shippingFee
      createdAt
      updatedAt

      address {
        detail
        province
        ward
        hamlet
        fullAddress
        phoneNumber
      }

      payment {
        paymentId
        paymentMethod
        status
        amount
        transactionId
        paidAt
        gatewayResponse
      }

      subOrders {
        subOrderId
        subtotal
        shippingFee
        createdAt

        store {
          storeId
          name
          avatar
        }

        shipment{
          shipmentId
          trackingCode
          status
          pickMoney
          value
          totalWeight
          transport
          createdAt
          updatedAt

          trackings {
            id
            labelId
            partnerId
            carrierStatus
            carrierStatusText
            message
            eventTime
            syncedAt
            weight
            estimatedPickTime
            estimatedDeliverTime
          }
        }

        items {
          itemId
          quantity
          priceAtOrder
          variant {
            id
            sku
            price
            stock
            colorImageUrl
            colorName
            sizeName
            product {
              productId
              name
            }
          }
        }
      }
    }
  }`;

  const res = await apiClient.authenticatedApiCall(query);
  return res;
}

export async function fetchOrdersByUser(userId: string) {
  const query = `query OrdersByUser($userId: ID!) {
    ordersByUser(userId: $userId) {
      orderId
      totalAmount
      shippingFee
      createdAt
      updatedAt

      address { detail province ward hamlet fullAddress phoneNumber }

      payment { paymentId paymentMethod status amount transactionId paidAt gatewayResponse }

      subOrders {
        subOrderId subtotal shippingFee createdAt
        store { storeId name avatar }
        shipment{ shipmentId trackingCode status pickMoney value totalWeight transport createdAt updatedAt trackings { id labelId partnerId carrierStatus carrierStatusText message eventTime syncedAt weight estimatedPickTime estimatedDeliverTime } }
        items { itemId quantity priceAtOrder variant { id sku price stock colorImageUrl colorName sizeName product { id name } } }
      }
    }
  }`;

  const variables = { userId };
  const res = await apiClient.authenticatedApiCall(query, variables);
  return res;
}

export async function fetchSubOrdersByStore(storeId: string, isPayment?: boolean) {
  const query = `query GetSubOrdersByStore($storeId: ID!, $isPayment: Boolean) {
    subOrdersByStore(storeId: $storeId, isPayment: $isPayment) {
      subOrderId
      shippingFee
      subtotal
      createdAt
      updatedAt

      store {
        storeId
        name
        slug
        email
        address
      }

      order {
        orderId
        totalAmount
        shippingFee
        createdAt
        updatedAt
        buyer {
          id
          email
          username
        }
        payment {
          paymentId
          paymentMethod
          amount
          status
          transactionId
          gatewayResponse
          paidAt
          createdAt
          updatedAt
        }
      }

      items {
        itemId
        quantity
        priceAtOrder
        variant {
          variantId
          sku
          price
          stock
          optionCombinations
          isInStock
          colorName
          sizeName
          colorImageUrl
          product {
            productId
            name
            slug
            basePrice
            galleryImages {
              imageUrl
            }
          }
        }
      }

      shipment {
        shipmentId
        trackingCode
        pickDate
        pickMoney
        note
        value
        transport
        status
        totalWeight
        createdAt
        updatedAt

        relatedParties
        trackings {
          id
          labelId
          partnerId
          carrierStatus
          carrierStatusText
          message
          eventTime
          syncedAt
          weight
          estimatedPickTime
          estimatedDeliverTime
          rawResponse
        }
      }
    }
  }`;

  const variables: any = { storeId };
  if (typeof isPayment !== 'undefined') {
    variables.isPayment = isPayment;
  }
  const res = await apiClient.authenticatedApiCall(query, variables);
  return res;
}

export async function cancelOrderService(orderId: string | number) {
  const mutation = `mutation CancelOrder($orderId: ID!) {
    cancelOrder(orderId: $orderId) {
      success
      message
    }
  }`;

  const variables = { orderId: String(orderId) };
  const res = await apiClient.authenticatedApiCall(mutation, variables);
  return res;
}

export async function cancelSubOrderService(subOrderId: string | number) {
  const mutation = `mutation CancelSubOrder($subOrderId: ID!) {
    cancelSubOrder(subOrderId: $subOrderId) {
      success
      message
    }
  }`;

  const variables = { subOrderId: String(subOrderId) };
  const res = await apiClient.authenticatedApiCall(mutation, variables);
  return res;
}

export async function confirmSubOrderShipmentService(subOrderId: string | number) {
  const mutation = `mutation ConfirmSubOrderShipment($id: ID!) {
    confirmSuborderShipment(subOrderId: $id) {
      success
      message
      result
    }
  }`;

  const variables = { id: String(subOrderId) };
  const res = await apiClient.authenticatedApiCall(mutation, variables);
  // Normalize response shape: prefer camelCase field, then snake_case, then raw
  const payload = res?.data?.confirmSuborderShipment ?? res?.data?.confirm_suborder_shipment ?? res;
  return payload;
}
