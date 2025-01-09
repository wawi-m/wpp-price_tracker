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
        const response = await fetch(`/api/v1/${endpoint}`);
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
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });
}

async function loadPlatforms() {
    const platforms = await fetchAPI('platforms');
    if (!platforms) return;

    const select = document.getElementById('platformFilter');
    platforms.forEach(platform => {
        const option = document.createElement('option');
        option.value = platform.id;
        option.textContent = platform.name;
        select.appendChild(option);
    });
}

async function loadProducts(page = 1) {
    const searchQuery = document.getElementById('searchQuery').value;
    const categoryId = document.getElementById('categoryFilter').value;
    const platformId = document.getElementById('platformFilter').value;

    const params = new URLSearchParams({
        page,
        search: searchQuery,
        category_id: categoryId,
        platform_id: platformId
    });

    const products = await fetchAPI(`products?${params}`);
    if (!products) return;

    const container = document.getElementById('productsList');
    if (page === 1) container.innerHTML = '';

    products.items.forEach(product => {
        const card = createProductCard(product);
        container.appendChild(card);
    });

    document.getElementById('loadMore').style.display = 
        products.has_next ? 'block' : 'none';
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
                <p class="card-text platform">${product.platform_name}</p>
                <div class="d-flex justify-content-between">
                    <a href="/price-history/${product.id}" class="btn btn-primary">Price History</a>
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

    const selects = ['product1', 'product2'];
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        products.items.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = `${product.name} (${product.platform_name})`;
            select.appendChild(option);
        });
    });
}

async function updateComparison() {
    const product1Id = document.getElementById('product1').value;
    const product2Id = document.getElementById('product2').value;

    if (!product1Id || !product2Id) return;

    const [product1Data, product2Data] = await Promise.all([
        fetchAPI(`products/${product1Id}`),
        fetchAPI(`products/${product2Id}`)
    ]);

    if (!product1Data || !product2Data) return;

    updateProductDetails('product1Details', product1Data);
    updateProductDetails('product2Details', product2Data);
    renderComparisonChart(product1Data, product2Data);
}

function updateProductDetails(containerId, product) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="card">
            <img src="${product.image_url}" class="card-img-top" alt="${product.name}">
            <div class="card-body">
                <h5 class="card-title">${product.name}</h5>
                <p class="card-text price">${formatPrice(product.current_price)}</p>
                <p class="card-text platform">${product.platform_name}</p>
                <a href="${product.url}" target="_blank" class="btn btn-primary">View Product</a>
            </div>
        </div>
    `;
}

function renderComparisonChart(product1, product2) {
    const trace1 = {
        x: product1.price_history.map(p => p.timestamp),
        y: product1.price_history.map(p => p.price),
        name: product1.name,
        type: 'scatter'
    };

    const trace2 = {
        x: product2.price_history.map(p => p.timestamp),
        y: product2.price_history.map(p => p.price),
        name: product2.name,
        type: 'scatter'
    };

    const layout = {
        title: 'Price Comparison',
        xaxis: { title: 'Date' },
        yaxis: { title: 'Price (KES)' }
    };

    Plotly.newPlot('comparisonChart', [trace1, trace2], layout);
}

// Price History Page Functions
async function loadProductsForHistory() {
    const products = await fetchAPI('products');
    if (!products) return;

    const select = document.getElementById('productSelect');
    products.items.forEach(product => {
        const option = document.createElement('option');
        option.value = product.id;
        option.textContent = `${product.name} (${product.platform_name})`;
        select.appendChild(option);
    });
}

async function updatePriceHistory() {
    const productId = document.getElementById('productSelect').value;
    if (!productId) return;

    const product = await fetchAPI(`products/${productId}`);
    if (!product) return;

    updatePriceStats(product);
    renderPriceHistoryChart(product);
}

function updatePriceStats(product) {
    const prices = product.price_history.map(p => p.price);
    document.getElementById('currentPrice').textContent = formatPrice(product.current_price);
    document.getElementById('lowestPrice').textContent = formatPrice(Math.min(...prices));
    document.getElementById('highestPrice').textContent = formatPrice(Math.max(...prices));
    document.getElementById('averagePrice').textContent = formatPrice(
        prices.reduce((a, b) => a + b, 0) / prices.length
    );
}

function renderPriceHistoryChart(product) {
    const trace = {
        x: product.price_history.map(p => p.timestamp),
        y: product.price_history.map(p => p.price),
        type: 'scatter',
        mode: 'lines+markers'
    };

    const layout = {
        title: `Price History for ${product.name}`,
        xaxis: { title: 'Date' },
        yaxis: { title: 'Price (KES)' }
    };

    Plotly.newPlot('priceHistoryChart', [trace], layout);
}
