from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import os
import time
import pandas as pd
import PyPDF2


def set_prefs():
    """Set preferences to Chrome driver.

    Returns
    -------
    df : dict
         drive preferences.
    """
    chrome_options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': os.path.abspath(os.curdir).replace('\\src', '\\data')}
    chrome_options.add_experimental_option('prefs', prefs)
    return chrome_options


def start_browser(chrome_options):
    """Start browser in a specific page.

    Parameters
    ----------
    chrome_options : dict
                     Dictionary with the driver preferences.

    Returns
    -------
    driver : object
             Browser initialized.
    """
    DRIVER_PATH = '../drivers/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=chrome_options)
    driver.get('https://simpleenergy.com.br/teste/')
    return driver


def send_keys(driver, code):
    """Insert a key value in a text box (input).

    Parameters
    ----------
    driver : object
             Browser initialized.

    code : str
           Key value.
    """
    inputElement = driver.find_element_by_id("codigo")
    inputElement.send_keys(code)
    inputElement.submit()


def confirm_click(driver, xpath):
    """Click according to specific XPath.

    Parameters
    ----------
    driver : object
             Browser initialized.

    xpath : str
            Button path.
    """
    confirm = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    confirm.click()


def wait_file_download(file_path):
    """Wait a specific file download.

    Parameters
    ----------
    file_path : str
                Path of the file being downloaded.
    """
    while not os.path.exists(file_path):
        time.sleep(1)


def selection_data(driver, code):
    """Download all the necessary files, specifying the Xpath of each one.

    Parameters
    ----------
    driver : object
             Browser initialized.

    code : str
           Key value.
    """
    list_tags = ['2|2|1|txt', '2|3|1|pdf', '3|2|2|txt', '3|3|2|pdf']

    for tag in list_tags:
        confirm_click(driver, f'/html/body/div[{tag.split("|")[0]}]/div[{tag.split("|")[1]}]/a')
        wait_file_download(f'../data/arquivo{tag.split("|")[2]}-{code}.{tag.split("|")[3]}')


def download_file(chrome_options, code):
    """Initializes the flow of functions needed to download the files.

    Parameters
    ----------
    chrome_options : dict
                     Dictionary with the driver preferences.

    code : str
           Key value.
    """
    driver = start_browser(chrome_options)
    send_keys(driver, code)
    selection_data(driver, code)
    driver.quit()


def list_files(extension):
    """List all files in data directory with a specific extension.

    Parameters
    ----------
    extension : str
                Files extension.

    Returns
    -------
    return : list
             Files name list.
    """
    return [f for f in os.listdir('../data') if f.endswith(extension)]


def read_txt_files(df):
    """Read content from all files listed and save it on dataframe.

    Parameters
    ----------
    df : pd.DataFrame
         Dataframe with the necessary structure to store and categorize the information.

    Returns
    -------
    df : pd.DataFrame
         Dataframe with the txts files content.
    """
    for file_name in list_files('.txt'):
        file = open(f'../data/{file_name}')
        content = file.read()
        file.close()

        df.loc[len(df)] = [file_name.split('-')[1].split('.')[0], file_name.split('-')[0], file_name.split('.')[1], content]

    return df


def read_pdf_files(df):
    """Read content from all files listed and save it on dataframe.

    Parameters
    ----------
    df : pd.DataFrame
         Dataframe with the necessary structure to store and categorize the information.

    Returns
    -------
    df : pd.DataFrame
         Dataframe with the pdfs files content.
    """
    for file_name in list_files('.pdf'):
        pdfFileObj = open(f'../data/{file_name}', 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        pageObj = pdfReader.getPage(0)
        content = pageObj.extractText()
        pdfFileObj.close()

        df.loc[len(df)] = [file_name.split('-')[1].split('.')[0], file_name.split('-')[0], file_name.split('.')[1], content]

    return df


def main():
    print(f"LOG: LOADING DRIVER SETTINGS")
    chrome_options = set_prefs()

    print(f"LOG: DOWNLOADING FILES")
    codes = ['98465', '321465']
    for code in codes:
        download_file(chrome_options, code)

    df = pd.DataFrame({'code': [], 'archive': [], 'source': [], 'content': []})
    print(f"LOG: READING TXT FILES")
    df = read_txt_files(df)

    print(f"LOG: READING PDF FILES")
    df = read_pdf_files(df)

    print(f"LOG: EXPORTING FINAL DATAFRAME")
    df.sort_values(['code', 'source']).to_excel('../simple-energy.xlsx')


if __name__ == '__main__':
    main()
