/** Reports service for admin */
export async function fetchReportTemplates(){
  try{
    const res = await fetch(`/api/admin/reports/templates`);
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }catch(err){
    return [
      { id: 'revenue', name: 'Báo cáo doanh thu (CSV)' },
      { id: 'orders', name: 'Báo cáo đơn hàng (CSV)' }
    ];
  }
}

export async function generateReport(templateId: string, params: Record<string, any> = {}){
  try{
    const res = await fetch(`/api/admin/reports/generate/${templateId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.blob();
  }catch(err){
    // return a fake blob (empty)
    return new Blob([], { type: 'text/csv' });
  }
}
