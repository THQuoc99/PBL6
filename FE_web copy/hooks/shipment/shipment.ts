import { useEffect, useState } from "react";
import { calculateShippingFee, ShippingFeeInput, ShippingFeeResult } from "../../services/shipment/shipment";

export function useCalculateShippingFee(input: ShippingFeeInput | null) {
  const [data, setData] = useState<ShippingFeeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!input) {
      setData(null);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    calculateShippingFee(input)
      .then((res) => setData(res))
      .catch((err) => setError(err.message || "Error"))
      .finally(() => setLoading(false));
  }, [JSON.stringify(input)]);

  return { data, loading, error };
}

