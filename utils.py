import os
import logging
from typing import Any, Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager


def setup_logging(log_path: str, execution_id: str) -> None:
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
    

def get_driver(options_configurations: Dict[str, Any], mode: str = "headless") -> Optional[WebDriver]:
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
        options.add_experimental_option("prefs", {
            "translate": {"enabled": False},
            "download.default_directory": options_configurations.get("asset_download_folder"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "savefile.overwrite_existing_files": False
        })

        options.add_argument(f"--{mode or 'headless'}")
        options.add_argument(
            f"user-agent={options_configurations['user_agent']}")

        chromedriver_path = options_configurations.get("chromedriver_path")
        if not chromedriver_path:
            chromedriver_path = ChromeDriverManager().install()

        service = Service(chromedriver_path)

        return webdriver.Chrome(service=service, options=options)

    except Exception:
        logging.exception("Error initializing Chrome driver")

        logging.exception("Error initializing Chrome driver")
