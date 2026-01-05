import { useState, useEffect, useCallback } from 'react';
import { fetchReportTemplates, generateReport } from '../../services/dashboardAdmin/reports';

export function useAdminReports(){
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<any>(null);

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    try{
      const res = await fetchReportTemplates();
      setTemplates(res);
      setError(null);
    }catch(err){ setError(err); }
    finally{ setLoading(false); }
  }, []);

  useEffect(()=>{ fetchTemplates(); }, [fetchTemplates]);

  const exportReport = async (templateId: string, params = {}) => {
    return await generateReport(templateId, params);
  };

  return { templates, loading, error, refetch: fetchTemplates, exportReport };
}
