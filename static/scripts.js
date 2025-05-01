// Tab switching
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons and content
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked button and corresponding content
        button.classList.add('active');
        document.getElementById(button.dataset.tab).classList.add('active');
    });
});

// Collection management
const collectionTable = document.getElementById('collection-table').querySelector('tbody');
const addKeycapForm = document.getElementById('add-keycap-form');

// Load collection
async function loadCollection() {
    try {
        const response = await fetch('/api/keycaps?vendor=s-craft');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const keycaps = await response.json();
        renderCollection(keycaps);
    } catch (error) {
        console.error('Error loading collection:', error);
        showError('Failed to load collection. Please try again later.');
    }
}

// Render collection
function renderCollection(keycaps) {
    collectionTable.innerHTML = '';
    if (!keycaps || keycaps.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="8" class="no-data">No keycaps in collection</td>';
        collectionTable.appendChild(row);
        return;
    }
    
    keycaps.forEach(keycap => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${keycap.name}</td>
            <td>${keycap.vendor}</td>
            <td>${keycap.artisan || ''}</td>
            <td>${keycap.pokemon || ''}</td>
            <td>${keycap.color || ''}</td>
            <td>${keycap.purchase_date || ''}</td>
            <td>${keycap.notes || ''}</td>
            <td class="actions">
                <button onclick="editKeycap('${keycap._id}')">Edit</button>
                <button onclick="deleteKeycap('${keycap._id}')">Delete</button>
            </td>
        `;
        collectionTable.appendChild(row);
    });
}

// Add keycap
addKeycapForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(addKeycapForm);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/keycaps', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add keycap');
        }
        
        addKeycapForm.reset();
        loadCollection();
    } catch (error) {
        console.error('Error adding keycap:', error);
        showError(error.message);
    }
});

// Edit keycap
async function editKeycap(id) {
    // Implementation for editing a keycap
    console.log('Edit keycap:', id);
}

// Delete keycap
async function deleteKeycap(id) {
    if (confirm('Are you sure you want to delete this keycap?')) {
        try {
            const response = await fetch(`/api/keycaps/${id}`, {
                method: 'DELETE',
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to delete keycap');
            }
            
            loadCollection();
        } catch (error) {
            console.error('Error deleting keycap:', error);
            showError(error.message);
        }
    }
}

// Drops management
const dropsTable = document.getElementById('drops-table').querySelector('tbody');
const scrapeBtn = document.getElementById('scrape-btn');
const compareBtn = document.getElementById('compare-btn');

let currentDrops = [];  // Store the current drops data

// Load drops
async function loadDrops(forceScrape = false) {
    try {
        const response = await fetch(`/api/drops${forceScrape ? '?force=true' : ''}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const drops = await response.json();
        currentDrops = drops;  // Store the drops data
        renderDrops(drops);
    } catch (error) {
        console.error('Error loading drops:', error);
        showError('Failed to load drops. Please try again later.');
    }
}

// Render drops
function renderDrops(drops) {
    dropsTable.innerHTML = '';
    if (!drops || drops.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="7" class="no-data">No drops available</td>';
        dropsTable.appendChild(row);
        return;
    }
    
    drops.forEach(drop => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${drop.name}</td>
            <td>${drop.image_url ? `<img src="${drop.image_url}" alt="${drop.name}" loading="lazy">` : 'No image'}</td>
            <td>${drop.pokemon || ''}</td>
            <td>${drop.color || ''}</td>
            <td>Batch ${drop.batch}</td>
            <td>${drop.price}</td>
            <td>Available</td>
        `;
        dropsTable.appendChild(row);
    });
}

// Scrape latest drops
scrapeBtn.addEventListener('click', async () => {
    scrapeBtn.disabled = true;
    scrapeBtn.textContent = 'Scraping...';
    
    try {
        await loadDrops(true);  // Force new scrape
        scrapeBtn.textContent = 'Scrape Latest Drops';
    } catch (error) {
        console.error('Error scraping drops:', error);
        showError('Failed to scrape drops. Please try again later.');
        scrapeBtn.textContent = 'Scrape Latest Drops';
    } finally {
        scrapeBtn.disabled = false;
    }
});

// Compare drops with collection
compareBtn.addEventListener('click', async () => {
    if (!currentDrops || currentDrops.length === 0) {
        showError('No drops data available. Please scrape drops first.');
        return;
    }
    
    try {
        const response = await fetch('/api/keycaps?vendor=s-craft');
        if (!response.ok) {
            throw new Error('Failed to fetch collection data');
        }
        
        const collection = await response.json();
        
        // Get collection names for comparison
        const collectionNames = new Set(collection.map(item => item.name));
        
        // Update drops table with comparison
        dropsTable.querySelectorAll('tr').forEach(row => {
            const nameCell = row.querySelector('td:first-child');
            const name = nameCell.textContent;
            
            if (!collectionNames.has(name)) {
                row.classList.add('missing');
                row.querySelector('td:last-child').textContent = 'Not in Collection';
            } else {
                row.classList.remove('missing');
                row.querySelector('td:last-child').textContent = 'In Collection';
            }
        });
    } catch (error) {
        console.error('Error comparing drops:', error);
        showError('Failed to compare drops with collection. Please try again later.');
    }
});

// Show error message
function showError(message) {
    // You can implement a more sophisticated error display here
    alert(message);
}

// Initial load
loadCollection();
// Don't automatically load drops on page load
// Instead, wait for user to click the Scrape button
