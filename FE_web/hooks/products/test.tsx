import React, { useState } from 'react';
import { useProducts } from './products';
import { useProductDetail } from './productDetail';

export default function TestProductsHooks() {
	// Lấy danh sách sản phẩm nổi bật
	const { products, loading, error } = useProducts({ isHot: true, isNew: true }, undefined, { first: 4 });
	const [selectedId, setSelectedId] = useState<string | null>(null);
	// Lấy chi tiết sản phẩm khi chọn
	const { product: detail, loading: loadingDetail, error: errorDetail } = useProductDetail(selectedId || '');

	return (
		<div style={{ padding: 32 }}>
			<h2>Test useProducts (isHot, isNew, first: 4)</h2>
			{loading && <div>Đang tải danh sách sản phẩm...</div>}
			{error && <div style={{ color: 'red' }}>{error}</div>}
			<ul>
				{products.map((p: any) => (
					<li key={p.productId} style={{ marginBottom: 8 }}>
						<button onClick={() => setSelectedId(p.productId)} style={{ fontWeight: selectedId === p.productId ? 'bold' : 'normal' }}>
							{p.name} (ID: {p.productId})
						</button>
					</li>
				))}
			</ul>

			<hr style={{ margin: '24px 0' }} />
			<h2>Test useProductDetail</h2>
			{selectedId ? (
				loadingDetail ? <div>Đang tải chi tiết sản phẩm...</div>
				: errorDetail ? <div style={{ color: 'red' }}>{errorDetail}</div>
				: detail ? (
					<pre style={{ background: '#f6f6f6', padding: 16, borderRadius: 8 }}>
						{JSON.stringify(detail, null, 2)}
					</pre>
				) : <div>Không có dữ liệu chi tiết.</div>
			) : <div>Chọn một sản phẩm để xem chi tiết.</div>}
		</div>
	);
}
