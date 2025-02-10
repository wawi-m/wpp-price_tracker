// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-KE', {
        style: 'currency',
        currency: 'KES',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price);
}

// Platform logos mapping
const platformLogos = {
    'Jumia': '/static/media/jumia-logo.png',
    'Kilimall': '/static/media/kilimall-logo.png'
};

// Default placeholder image
const placeholderImage = '/static/media/placeholder.png';

// API Functions
async function fetchAPI(endpoint) {
    try {
        if (sessionStorage.getItem(endpoint)) {
            return JSON.parse(sessionStorage.getItem(endpoint));
        }
        const response = await fetch(`/api/v1/${endpoint}`);
        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        sessionStorage.setItem(endpoint, JSON.stringify(data)); // Cache response
        return data;
    } catch (error) {
        console.error(`Error fetching from ${endpoint}:`, error);
        return null;
    }
}

// Load category & platform filters
async function loadFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const platformFilter = document.getElementById('platformFilter');

    try {
        const categories = await fetchAPI('categories');
        if (categories && categoryFilter) {
            categoryFilter.innerHTML = '<option value="">All Categories</option>' + 
                categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }

        const platforms = await fetchAPI('platforms');
        if (platforms && platformFilter) {
            platformFilter.innerHTML = '<option value="">All Platforms</option>' + 
                platforms.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
        }

        console.log('Filters loaded successfully');
    } catch (error) {
        console.error('Error loading filters:', error);
    }
}

// Load products with filters
async function loadProducts(page = 1, append = false, search = '') {
    try {
        const categoryFilter = document.getElementById('categoryFilter');
        const platformFilter = document.getElementById('platformFilter');

        if (!categoryFilter.children.length || !platformFilter.children.length) {
            await loadFilters();
        }

        const categoryId = categoryFilter?.value || '';
        const platformId = platformFilter?.value || '';

        const params = new URLSearchParams({
            page,
            ...(search && { search }),
            ...(categoryId && { category_id: categoryId }),
            ...(platformId && { platform_id: platformId })
        });

        const data = await fetchAPI(`products?${params.toString()}`);
        if (!data) throw new Error('Failed to load products');

        const container = document.getElementById('productsList');
        if (!append) {
            container.innerHTML = '';
        }

        data.items.forEach(product => {
            const col = document.createElement('div');
            col.className = 'col-md-6 col-lg-4 mb-4';

            const imageUrl = product.image_url || placeholderImage;

            col.innerHTML = `
                <div class="card product-card">
                    <div class="card-img-wrapper">
                        <img src="${imageUrl}" 
                             class="card-img-top" 
                             alt="${product.name}"
                             onerror="this.src='${placeholderImage}'">
                    </div>  
                    <div class="card-body">
                        <h5 class="card-title text-truncate" title="${product.name}">${product.name}</h5>
                        <p class="card-text price mb-2">${formatPrice(product.current_price)}</p>
                        <div class="platform-badge ${product.platform.toLowerCase()}-badge">
                            <img src="${platformLogos[product.platform]}" 
                                 alt="${product.platform}" 
                                 class="platform-logo-small"
                                 onerror="this.style.display='none'">
                            ${product.platform}
                        </div>
                        <div class="product-actions mt-3">
                            <button class="btn btn-primary btn-sm" onclick="loadPriceHistory(${product.id})">
                                <i class="fas fa-chart-line"></i> Price History
                            </button>
                            <button class="btn btn-outline-primary btn-sm" onclick="addToCompare(${product.id})">
                                <i class="fas fa-balance-scale"></i> Compare
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });

        const loadMoreBtn = document.getElementById('loadMore');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = data.has_next ? 'block' : 'none';
            loadMoreBtn.onclick = () => loadProducts(page + 1, true);
        }
    } catch (error) {
        console.error('Error loading products:', error);
        if (!append) {
            document.getElementById('productsList').innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        Failed to load products. Please try again later.
                    </div>
                </div>
            `;
        }
    }
}

// Load price history
async function loadPriceHistory(productId) {
    try {
        const product = await fetchAPI(`products/${productId}`);
        if (!product) throw new Error('Failed to load product');

        const chartData = {
            labels: product.price_history.map(ph => new Date(ph.timestamp)),
            datasets: [{
                label: 'Price History',
                data: product.price_history.map(ph => ph.price),
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        };

        if (window.priceHistoryChart) {
            window.priceHistoryChart.destroy();
        }

        const ctx = document.getElementById('priceChart');
        if (!ctx) return;

        window.priceHistoryChart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    }
                }
            }
        });

        // Update product details section
        const detailsContainer = document.getElementById('productDetails');
        if (detailsContainer) {
            const imageUrl = product.image_url || '/static/media/placeholder.png';
            detailsContainer.innerHTML = `
                <div class="text-center mb-3">
                    <img src="${imageUrl}" 
                         alt="${product.name}" 
                         class="img-fluid" 
                         style="max-height: 200px;"
                         onerror="this.src='/static/media/placeholder.png'">
                </div>
                <h6>${product.name}</h6>
                <p class="mb-1">Current Price: ${formatPrice(product.current_price)}</p>
                <p class="mb-1">Platform: ${product.platform}</p>
                <a href="${product.url}" target="_blank" class="btn btn-sm btn-outline-primary">
                    View on ${product.platform}
                </a>
            `;
        }
    } catch (error) {
        console.error('Error loading price history:', error);
    }
}

// Load stats   
async function loadStats() {
    const statElements = {
        totalProducts: document.getElementById('totalProducts'),
        priceDrops: document.getElementById('priceDrops'),
        priceIncreases: document.getElementById('priceIncreases'),
        jumiaProducts: document.getElementById('jumiaProducts'),
        jumiaPrices: document.getElementById('jumiaPrices'),
        kilimallProducts: document.getElementById('kilimallProducts'),
        kilimallPrices: document.getElementById('kilimallPrices')
    };

    try {
        const data = await fetchAPI('stats');
        if (!data) throw new Error('Failed to load stats');

        console.log('Stats Data:', data); // 🔹 Log received stats for debugging

        // Update elements only if they exist
        Object.keys(statElements).forEach(key => {
            if (statElements[key]) {
                if (key.includes('Prices')) {
                    statElements[key].textContent = `${data[key] || '0'} prices tracked`;
                } else {
                    statElements[key].textContent = data[key] || '0';
                }
            }
        });

        console.log('Stats updated successfully');
    } catch (error) {
        console.error('Error loading stats:', error);

        // Reset stats to "0" if an error occurs
        Object.values(statElements).forEach(element => {
            if (element) {
                element.textContent = element.id.includes('Prices') ? '0 prices tracked' : '0';
            }
        });
    }
}
