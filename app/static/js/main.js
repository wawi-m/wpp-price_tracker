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
        const response = await fetch(`https://wpp-pricetracker-7e955bd28547.herokuapp.com/api/v1/${endpoint}`);
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
        total_products: document.getElementById('total_products'),
        price_drops: document.getElementById('price_drops'),
        price_increases: document.getElementById('price_increases'),
        jumia_products: document.getElementById('jumia_products'),
        jumia_prices: document.getElementById('jumia_prices'),
        kilimall_products: document.getElementById('kilimall_products'),
        kilimall_prices: document.getElementById('kilimall_prices')
    };

    // Verify all elements exist
    console.log("statElements:", statElements);
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
        statElements.total_products.textContent = data.total_products || '0';
        statElements.price_drops.textContent = data.price_drops || '0';
        statElements.price_increases.textContent = data.price_increases || '0';
        
        // Update platform stats
        statElements.jumia_products.textContent = data.jumia_products || '0';
        statElements.jumia_prices.textContent = `${data.jumia_prices || '0'} prices tracked`;
        statElements.kilimall_products.textContent = data.kilimall_products || '0';
        statElements.kilimall_prices.textContent = `${data.kilimall_prices || '0'} prices tracked`;

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
            
            col.innerHTML = `...`;  // same as before

            container.appendChild(col);
        });

        const loadMoreBtn = document.getElementById('loadMore');
        if (loadMoreBtn) {
            loadMoreBtn.style.display = data.has_next ? 'block' : 'none';
        }
    } catch (error) {
        console.error('Error loading products:', error);
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
});
