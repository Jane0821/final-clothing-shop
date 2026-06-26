document.addEventListener('DOMContentLoaded', function () {
    const filterForm = document.querySelector('form');
    const btnSubmit = document.getElementById('btnSubmit') || document.querySelector('button[type="submit"]');
    const loadingStatus = document.getElementById('loadingStatus');
    const resultGrid = document.getElementById('resultGrid');
    const emptyMessage = document.getElementById('emptyMessage');

    if (!filterForm) return;

    filterForm.addEventListener('submit', function (e) {
        e.preventDefault();

        if (loadingStatus) loadingStatus.classList.remove('d-none');
        if (resultGrid) resultGrid.innerHTML = '';
        if (emptyMessage) emptyMessage.classList.add('d-none');
        if (btnSubmit) btnSubmit.disabled = true;

        const formData = new FormData(filterForm);
        const payload = {
            gender: formData.get('gender'),
            brand: formData.get('brand'),
            type: formData.get('type'),
            min_price: formData.get('min_price'),
            max_price: formData.get('max_price'),
            keyword: formData.get('keyword'),
            sort_by: formData.get('sort_by')
        };

        fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(res => {
            if (loadingStatus) loadingStatus.classList.add('d-none');
            if (btnSubmit) btnSubmit.disabled = false;

            if (res.success && res.count > 0) {
                res.data.forEach(item => {
                    // 【設計美化】判斷是不是店長推薦，如果是，加上精緻的金色耀眼邊框與專屬 Badge
                    const cardStyle = item.is_fallback 
                        ? 'border: 2px solid #ffc107!important; background-color: #fffdf5;' 
                        : 'border: none;';
                    
                    const badgeHtml = item.is_fallback 
                        ? `<span class="badge bg-warning text-dark fw-bold animate__animated animate__pulse animate__infinite"><i class="fa-solid fa-crown me-1"></i>店長推薦</span>`
                        : `<span class="badge bg-secondary font-monospace">NO. ${item.item_code}</span>`;

                    const officialLinkHtml = item.official_url
                        ? `<a href="${item.official_url}" target="_blank" rel="noopener" class="btn btn-sm btn-outline-primary mt-3 w-100" onclick="event.stopPropagation()">品牌官網</a>`
                        : '';

                    const cardOnclick = item.official_url
                        ? `onclick="window.open('${item.official_url}', '_blank', 'noopener')"` 
                        : '';

                    const cardHtml = `
                        <div class="col animate__animated animate__fadeInUp">
                            <div class="card h-100 shadow-sm overflow-hidden" style="${cardStyle} cursor: ${item.official_url ? 'pointer' : 'default'};" ${cardOnclick}>
                                <div class="position-relative bg-light text-center" style="height: 220px; overflow: hidden;">
                                    <img src="${item.image_url}" class="w-100 h-100 object-fit-cover" alt="商品圖片" onerror="this.src='https://via.placeholder.com/320x320.png?text=Clothing'">
                                </div>
                                
                                <div class="bg-dark text-white px-3 py-2 d-flex justify-content-between align-items-center">
                                    ${badgeHtml}
                                    <small class="text-info fw-bold">${item.brand}</small>
                                </div>
                                
                                <div class="card-body d-flex flex-column p-4">
                                    <h5 class="card-title fw-bold text-dark mb-3">${item.title}</h5>
                                    ${officialLinkHtml}
                                    <div class="mt-auto pt-3 border-top border-light">
                                        <div class="d-flex justify-content-between align-items-center">
                                            <div class="text-danger fw-bold h4 mb-0">
                                                <small class="fs-6">NT$</small> ${item.price.toLocaleString()}
                                            </div>
                                            <div class="text-warning d-flex align-items-center bg-white px-2 py-1 rounded shadow-sm border">
                                                <i class="fa-solid fa-star me-1"></i>
                                                <span class="text-dark fw-bold">${item.rating.toFixed(1)}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    if (resultGrid) resultGrid.insertAdjacentHTML('beforeend', cardHtml);
                });
            } else {
                if (emptyMessage) {
                    emptyMessage.classList.remove('d-none');
                    emptyMessage.innerHTML = `
                        <i class="fa-solid fa-magnifying-glass-minus fa-2x mb-2 text-muted"></i>
                        <p class="mb-0">庫存中找不到喔！請放寬條件再試試看！</p>
                    `;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (loadingStatus) loadingStatus.classList.add('d-none');
            if (btnSubmit) btnSubmit.disabled = false;
        });
    });
});
