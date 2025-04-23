import random
import time
from playwright.sync_api import sync_playwright
from app.utils import extract_data

from app.models import SearchGoogleMapsResponse, SearchGoogleMapsResponseItem
        
def process_listing(listing_to_process, page) ->  SearchGoogleMapsResponse:
    """Process listing container and return formatted place data"""
    
    result: SearchGoogleMapsResponse = SearchGoogleMapsResponse()
    # Conjunto para almacenar nombres ya procesados y evitar duplicados
    processed_names = set()
    lastname = None
    
    name_xpath = '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]'
    address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
    website_xpath = '//a[@data-item-id="authority"]'
    phone_xpath = '//button[contains(@data-item-id, "phone")]//div[contains(@class, "fontBodyMedium")]'
    schedule_xpath1 = '//div[contains(@aria-label, "Tuesday,")]'
    schedule_xpath2 = '//div[contains(@jsaction, "pane.openhours")]//span[contains(@aria-label, "Show open hours for the week")]'
    
    for listing in listing_to_process:
        try:
            # Hacemos clic en el listing
            listing.click()
            
            # Esperamos a que aparezca el selector del nombre
            page.wait_for_selector(name_xpath, timeout=30000)
            
            # Obtenemos el nombre
            current_name = extract_data(name_xpath, page)
            
            # Si no hay nombre, continuamos con el siguiente
            if not current_name:
                print("No se pudo obtener el nombre, continuando...")
                continue
            
            # Verificamos si el nombre es igual al último procesado
            max_retries = 5
            retries = 0
            
            # Esperamos hasta que el nombre cambie o se agoten los intentos
            while current_name == lastname and retries < max_retries:
                print(f"Esperando a que cambie el nombre. Intento {retries+1}/{max_retries}...")
                time.sleep(8)  # Esperamos 10 segundos
                current_name = extract_data(name_xpath, page)
                retries += 1
            
            # Si después de los intentos sigue siendo el mismo, saltamos
            if current_name == lastname:
                print(f"El nombre no cambió después de {max_retries} intentos, saltando...")
                continue
            
            # Verificamos si el nombre ya ha sido procesado
            if current_name in processed_names:
                print(f"Saltando restaurante duplicado: {current_name}")
                continue
                
            # Actualizamos el último nombre procesado
            lastname = current_name
            
            # Añadimos el nombre al conjunto de procesados
            processed_names.add(current_name)
            
            # Ahora extraemos el resto de la información
            address = extract_data(address_xpath, page)
            
            if page.locator(website_xpath).count() > 0:
                website = page.locator(website_xpath).get_attribute("href")
            else:
                website = ""
            
            phone = extract_data(phone_xpath, page)
            
            # Obtenemos la información del horario
            schedule_text = ""
            if page.locator(schedule_xpath2).count() > 0:
                page.locator(schedule_xpath2).click()
                try:
                    page.wait_for_selector(schedule_xpath1, timeout=10000)
                    schedule_text = page.locator(schedule_xpath1).get_attribute("aria-label")
                except:
                    print(f"No se pudo obtener el horario para {current_name}")
            elif page.locator(schedule_xpath1).count() > 0:
                schedule_text = page.locator(schedule_xpath1).get_attribute("aria-label")
            
            # Limpiamos el texto del horario
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
            
            # Agregamos el elemento a los resultados
            result.items.append(SearchGoogleMapsResponseItem(
                name=current_name, 
                address=address, 
                website=website, 
                phone_number=phone, 
                schedule=schedule_text
            ))
            
            print(f"Procesado correctamente: {current_name}")
            
        except Exception as e:
            print(f"Error al procesar listing: {str(e)}")
            continue
    
    return result


def main(usr_query: str) -> SearchGoogleMapsResponse:
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=True,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-gpu',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process'
        ]
    )
    context = browser.new_context(
        user_agent=user_agent,
        viewport={"width": 1920, "height": 1080},
        geolocation={"latitude": 19.4326, "longitude": -99.1332},  # Ciudad de México
        locale="en-US",
        timezone_id="America/Mexico_City",
        record_video_dir="videos/",
        record_video_size={"width": 1920, "height": 1080}
    )
    
    page = context.new_page()

    page.goto("https://www.google.com/maps?gl=MX&hl=en", wait_until="load")
    page.wait_for_timeout(2000)

    print(f"Searching for {usr_query}")
    input_box = page.locator('//input[@name="q"]')
    input_box.fill(usr_query)
    page.wait_for_timeout(random.randint(500, 1000))  # Simular pausa humana
    input_box.press("Enter")

    xpath_search_result_element = '//div[@role="feed"]'
    page.wait_for_selector(xpath_search_result_element)
    results_container = page.query_selector(xpath_search_result_element)
    page.wait_for_timeout(3000)  # Dar tiempo para que carguen resultados iniciales

    keep_scrolling = True
    while keep_scrolling:
        print("Scrolling...")
        results_container.press("Space")
        time.sleep(2.5)
    
        if results_container.query_selector('//span[text()="You\'ve reached the end of the list."]'):
            print("Reached the end of the list")
            results_container.press("Space")
            keep_scrolling = False
            
            all_listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
            
            listening_to_process = [listing.locator("xpath=..") for listing in all_listings]
        
            places_string = process_listing(listening_to_process, page)
        
    context.close()
    page.close()
    browser.close()
    playwright.stop()
    
    return places_string










