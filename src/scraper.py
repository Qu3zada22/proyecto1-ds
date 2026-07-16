from io import StringIO

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


URL = "https://www.mineduc.gob.gt/BUSCAESTABLECIMIENTO_GE/wbfBuscar.aspx"


def iniciar_driver():
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    driver.maximize_window()
    driver.get(URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.NAME, "_ctl0:ContentPlaceHolder1:cmbDepartamento")
        )
    )

    return driver


def seleccionar_departamento(driver, codigo):

    departamento = Select(
        driver.find_element(
            By.NAME,
            "_ctl0:ContentPlaceHolder1:cmbDepartamento"
        )
    )

    departamento.select_by_value(codigo)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.NAME, "_ctl0:ContentPlaceHolder1:cmbDepartamento")
        )
    )


def seleccionar_nivel(driver):

    nivel = Select(
        driver.find_element(
            By.NAME,
            "_ctl0:ContentPlaceHolder1:cmbNivel"
        )
    )

    nivel.select_by_value("46")   # Diversificado

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.NAME, "_ctl0:ContentPlaceHolder1:cmbNivel")
        )
    )


def buscar(driver):

    boton = driver.find_element(
        By.NAME,
        "_ctl0:ContentPlaceHolder1:IbtnConsultar"
    )

    boton.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.ID,
                "_ctl0_ContentPlaceHolder1_dgResultado"
            )
        )
    )


def obtener_dataframe(driver):

    html = driver.page_source

    tablas = pd.read_html(StringIO(html))

    df = tablas[9].copy()

    # Primera fila = encabezados
    df.columns = df.iloc[0]

    # Eliminar fila de encabezados
    df = df.iloc[1:].reset_index(drop=True)

    # Eliminar columna vacía
    df = df.loc[:, df.columns.notna()]

    # Eliminar filas completamente vacías
    df = df.dropna(how="all")

    return df


def obtener_departamento(driver, codigo_departamento):

    seleccionar_departamento(driver, codigo_departamento)

    seleccionar_nivel(driver)

    buscar(driver)

    return obtener_dataframe(driver)