# shipping/constants.py

GHTK_STATUS_TO_SHIPMENT = {
    # ====== HỦY ======
    -1: 'cancelled',      # Hủy đơn hàng

    # ====== CHỜ XÁC NHẬN / CHƯA CHẠY ======
    1: 'pending',         # Chưa tiếp nhận
    2: 'pending',         # Đã tiếp nhận
    8: 'pending',         # Hoãn lấy hàng
    12: 'pending',        # Đang lấy hàng
    128: 'pending',       # Shipper báo delay lấy hàng

    # ====== VẬN CHUYỂN ======
    3: 'shipping',        # Đã lấy hàng / đã nhập kho
    10: 'shipping',       # Delay giao hàng
    123: 'shipping',      # Shipper báo đã lấy hàng

    # ====== ĐANG GIAO ======
    4: 'out_for_delivery',  # Đang giao hàng
    45: 'out_for_delivery', # Shipper báo đã giao hàng (chưa đối soát)
    410: 'out_for_delivery',# Shipper báo delay giao hàng

    # ====== HOÀN THÀNH ======
    5: 'completed',       # Đã giao hàng / chưa đối soát
    6: 'completed',       # Đã đối soát

    # ====== TRẢ HÀNG / HOÀN TIỀN ======
    7: 'returned',        # Không lấy được hàng
    9: 'returned',        # Không giao được hàng
    11: 'returned',       # Đối soát công nợ trả hàng
    13: 'returned',       # Đơn hàng bồi hoàn
    20: 'returned',       # Đang trả hàng
    21: 'returned',       # Đã trả hàng
    127: 'returned',      # Shipper báo không lấy được hàng
    49: 'returned',       # Shipper báo không giao được
}
