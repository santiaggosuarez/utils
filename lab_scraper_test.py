"""
  Prueba para descargar imágenes de envases de medicamentos desde la web de un laboratorio.
"""
import os
import re
import json
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def sanitize_filename(filename):
    """Estandariza el nombre para usarlo como archivo"""
    return re.sub(r'[\\/*?:"<>|]', "_", filename).strip()

def setup_driver():
    """Configura el driver de Selenium"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Ejecución sin interfaz gráfica headless or start-maximized
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_casasco_products(base_url, output_folder):
    """
    Scrapea productos de Casasco usando Selenium
    
    Args:
        base_url (str): URL base para scrapear productos
        output_folder (str): Carpeta donde guardar los resultados
    """
    driver = setup_driver()
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        driver.execute_script("document.body.style.zoom='70%'")
        
        # 1. Obtener todos los links de productos
        print(f"Obteniendo productos de {base_url}...")
        product_links = get_product_links(driver, base_url)
        
        # 2. Procesar cada producto
        print(f"\nProcesando {len(product_links)} productos...")
        for product_name, product_url in product_links.items():
            print(f"\nProcesando: {product_name}")
            process_product_page(driver, product_name, product_url, output_folder)
            
    finally:
        driver.quit()

def get_product_links(driver, base_url):
    """Obtiene todos los links de productos de la página base"""
    driver.get(base_url)
    time.sleep(3)  # Esperar carga inicial
    
    # Scroll para cargar contenido dinámico
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    product_links = {}
    product_pattern = "https://www.casasco.com.ar/es/producto/"
    
    links = driver.find_elements(By.XPATH, f"//a[starts-with(@href, '{product_pattern}')]")
    for link in links:
        product_name = sanitize_filename(link.text)
        product_url = link.get_attribute("href")
        if product_name and product_url:
            product_links[product_name] = product_url
    
    return product_links

def process_product_page(driver, product_name, product_url, output_folder):
    """Procesa una página individual de producto"""
    try:
        driver.get(product_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "post-content"))
        )
        
        driver.execute_script("document.body.style.transform='scale(0.7)'; document.body.style.transformOrigin='0 0'")
        
        product_data = {
            "name": product_name,
            "source_url": product_url,
            "text": "",
            "download_pdf_url": ""
        }
        
        # 1. Extraer texto y elementos del post-content
        post_content = driver.find_element(By.CLASS_NAME, "post-content")
        product_data["text"] = extract_text_from_post(post_content)
        
        # 2. Descargar imágenes
        download_images(driver, post_content, product_name, output_folder)
        
        # 3. Buscar el PDF del prospecto con espera y validaciones mejoradas
        try:
            # Primero hacer scroll para asegurar visibilidad
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_content)
            time.sleep(1)  # Pequeña pausa para animaciones
            
            # Esperar explícitamente para el botón específico
            pdf_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, ".//a[contains(@class, 'fusion-button') and contains(., 'Descarga el prospecto') and contains(@href, '.pdf')]")
                )
            )
            
            # Obtener URL y validarla
            pdf_url = pdf_link.get_attribute('href')
            if not pdf_url.lower().endswith('.pdf'):
                raise ValueError("El enlace no termina con .pdf")
            
            product_data["download_pdf_url"] = pdf_url
            print(f"  ✓ PDF encontrado: {pdf_url}")
            
        except Exception as e:
            print(f"  ! Error al obtener PDF: {str(e)}")
            product_data["download_pdf_url"] = ""
        
        # Guardar JSON con los datos
        save_product_json(product_data, product_name, output_folder)
        
    except Exception as e:
        print(f"Error procesando {product_name}: {str(e)}")

def extract_text_from_post(post_content):
    """Extrae todo el texto de los párrafos en post-content"""
    paragraphs = post_content.find_elements(By.TAG_NAME, "p")
    return "\n\n".join([p.text for p in paragraphs if p.text.strip()])

def download_images(driver, post_content, product_name, output_folder):
    """Descarga todas las imágenes encontradas en los href de etiquetas a con manejo de errores mejorado"""
    try:
        img_links = []
        links = post_content.find_elements(By.TAG_NAME, "a")
        
        # 1. Recolectar URLs de imágenes válidas
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and href.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    img_links.append(href)
            except Exception as e:
                print(f"  Error obteniendo enlace: {str(e)}")
                continue
        
        # 2. Descargar imágenes con múltiples mejoras
        for i, img_url in enumerate(img_links, 1):
            try:
                img_ext = os.path.splitext(img_url)[1] or '.jpg'
                img_name = f"{product_name}_{i}{img_ext}"
                img_path = os.path.join(output_folder, img_name)
                
                # Configuración de la petición HTTP
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                # Intentar hasta 3 veces con delays
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        # Espera entre intentos (aumenta progresivamente)
                        time.sleep(1 + attempt)  # 1s, luego 2s, luego 3s
                        
                        # Hacer la petición con timeout
                        response = requests.get(img_url, headers=headers, stream=True, timeout=10)
                        response.raise_for_status()  # Verificar código HTTP
                        
                        # Verificar que sea realmente una imagen
                        if 'image' not in response.headers.get('Content-Type', ''):
                            raise ValueError("El contenido no es una imagen válida")
                        
                        # Guardar la imagen
                        with open(img_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                if chunk:  # Filtrar chunks vacíos
                                    f.write(chunk)
                        
                        # Verificar que el archivo se creó correctamente
                        if os.path.getsize(img_path) == 0:
                            raise ValueError("Archivo de imagen vacío")
                            
                        print(f"  Imagen descargada correctamente: {img_name}")
                        break  # Salir del bucle de intentos si tuvo éxito
                        
                    except Exception as e:
                        if attempt == max_attempts - 1:  # Último intento fallido
                            print(f"  Error descargando imagen {img_url} (intento {attempt + 1}): {str(e)}")
                            if os.path.exists(img_path):  # Eliminar archivo corrupto si existe
                                os.remove(img_path)
                        continue
                        
            except Exception as e:
                print(f"  Error procesando imagen {img_url}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error general en download_images: {str(e)}")

def save_product_json(product_data, product_name, output_folder):
    """Guarda los datos del producto en un JSON"""
    json_path = os.path.join(output_folder, f"{product_name}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, ensure_ascii=False, indent=2)
    print(f"  JSON guardado: {product_name}.json")

if __name__ == "__main__":
    # Configuración
    BASE_URL = "https://www.casasco.com.ar/es/categoria-producto/productos/"
    OUTPUT_FOLDER = ""
    
    # Ejecutar scraper
    scrape_casasco_products(BASE_URL, OUTPUT_FOLDER)
