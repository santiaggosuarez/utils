import logging
from pathlib import Path
from typing import Any, Mapping

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver


logger = logging.getLogger(__name__)


def setup_logging(log_path: str, execution_id: str) -> None:
    """Configura archivo y consola. Llamar al iniciar, antes de crear hilos.

    Reemplaza y cierra los manejadores existentes del logger raíz.
    """
    if not execution_id or Path(execution_id).name != execution_id:
        raise ValueError("execution_id debe ser un identificador, no una ruta.")

    log_directory = Path(log_path).expanduser().resolve()
    log_directory.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(
        log_directory / f"{execution_id}.log",
        mode="a",
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(execution_id)s - %(asctime)s - %(levelname)s - "
            "%(module)s - %(message)s",
            defaults={"execution_id": execution_id},
        )
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler],
        force=True,
    )


def get_driver(
    options_configurations: Mapping[str, Any],
    mode: str = "headless",
) -> WebDriver:
    """Crea Chrome o propaga una excepción si no puede iniciarlo.

    Modos: 'headless', 'headless=new', 'start-maximized' y 'normal'.

    Configuraciones opcionales:
        asset_download_folder: directorio de descargas.
        user_agent: user-agent personalizado.
        chromedriver_path: ruta al ejecutable de ChromeDriver.
        disable_images: bloquea imágenes; True por defecto.
        no_sandbox: desactiva el sandbox; False por defecto.
        disable_dev_shm_usage: evita /dev/shm; False por defecto.

    Sin chromedriver_path, Selenium Manager gestiona el driver.
    El código que llama a esta función debe ejecutar driver.quit() al terminar.
    """
    normalized_mode = (mode or "headless").strip().removeprefix("--")
    valid_modes = {"headless", "headless=new", "start-maximized", "normal"}
    if normalized_mode not in valid_modes:
        raise ValueError(f"Modo de Chrome no válido: {mode!r}")

    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")

    if normalized_mode in {"headless", "headless=new"}:
        options.add_argument("--headless=new")
    elif normalized_mode == "start-maximized":
        options.add_argument("--start-maximized")

    if options_configurations.get("no_sandbox", False):
        options.add_argument("--no-sandbox")
    if options_configurations.get("disable_dev_shm_usage", False):
        options.add_argument("--disable-dev-shm-usage")

    prefs: dict[str, Any] = {
        "translate.enabled": False,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }

    if options_configurations.get("disable_images", True):
        prefs["profile.managed_default_content_settings.images"] = 2

    download_folder = options_configurations.get("asset_download_folder")
    if download_folder:
        download_directory = Path(download_folder).expanduser().resolve()
        download_directory.mkdir(parents=True, exist_ok=True)
        prefs["download.default_directory"] = str(download_directory)

    options.add_experimental_option("prefs", prefs)

    user_agent = options_configurations.get("user_agent")
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")

    chromedriver_path = options_configurations.get("chromedriver_path")
    if chromedriver_path:
        driver_path = Path(chromedriver_path).expanduser().resolve()
        if not driver_path.is_file():
            raise FileNotFoundError(f"No se encontró ChromeDriver: {driver_path}")
        service = Service(executable_path=str(driver_path))
    else:
        service = Service()

    try:
        return webdriver.Chrome(service=service, options=options)
    except WebDriverException:
        logger.exception("No se pudo inicializar ChromeDriver.")
        raise
