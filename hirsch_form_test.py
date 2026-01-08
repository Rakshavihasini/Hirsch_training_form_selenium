from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import test_data
import os 

def fill_form():
    options = Options()
    download_dir = os.path.join(os.getcwd(), "pdf_output")
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    prefs = {
        "printing.print_preview_sticky_settings.appState":
            '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],'
            '"selectedDestinationId":"Save as PDF","version":2}',
        "savefile.default_directory": download_dir
    }

    options.add_experimental_option("prefs", prefs)
    options.add_argument("--kiosk-printing")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://hirschqa.azurewebsites.net/training/")
    wait = WebDriverWait(driver, 5)

    title = driver.title
    try:
        assert "Training Form" in title
        print("Title test passed")
    except AssertionError:
        print("Title test failed")

    fill_contact(driver)
    fill_institution(driver)
    submit_form(driver)
    


def fill_contact(driver):

    driver.find_element(By.ID,"Name").send_keys(test_data.name)
    sleep(1)
    driver.find_element(By.ID, "email").send_keys(test_data.email)
    sleep(1)
    driver.find_element(By.ID, "phone").send_keys(test_data.phone)
    sleep(1)
    gender_radio = driver.find_element(By.ID, "gender2")
    driver.execute_script("arguments[0].click();", gender_radio)

    driver.find_element(By.ID, "dob").send_keys(test_data.dob)

    state = driver.find_element(By.ID, "state") 
    state_dropdown = Select(state)
    state_dropdown.select_by_visible_text(test_data.state)
    



def fill_institution(driver):
    # Degree
    education_group = driver.find_element(By.TAG_NAME, "table")
    input_collection = education_group.find_elements(By.TAG_NAME, "input")
    print(len(input_collection))

    input_collection[0].send_keys("SRM")
    sleep(1)


    input_collection[1].send_keys("85")
    sleep(1)

    # Higher Secondary

    input_collection[2].send_keys("KV")

    input_collection[3].send_keys("91")

    
    print("Institution filling completed")

    lang_checkbox = driver.find_element(By.ID, "lang1")
    driver.execute_script("arguments[0].click();", lang_checkbox)
    sleep(2)


def submit_form(driver):
    submit_button = driver.find_element(By.XPATH, "//input[@type='button' and @value='Submit']")
    driver.execute_script("arguments[0].click();", submit_button)

