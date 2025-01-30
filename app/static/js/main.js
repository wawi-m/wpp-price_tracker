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
        currency: 'KES'
    }).format(price);
}

// API Functions
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`/blueprint/api/v1/${endpoint}`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

// Home Page Functions
async function loadCategories() {
    const categories = await fetchAPI('categories');
    if (!categories) return;

    const select = document.getElementById('categoryFilter');
    if (select) {
        select.innerHTML = '<option value="">All Categories</option>';
        categories.items.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            select.appendChild(option);
        });
    }
}

async function loadPlatforms() {
    const platforms = await fetchAPI('platforms');
    if (!platforms) return;

    const select = document.getElementById('platformFilter');
    if (select) {
        select.innerHTML = '<option value="">All Platforms</option>';
        platforms.items.forEach(platform => {
            const option = document.createElement('option');
            option.value = platform.id;
            option.textContent = platform.name;
            select.appendChild(option);
        });
    }
}

async function loadProducts(page = 1) {
    const searchQuery = document.getElementById('searchQuery')?.value || '';
    const categoryId = document.getElementById('categoryFilter')?.value || '';
    const platformId = document.getElementById('platformFilter')?.value || '';

    const params = new URLSearchParams({
        page,
        ...(searchQuery && { search: searchQuery }),
        ...(categoryId && { category_id: categoryId }),
        ...(platformId && { platform_id: platformId })
    });

    const products = await fetchAPI(`products?${params}`);
    if (!products) return;

    const container = document.getElementById('productsList');
    if (!container) return;

    if (page === 1) container.innerHTML = '';

    products.items.forEach(product => {
        const card = createProductCard(product);
        container.appendChild(card);
    });

    const loadMoreBtn = document.getElementById('loadMore');
    if (loadMoreBtn) {
        loadMoreBtn.style.display = products.has_next ? 'block' : 'none';
    }
}

function createProductCard(product) {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-4';
    col.innerHTML = `
        <div class="card product-card">
            <img src="${product.image_url}" class="card-img-top" alt="${product.name}">
            <div class="card-body">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text price">${formatPrice(product.current_price)}</p>
                <p class="card-text platform">${product.platform}</p>
                <div class="d-flex justify-content-between">
                    <a href="/price-history" class="btn btn-primary" data-product-id="${product.id}">Price History</a>
                    <a href="${product.url}" target="_blank" class="btn btn-outline-primary">View Product</a>
                </div>
            </div>
        </div>
    `;
    return col;
}

// Comparison Page Functions
async function loadProductsForComparison() {
    const products = await fetchAPI('products');
    if (!products) return;

    const product1Select = document.getElementById('product1');
    const product2Select = document.getElementById('product2');

    if (product1Select && product2Select) {
        const options = products.items.map(product => `
            <option value="${product.id}">${product.name} - ${formatPrice(product.current_price)}</option>
        `).join('');

        product1Select.innerHTML = '<option value="">Select a product...</option>' + options;
        product2Select.innerHTML = '<option value="">Select a product...</option>' + options;
    }
}

async function updateComparison() {
    const product1Id = document.getElementById('product1')?.value;
    const product2Id = document.getElementById('product2')?.value;

    if (!product1Id || !product2Id) return;

    const [product1, product2] = await Promise.all([
        fetchAPI(`products/${product1Id}`),
        fetchAPI(`products/${product2Id}`)
    ]);

    if (product1 && product2) {
        updateProductDetails('product1Details', product1);
        updateProductDetails('product2Details', product2);
        renderComparisonChart(product1, product2);
    }
}

function updateProductDetails(containerId, product) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
        <div class="card">
            <img src="${product.image_url}" class="card-img-top" alt="${product.name}">
            <div class="card-body">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text">Current Price: ${formatPrice(product.current_price)}</p>
                <p class="card-text">Platform: ${product.platform}</p>
                <a href="${product.url}" target="_blank" class="btn btn-primary">View Product</a>
            </div>
        </div>
    `;
}

function renderComparisonChart(product1, product2) {
    const chartContainer = document.getElementById('comparisonChart');
    if (!chartContainer) return;

    const ctx = chartContainer.getContext('2d');
    if (window.priceComparisonChart) {
        window.priceComparisonChart.destroy();
    }

    const datasets = [
        {
            label: product1.name,
            data: product1.price_history.map(ph => ({
                x: new Date(ph.date),
                y: ph.price
            })),
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        },
        {
            label: product2.name,
            data: product2.price_history.map(ph => ({
                x: new Date(ph.date),
                y: ph.price
            })),
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1
        }
    ];

    window.priceComparisonChart = new Chart(ctx, {
        type: 'line',
        data: { datasets },
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
}

// Price History Page Functions
async function loadProductsForHistory() {
    const products = await fetchAPI('products');
    if (!products) return;

    const select = document.getElementById('productSelect');
    if (select) {
        select.innerHTML = '<option value="">Select a product...</option>';
        products.items.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = `${product.name} - ${formatPrice(product.current_price)}`;
            select.appendChild(option);
        });
    }
}

async function updatePriceHistory() {
    const productId = document.getElementById('productSelect')?.value;
    if (!productId) return;

    const product = await fetchAPI(`products/${productId}`);
    if (product) {
        updatePriceStats(product);
        renderPriceHistoryChart(product);
    }
}

function updatePriceStats(product) {
    document.getElementById('currentPrice').textContent = formatPrice(product.current_price);
    
    const prices = product.price_history.map(ph => ph.price);
    document.getElementById('lowestPrice').textContent = formatPrice(Math.min(...prices));
    document.getElementById('highestPrice').textContent = formatPrice(Math.max(...prices));
    document.getElementById('averagePrice').textContent = formatPrice(
        prices.reduce((a, b) => a + b, 0) / prices.length
    );
}

function renderPriceHistoryChart(product) {
    const chartContainer = document.getElementById('priceHistoryChart');
    if (!chartContainer) return;

    const ctx = chartContainer.getContext('2d');
    if (window.priceHistoryChart) {
        window.priceHistoryChart.destroy();
    }

    const data = {
        labels: product.price_history.map(ph => new Date(ph.date)),
        datasets: [{
            label: 'Price History',
            data: product.price_history.map(ph => ph.price),
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    };

    window.priceHistoryChart = new Chart(ctx, {
        type: 'line',
        data: data,
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
}

// Initialize page-specific functions
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;

    if (path === '/') {
        loadCategories();
        loadPlatforms();
        loadProducts();

        // Set up event listeners
        document.getElementById('searchQuery')?.addEventListener('input', 
            debounce(() => loadProducts(1), 500)
        );
        document.getElementById('categoryFilter')?.addEventListener('change', 
            () => loadProducts(1)
        );
        document.getElementById('platformFilter')?.addEventListener('change', 
            () => loadProducts(1)
        );
        document.getElementById('loadMore')?.addEventListener('click', 
            () => loadProducts(document.querySelectorAll('.product-card').length / 12 + 1)
        );
    }
    else if (path === '/compare') {
        loadProductsForComparison();
    }
    else if (path === '/price-history') {
        loadProductsForHistory();
        document.getElementById('productSelect')?.addEventListener('change', updatePriceHistory);
    }
});
