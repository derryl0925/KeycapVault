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
