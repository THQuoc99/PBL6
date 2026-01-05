from shipments.models import Shipment, ShipmentTracking
s = Shipment.objects.order_by('-created_at').first()
print('LATEST_SHIPMENT:', getattr(s, 'shipment_id', None), 'tracking_code=', getattr(s, 'tracking_code', None))
if not s:
    print('No shipment found')
else:
    qs = ShipmentTracking.objects.filter(shipment=s).order_by('-synced_at')
    print('TRACKING_COUNT_FOR_SHIPMENT =', qs.count())
    for row in qs.values('id','label_id','partner_id','carrier_status','carrier_status_text','event_time','synced_at')[:20]:
        print(row)

# Also global counts
print('TOTAL_TRACKINGS =', ShipmentTracking.objects.count())
print('LATEST_TRACKINGS (global):')
for r in ShipmentTracking.objects.order_by('-synced_at')[:10].values('id','shipment_id','label_id','partner_id','event_time','synced_at'):
    print(r)
