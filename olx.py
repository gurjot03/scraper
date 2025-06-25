from playwright.sync_api import sync_playwright
import os
import json

def initialize_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    return playwright, browser, page

def load_existing_data(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def append_to_json(new_listings, filename):
    existing_data = load_existing_data(filename)
    existing_data.extend(new_listings)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

def scrape(url, output_file='olx_listings.json'):
    playwright, browser, page = initialize_browser()
    
    processed_count = len(load_existing_data(output_file))
    
    try:
        page.goto(url)
        page.wait_for_timeout(5000)

        while True:
            listing_elements = page.locator("li[data-aut-id='itemBox3']")
            current_total = listing_elements.count()
            print(f"Found {current_total} total listings on page, already processed: {processed_count}")
            
            new_listings = []
            for i in range(processed_count, current_total):
                try:
                    element = listing_elements.nth(i)
                    
                    price_element = element.locator("span[data-aut-id='itemPrice']")
                    price = price_element.inner_text() if price_element.count() > 0 else "N/A"

                    details_element = element.locator("span[data-aut-id='itemDetails']")
                    details = details_element.inner_text() if details_element.count() > 0 else "N/A"
                    
                    title_element = element.locator("span[data-aut-id='itemTitle']")
                    title = title_element.inner_text() if title_element.count() > 0 else "N/A"

                    location_element = element.locator("span[data-aut-id='item-location']")
                    location = location_element.inner_text() if location_element.count() > 0 else "N/A"
                    
                    listing_data = {
                        "title": title,
                        "price": price,
                        "details": details,
                        "location": location
                    }
                    
                    new_listings.append(listing_data)
                    print(f"Processed listing {processed_count + len(new_listings)}: {title}")
                    
                except Exception as e:
                    print(f"Error processing listing {i}: {e}")
                    continue
            
            if new_listings:
                append_to_json(new_listings, output_file)
                print(f"Appended {len(new_listings)} new listings to {output_file}")
                processed_count += len(new_listings)
            
            load_more_button = page.locator("button[data-aut-id='btnLoadMore']")
            if load_more_button.count() > 0:
                print("Clicking load more button...")
                load_more_button.click()
                page.wait_for_timeout(15000)
            else:
                print("No more content to load")
                break
                
    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        browser.close()
        playwright.stop()

if __name__ == "__main__":
    url = 'https://www.olx.in/items/q-car-cover'
    scrape(url)