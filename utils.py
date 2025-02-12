import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def setup_logging(log_path, execution_id):
    """
    Configura el sistema de logging con dos manejadores: uno para escribir en un archivo con un formato detallado
    (incluyendo fecha, hora, nivel de severidad y nombre del módulo) y otro para imprimir
    en la consola con un formato más simple (solo el mensaje).
    
    Args:
        log_path (str): Ruta a la carpeta de program logs.
        execution_id (str): Identificador de la ejecución que se está registrando.
    """
    os.makedirs(log_path, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    file_format = logging.Formatter(f"{execution_id} - %(asctime)s - %(levelname)s - %(module)s - %(message)s")
    console_format = logging.Formatter('%(message)s')

    path = os.path.join(log_path, f"{execution_id}.log")
    file_handler = logging.FileHandler(path)
    file_handler.setFormatter(file_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    

def get_driver(options_configurations, mode="headless"):
    """
    Inicializa y retorna un driver de Chrome con configuraciones específicas.
    
    Args:
        options_configurations (dict): Diccionario con configuraciones para el driver de Chrome.
        mode (str): Modo en el que se abrirá el navegador. Ejemplo: "headless", "start-maximized"
    
    Returns:
        webdriver: Una instancia del driver de Chrome con las opciones dadas.
    """
    try:
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-images")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("prefs", {"translate": {"enabled": False}})

        options.add_argument(f"--{mode or 'headless'}")
        options.add_argument(f"user-agent={options_configurations['user_agent']}")
        service = Service(options_configurations['chromedriver_path'])
        
        return webdriver.Chrome(service=service, options=options)

    except Exception as e:
        logging.exception("Error initializing Chrome driver")
