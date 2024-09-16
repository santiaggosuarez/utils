from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

# Configuración para abrir Chrome en modo maximizado
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Iniciar el navegador utilizando webdriver-manager
driver = webdriver.Chrome(service=Service('/home/ssantiago/ChromeDriver/chromedriver-linux64/chromedriver'))

# Abrir una página web (puedes cambiarla según tus necesidades)
driver.get("https://www.google.com")

# Esperar 120 segundos para navegar
time.sleep(120)

# Refrescar la página cada 2 segundos
try:
    while True:
        driver.refresh()
        time.sleep(2)
except KeyboardInterrupt:
    # Cerrar el navegador si se interrumpe el bucle
    driver.quit()
