import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime
import logging
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_image_url(url: str, base_url: str) -> str:
    """Clean and normalize image URL."""
    if not url:
        return None
    
    # Remove any query parameters
    url = url.split('?')[0]
    
    # Handle relative URLs
    if not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    
    return url

def scrape_s_craft() -> List[Dict]:
    """Scrape S-Craft Studio group buy page for keycap products."""
    base_url = "https://www.s-craft.studio/shop/group-buy"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    
    # Batch IDs mapping (batch number to ID and pages)
    batch_config = {
        1: {"id": 1, "pages": 1},
        2: {"id": 2, "pages": 1},
        3: {"id": 3, "pages": 1},
        4: {"id": 4, "pages": 1},
        5: {"id": 5, "pages": 1},
        6: {"id": 6, "pages": 1},
        7: {"id": 7, "pages": 1},
        8: {"id": 8, "pages": 1},
        9: {"id": 9, "pages": 1},
        10: {"id": 14, "pages": 1},
        11: {"id": 18, "pages": 2},
        12: {"id": 21, "pages": 2}
    }
    
    all_products = []
    seen_products = set()  # Track unique products by name and batch
    
    try:
        # Scrape each batch
        for batch_num, config in batch_config.items():
            batch_id = config["id"]
            pages = config["pages"]
            
            for page in range(1, pages + 1):
                url = f"{base_url}?batch_id={batch_id}"
                if page > 1:
                    url += f"&page={page}"
                
                logger.info(f"Scraping batch {batch_num} (ID: {batch_id}), page {page} from {url}")
                
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find product cards
                    product_cards = soup.select('div.product-item, div.product-card, div.product')
                    if not product_cards:
                        logger.warning(f"No products found in batch {batch_num} with primary selectors. Trying alternative selectors...")
                        product_cards = soup.select('div[class*="product"], div[class*="item"]')
                    
                    logger.info(f"Found {len(product_cards)} products in batch {batch_num}, page {page}")
                    
                    for card in product_cards:
                        try:
                            # Get product name with improved validation
                            name_elem = card.select_one('h2, h3, .product-name, .title, [class*="name"]')
                            if not name_elem or not name_elem.text.strip():
                                logger.warning(f"Skipping product with missing name in batch {batch_num}, page {page}")
                                continue
                                
                            name = name_elem.text.strip()
                            
                            # Skip if name is just whitespace or "Unknown Product"
                            if not name or name == "Unknown Product":
                                logger.warning(f"Skipping invalid product name in batch {batch_num}, page {page}")
                                continue
                            
                            # Create unique identifier for product (name + batch)
                            product_id = f"{name}_{batch_num}"
                            
                            # Skip if we've already seen this product in this batch
                            if product_id in seen_products:
                                logger.debug(f"Skipping duplicate product: {name} in batch {batch_num}")
                                continue
                            seen_products.add(product_id)
                            
                            # Get image URL with fallbacks for later batches
                            image_url = None
                            if batch_num >= 9:
                                # Try multiple image selectors for later batches
                                for selector in [
                                    'img.product-image',
                                    'img.main-image',
                                    'img[class*="product"]',
                                    'img[class*="main"]',
                                    'img'
                                ]:
                                    img_elem = card.select_one(selector)
                                    if img_elem and 'src' in img_elem.attrs:
                                        image_url = clean_image_url(img_elem['src'], base_url)
                                        if image_url and not image_url.endswith(('gif', 'svg')):  # Skip loading/placeholder images
                                            break
                            else:
                                # Original image handling for earlier batches
                                img_elem = card.select_one('img')
                                if img_elem and 'src' in img_elem.attrs:
                                    image_url = clean_image_url(img_elem['src'], base_url)
                            
                            # Get price with validation
                            price_elem = card.select_one('.price, [class*="price"], span[class*="amount"]')
                            if not price_elem or not price_elem.text.strip():
                                logger.warning(f"Missing price for product {name} in batch {batch_num}")
                                continue
                                
                            price = price_elem.text.strip()
                            
                            product = {
                                "name": name,
                                "image_url": image_url,
                                "product_url": url,
                                "price": price,
                                "batch": batch_num,
                                "vendor": "s-craft",
                                "scraped_at": datetime.utcnow().isoformat()
                            }
                            
                            logger.debug(f"Extracted product: {product}")
                            all_products.append(product)
                            
                        except Exception as e:
                            logger.error(f"Error parsing product card in batch {batch_num}, page {page}: {str(e)}")
                            continue
                    
                except requests.RequestException as e:
                    logger.error(f"Error fetching batch {batch_num}, page {page}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing batch {batch_num}, page {page}: {str(e)}")
                    continue
        
        logger.info(f"Successfully scraped {len(all_products)} unique products across all batches")
        return all_products
        
    except Exception as e:
        logger.error(f"Critical error in scraper: {str(e)}")
        return []

# For testing the scraper directly
if __name__ == "__main__":
    products = scrape_s_craft()
    print(f"Found {len(products)} products")
    for product in products[:5]:  # Print first 5 products as sample
        print(product)
