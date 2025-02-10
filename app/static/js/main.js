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
        // **🔹 Added caching to prevent unnecessary API calls**
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

// **🔹 New function to load category & platform filters first**
async function loadFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const platformFilter = document.getElementById('platformFilter');

    try {
        // **Fetch and populate categories**
        const categories = await fetchAPI('categories');
        if (categories && categoryFilter) {
            categoryFilter.innerHTML = '<option value="">All Categories</option>' + 
                categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
        }

        // **Fetch and populate platforms**
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

// Stats Functions
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

        // Update stats with fallback to 0
        statElements.totalProducts.textContent = data.total_products || '0';
        statElements.priceDrops.textContent = data.price_drops || '0';
        statElements.priceIncreases.textContent = data.price_increases || '0';
        statElements.jumiaProducts.textContent = data.jumia_products || '0';
        statElements.jumiaPrices.textContent = `${data.jumia_prices || '0'} prices tracked`;
        statElements.kilimallProducts.textContent = data.kilimall_products || '0';
        statElements.kilimallPrices.textContent = `${data.kilimall_prices || '0'} prices tracked`;

    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// **🔹 Updated loadProducts() to call loadFilters() first**
async function loadProducts(page = 1, append = false, search = '') {
    try {
        const categoryFilter = document.getElementById('categoryFilter');
        const platformFilter = document.getElementById('platformFilter');

        // **Ensure filters are loaded before fetching products**
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
                <div class="card">
                    <img src="${imageUrl}" class="card-img-top" alt="${product.name}">
                    <div class="card-body">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text">${formatPrice(product.current_price)}</p>
                    </div>
                </div>
            `;
            container.appendChild(col);
        });

    } catch (error) {
        console.error('Error loading products:', error);
    }
}

// **Price History Functions**
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
            data: chartData
        });

    } catch (error) {
        console.error('Error loading price history:', error);
    }
}

// **Compare functionality**
let compareList = [];
function addToCompare(productId) {
    if (!compareList.includes(productId)) {
        compareList.push(productId);
        if (compareList.length === 2) {
            window.location.href = `/compare?products=${compareList.join(',')}`;
        } else {
            alert('Select one more product to compare');
        }
    }
}

// **Search functionality**
const searchProducts = debounce(() => {
    const searchQuery = document.getElementById('searchQuery')?.value.trim();
    if (searchQuery) {
        loadProducts(1, false, searchQuery);
    }
}, 500);

// **Ensure filters load before products on page load**
document.addEventListener('DOMContentLoaded', async () => {
    await loadFilters();
    await loadProducts();
});
