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
        const response = await fetch(`/api/v1/${endpoint}`);
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error:', error);
        return null;
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

    // Verify all elements exist
    const missingElements = Object.entries(statElements)
        .filter(([key, element]) => !element)
        .map(([key]) => key);

    if (missingElements.length > 0) {
        console.error('Missing stat elements:', missingElements);
        return;
    }

    try {
        const data = await fetchAPI('stats');
        if (!data) throw new Error('Failed to load stats');
        
        // Log received data for debugging
        console.log('Received stats data:', data);
        
        // Update stats with fallback to 0
        statElements.totalProducts.textContent = data.total_products || '0';
        statElements.priceDrops.textContent = data.price_drops || '0';
        statElements.priceIncreases.textContent = data.price_increases || '0';
        
        // Update platform stats
        statElements.jumiaProducts.textContent = data.jumia_products || '0';
        statElements.jumiaPrices.textContent = `${data.jumia_prices || '0'} prices tracked`;
        statElements.kilimallProducts.textContent = data.kilimall_products || '0';
        statElements.kilimallPrices.textContent = `${data.kilimall_prices || '0'} prices tracked`;

        // Log successful update
        console.log('Stats updated successfully');
    } catch (error) {
        console.error('Error loading stats:', error);
        // Set all stats to 0 on error
        Object.values(statElements).forEach(element => {
            if (element.id.includes('Prices')) {
                element.textContent = '0 prices tracked';
            } else {
                element.textContent = '0';
            }
        });
    }
}

// Products Functions
async function loadProducts(page = 1, append = false, search = '') {
    try {
        // First, load categories and platforms if needed
        const categoryFilter = document.getElementById('categoryFilter');
        const platformFilter = document.getElementById('platformFilter');
        
        // Load categories if filter is empty
        if (categoryFilter && !categoryFilter.children.length) {
            const categories = await fetchAPI('categories');
            if (categories) {
                categoryFilter.innerHTML = '<option value="">All Categories</option>';
                categories.forEach(category => {
                    categoryFilter.innerHTML += `<option value="${category.id}">${category.name}</option>`;
                });
            }
        }
        
        // Load platforms if filter is empty
        if (platformFilter && !platformFilter.children.length) {
            const platforms = await fetchAPI('platforms');
            if (platforms) {
                platformFilter.innerHTML = '<option value="">All Platforms</option>';
                platforms.forEach(platform => {
                    platformFilter.innerHTML += `<option value="${platform.id}">${platform.name}</option>`;
                });
            }
        }

        // Get selected filter values
        const categoryId = categoryFilter?.value;
        const platformId = platformFilter?.value;

        const params = new URLSearchParams({
            page,
            ...(search && { search }),
            ...(categoryId && { category_id: categoryId }),
            ...(platformId && { platform_id: platformId })
        });

        const data = await fetchAPI(`products?${params}`);
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
        }
    } catch (error) {
        console.error('Error loading products:', error);
        const container = document.getElementById('productsList');
        if (!append) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-danger">
                        Failed to load products. Please try again later.
                    </div>
                </div>
            `;
        }
    }
}

// Price History Functions
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
        
        console.log(chartData);
        
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

        const detailsContainer = document.getElementById('productDetails');
        if (detailsContainer) {
            const imageUrl = product.image_url || placeholderImage;
            detailsContainer.innerHTML = `
                <div class="text-center mb-3">
                    <img src="${imageUrl}" 
                         alt="${product.name}" 
                         class="img-fluid" 
                         style="max-height: 200px;"
                         onerror="this.src='${placeholderImage}'">
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

// Compare functionality
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

// Search functionality
const searchProducts = debounce(() => {
    const searchQuery = document.getElementById('searchQuery')?.value.trim();
    if (searchQuery) {
        loadProducts(1, false, searchQuery);
    }
}, 500);

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data
    loadStats();
    loadProducts();
    
    // Set up search functionality
    const searchInput = document.getElementById('searchQuery');
    if (searchInput) {
        searchInput.addEventListener('input', searchProducts);
    }
    
    // Set up load more functionality
    const loadMoreBtn = document.getElementById('loadMore');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', () => {
            const currentPage = Math.ceil(document.querySelectorAll('.product-card').length / 12);
            loadProducts(currentPage + 1, true);
        });
    }

    // Set up filters
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => loadProducts(1));
    }

    const platformFilter = document.getElementById('platformFilter');
    if (platformFilter) {
        platformFilter.addEventListener('change', () => loadProducts(1));
    }
});