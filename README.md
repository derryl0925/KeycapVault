# KeycapVault

A web application for tracking Pokémon keycap collections and comparing against S-Craft Studio drops.

## Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- Homebrew (for macOS)
- MongoDB Community Edition

### 2. Install MongoDB
```bash
# Install MongoDB using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Create data directory
mkdir -p ~/data/mongodb
chmod 755 ~/data/mongodb

# Start MongoDB service
brew services start mongodb-community
```

### 3. Install Python Dependencies
```bash
# Install required Python packages
pip install -r requirements.txt
```

### 4. Configure MongoDB
- MongoDB will run on the default port (27017)
- Data will be stored in `~/data/mongodb`
- No additional configuration needed for local development

### 5. Run the Application
```bash
# Start the Flask application
python app.py
```
The application will be available at http://127.0.0.1:5001

### 6. Troubleshooting

#### MongoDB Issues
- If MongoDB fails to start:
  ```bash
  # Check MongoDB status
  brew services list
  
  # Restart MongoDB
  brew services restart mongodb-community
  ```

- If you get permission errors:
  ```bash
  # Fix permissions on data directory
  sudo chown -R $(whoami) ~/data/mongodb
  ```

#### Application Issues
- If port 5001 is in use:
  - Edit `app.py` and change the port number
  - Or find and stop the process using port 5001

- If you get SSL/OpenSSL warnings:
  - These warnings are non-critical and won't affect functionality
  - They're related to macOS's LibreSSL and can be safely ignored

### 7. Development Notes
- The application uses MongoDB for persistent storage
- Scraped data is stored in the `scrapes` collection
- User collections are stored in the `keycaps` collection
- The database is automatically initialized when the application starts

### 8. API Endpoints
- `GET /` - Main application page
- `GET /api/keycaps` - Get all keycaps (optionally filtered by vendor)
- `POST /api/keycaps` - Add a new keycap
- `PUT /api/keycaps/<id>` - Update a keycap
- `DELETE /api/keycaps/<id>` - Delete a keycap
- `GET /api/drops` - Get latest S-Craft drops
- `GET /api/drops?force=true` - Force a new scrape

## Technical Issues and Fixes

### 1. Duplicate Items in Scraping
**Issue**: The scraper was creating duplicate entries for the same product across different pages of the same batch.
**Root Cause**: The deduplication logic was only checking for exact name matches, but some products appeared multiple times with slight variations in their names or formatting.
**Solution**: 
- Implemented a more robust deduplication system using a combination of product name and batch number
- Added a `seen_products` set to track unique products using a composite key: `f"{name}_{batch_num}"`
- Improved name normalization to handle variations in product names

### 2. Missing Items in Scraping
**Issue**: Some items from batches 9-12 were not being scraped correctly.
**Root Cause**: 
- The website's HTML structure changed for later batches
- Image URLs were using different selectors and formats
- Some products were in different page layouts
**Solution**:
- Added multiple fallback selectors for product cards and images
- Implemented a more flexible image URL cleaning function
- Added batch-specific handling for different HTML structures
- Improved error handling and logging for failed scrapes

### 3. Database Connection Issues
**Issue**: Keycaps were being added to the database but not showing up in the frontend.
**Root Cause**: 
- Inconsistent vendor name casing ("S-Craft" vs "s-craft")
- Frontend was not properly handling the database response
- Missing error handling in the frontend code
**Solution**:
- Standardized vendor name to "S-Craft" across the application
- Added comprehensive error handling and logging
- Implemented proper async/await patterns in the frontend
- Added debug logging to track data flow

### 4. Image URL Issues
**Issue**: Some product images were not loading correctly.
**Root Cause**: 
- Relative URLs were not being properly converted to absolute URLs
- Some image URLs contained query parameters or were malformed
**Solution**:
- Implemented a robust URL cleaning function
- Added proper URL joining with the base URL
- Added validation for image URLs
- Implemented fallback image handling

## Manual Database Inspection

To manually inspect the MongoDB database, you can use the `mongosh` command-line tool. Here are some useful commands:

1. Connect to the database:
```bash
mongosh keycapvault
```

2. View all keycaps:
```bash
mongosh keycapvault --eval "db.keycaps.find().pretty()"
```

3. View keycaps by vendor:
```bash
mongosh keycapvault --eval "db.keycaps.find({vendor: 'S-Craft'}).pretty()"
```

4. Count total keycaps:
```bash
mongosh keycapvault --eval "db.keycaps.countDocuments()"
```

5. View latest scrape results:
```bash
mongosh keycapvault --eval "db.scrapes.find().sort({scraped_at: -1}).limit(1).pretty()"
```
