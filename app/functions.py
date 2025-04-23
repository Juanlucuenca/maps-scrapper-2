import time
from playwright.sync_api import sync_playwright
from app.utils import extract_data

from app.models import SearchGoogleMapsResponse, SearchGoogleMapsResponseItem
        
def process_listing(listing_to_process, page) ->  SearchGoogleMapsResponse:
    """Process listing container and return formatted place data"""
    
    result: SearchGoogleMapsResponse = SearchGoogleMapsResponse()
    # Conjunto para almacenar nombres ya procesados y evitar duplicados
    processed_names = set()
    
    name_xpath = '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]'
    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
    website_xpath = '//a[@data-item-id="authority"]'
    phone_xpath = '//button[contains(@data-item-id, "phone")]//div[contains(@class, "fontBodyMedium")]'
    schedule_xpath1 = '//div[contains(@aria-label, "Tuesday,")]'
    schedule_xpath2 = '//div[contains(@jsaction, "pane.openhours")]//span[contains(@aria-label, "Show open hours for the week")]'
    for listing in listing_to_process:
        listing.click()
        page.wait_for_selector('//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]', timeout=30000)
        page.wait_for_timeout(3000)
        
        name = extract_data(name_xpath, page)
        
        # Verificar si el nombre ya ha sido procesado
        if name and name in processed_names:
            print(f"Skipping duplicate restaurant: {name}")
            continue
            
        # Añadir el nombre al conjunto de nombres procesados
        if name:
            processed_names.add(name)
        
        address = extract_data(address_xpath, page)
        
        if page.locator(website_xpath).count() > 0:
            website = page.locator(website_xpath).get_attribute("href")
        else:
            website = ""
        
        phone = extract_data(phone_xpath, page)
        if page.locator(schedule_xpath2).count() > 0:
            page.locator(schedule_xpath2).click()
            page.wait_for_selector('//div[contains(@aria-label, "Tuesday,")]', timeout=10000)
            schedule_text = page.locator(schedule_xpath1).get_attribute("aria-label")
        elif page.locator(schedule_xpath1).count() > 0:
            schedule_text = page.locator(schedule_xpath1).get_attribute("aria-label")
        else:
            schedule_text = ""
        
        # Limpiar el texto del horario
        if schedule_text:
            # Reemplazar los caracteres \u202f por espacio normal
            schedule_text = schedule_text.replace('\u202f', ' ')
            
            # Eliminar "Hide open hours for the week" si está presente
            if ". Hide open hours for the week" in schedule_text:
                schedule_text = schedule_text.split(". Hide open hours for the week")[0]
            
            # Eliminar cualquier otro texto innecesario después del último día
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            last_day_index = -1
            
            for day in days:
                if day in schedule_text:
                    last_day_index = max(last_day_index, schedule_text.rfind(day))
            
            if last_day_index != -1:
                # Encuentra el final de la información del último día
                parts = schedule_text[last_day_index:].split(';')
                if parts:
                    end_of_schedule = parts[0].split('.')
                    if end_of_schedule:
                        schedule_text = schedule_text[:last_day_index] + end_of_schedule[0]
                        if ';' in schedule_text[:last_day_index]:
                            schedule_text += '.'
        
        result.items.append(SearchGoogleMapsResponseItem(name=name, address=address, website=website, phone_number=phone, schedule=schedule_text))
        print(result)
        
    return result
        


def main(usr_query: str) -> SearchGoogleMapsResponse:
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.google.com/maps?gl=MX&hl=en", wait_until="load")
    page.wait_for_timeout(2000)

    print(f"Searching for {usr_query}")
    input_box = page.locator('//input[@name="q"]')
    input_box.fill(usr_query)
    input_box.press("Enter")

    xpath_search_result_element = '//div[@role="feed"]'
    page.wait_for_selector(xpath_search_result_element)
    results_container = page.query_selector(xpath_search_result_element)
    results_container.scroll_into_view_if_needed()

    keep_scrolling = True
    while keep_scrolling:
        print("Scrolling...")
        results_container.press("Space")
        time.sleep(1)
    
        if results_container.query_selector('//span[text()="You\'ve reached the end of the list."]'):
            print("Reached the end of the list")
            results_container.press("Space")
            keep_scrolling = False
            
            all_listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
            
            listening_to_process = [listing.locator("xpath=..") for listing in all_listings]
        
            places_string = process_listing(listening_to_process, page)
        
    context.close()
    browser.close()
    playwright.stop()
    
    return places_string










