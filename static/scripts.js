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
        console.log('Starting to load collection...');
        const response = await fetch('/api/keycaps?vendor=S-Craft');
        console.log('API Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const keycaps = await response.json();
        console.log('Received keycaps data:', keycaps);
        
        if (!Array.isArray(keycaps)) {
            console.error('Received data is not an array:', keycaps);
            throw new Error('Invalid data format received from server');
        }
        
        renderCollection(keycaps);
    } catch (error) {
        console.error('Error loading collection:', error);
        showError('Failed to load collection. Please try again later.');
    }
}

// Render collection
function renderCollection(keycaps) {
    console.log('Starting to render collection...');
    console.log('Keycaps to render:', keycaps);
    
    collectionTable.innerHTML = '';
    if (!keycaps || keycaps.length === 0) {
        console.log('No keycaps to render, showing empty message');
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="no-data">No keycaps in collection</td>';
        collectionTable.appendChild(row);
        return;
    }
    
    console.log(`Rendering ${keycaps.length} keycaps`);
    keycaps.forEach((keycap, index) => {
        console.log(`Rendering keycap ${index + 1}:`, keycap);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${keycap.name || ''}</td>
            <td>${keycap.vendor || ''}</td>
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
    console.log('Form submitted');
    
    const formData = new FormData(addKeycapForm);
    const data = Object.fromEntries(formData.entries());
    console.log('Form data:', data);
    
    // Ensure consistent vendor name
    data.vendor = 'S-Craft';
    
    console.log('Data to be sent:', data);
    
    try {
        const response = await fetch('/api/keycaps', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        
        console.log('Add keycap response status:', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to add keycap');
        }
        
        const result = await response.json();
        console.log('Add keycap result:', result);
        
        addKeycapForm.reset();
        await loadCollection();
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
        row.innerHTML = '<td colspan="4" class="no-data">No drops available</td>';
        dropsTable.appendChild(row);
        return;
    }
    
    drops.forEach(drop => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${drop.name}</td>
            <td>${drop.image_url ? `<img src="${drop.image_url}" alt="${drop.name}" loading="lazy">` : 'No image'}</td>
            <td>Batch ${drop.batch}</td>
            <td>${drop.price}</td>
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
    console.log('Compare button clicked');
    console.log('Current drops:', currentDrops);
    
    if (!currentDrops || currentDrops.length === 0) {
        console.log('No drops data available');
        showError('No drops data available. Please scrape drops first.');
        return;
    }
    
    try {
        console.log('Fetching comparison data...');
        const response = await fetch('/api/compare');
        console.log('Comparison response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Comparison response error:', errorText);
            throw new Error('Failed to fetch comparison data');
        }
        
        const comparison = await response.json();
        console.log('Comparison results:', comparison);
        
        if (!comparison.matches || !comparison.missing) {
            console.error('Invalid comparison data structure:', comparison);
            throw new Error('Invalid comparison data received');
        }
        
        // Update drops table with comparison results
        const rows = dropsTable.querySelectorAll('tr');
        console.log(`Updating ${rows.length} rows in drops table`);
        
        rows.forEach((row, index) => {
            const nameCell = row.querySelector('td:first-child');
            if (!nameCell) {
                console.warn(`No name cell found in row ${index}`);
                return;
            }
            
            const name = nameCell.textContent.toLowerCase();
            console.log(`Checking row ${index} with name: ${name}`);
            
            // Check if this item is in the missing list
            const isMissing = comparison.missing.some(item => 
                item.name.toLowerCase() === name
            );
            
            console.log(`Row ${index} is ${isMissing ? 'missing' : 'found'}`);
            
            if (isMissing) {
                row.classList.add('missing');
            } else {
                row.classList.remove('missing');
            }
        });
        
        console.log('Comparison update complete');
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
console.log('Page loaded, initializing...');
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded');
    // Switch to collection tab and load data
    const collectionTab = document.querySelector('[data-tab="collection"]');
    if (collectionTab) {
        collectionTab.click();
        loadCollection();
    }
});
// Don't automatically load drops on page load
// Instead, wait for user to click the Scrape button
