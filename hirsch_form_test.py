from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select,WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import logging
import test_data
import os 

logging.basicConfig(
    filename="automation.log",
    level=logging.INFO,
    format=f"%(asctime)s - %(levelname)s - %(message)s"
)

def fill_form():
    options = Options()
    download_dir = os.path.join(os.getcwd(), "pdf_output")
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    prefs = {
    # for PRINT Save as PDF 
    "printing.print_preview_sticky_settings.appState":
        '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],'
        '"selectedDestinationId":"Save as PDF","version":2}',

    "savefile.default_directory": download_dir,

    # HYPERLINK PDF download 
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}

    options.add_experimental_option("prefs", prefs)
    options.add_argument("--kiosk-printing")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    logging.info("Launching browser")
    driver.get("https://hirschqa.azurewebsites.net/training/")
    wait = WebDriverWait(driver, 5)

    title = driver.title
    try:
        assert "Training Form" in title
        logging.info("Title test passed")
    except AssertionError:
        logging.error("Title test failed")

    fill_contact(driver)
    
    #fill_institution(driver)
    submit_form(driver)
    #download_logo_pdf(driver, download_dir)  
    #click_footer_link(driver)
    

    

def fill_contact(driver):
    driver.find_element(By.ID, "Name").send_keys(test_data.name)

    driver.find_element(By.ID, "email").send_keys(test_data.email)

    # PHONE NUMBER (NEGATIVE TEST)
    phone_input = driver.find_element(By.ID, "phone")
    phone_input.send_keys(test_data.phone)

    

    gender_radio = driver.find_element(By.ID, "gender2")
    driver.execute_script("arguments[0].click();", gender_radio)

    driver.find_element(By.ID, "dob").send_keys(test_data.dob)

    state = driver.find_element(By.ID, "state")
    Select(state).select_by_visible_text(test_data.state)

    


def fill_institution(driver):
    # Degree
    education_group = driver.find_element(By.TAG_NAME, "table")
    input_collection = education_group.find_elements(By.TAG_NAME, "input")
    #print(len(input_collection))

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

def download_logo_pdf(driver, download_dir):
    logging.info("Attempting to download logo PDF")

    logo_link = driver.find_element( By.XPATH, "//a[img[contains(@alt, 'Logo')]]")

    logo_link.click()

    # Wait for download
    sleep(4)

    pdfs = [f for f in os.listdir(download_dir) if f.endswith(".pdf")]

    assert len(pdfs) > 0, "Logo PDF was not downloaded"
    logging.info(f"Logo PDF downloaded successfully: {pdfs}")

def click_footer_link(driver):
    main_window = driver.current_window_handle

    footer_link = driver.find_element(By.LINK_TEXT, "Hirsch Secure")
    footer_link.click()

    # Wait for new tab
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Switch to new tab
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            break

    logging.info("Switched to footer link tab")

    try:

        footer_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Contact")))
        driver.execute_script("arguments[0].click();", footer_element)

        logging.info("Footer page loaded successfully - Contact link clicked")

    except Exception as e:
        logging.error("Footer page element validation FAILED")
        logging.error(str(e))
        raise AssertionError("Footer link page did not load correctly")
    
    finally:
        driver.close()
        driver.switch_to.window(main_window)
        logging.info("Closed tab and switched back to main tab")


    





def submit_form(driver):
    
    phone_input = driver.find_element(By.ID, "phone")

    submit_button = driver.find_element(
        By.XPATH, "//input[@type='button' and @value='Submit']"
    )
    sleep(2)

    driver.execute_script("arguments[0].click();", submit_button)

    
    is_phone_valid = driver.execute_script(
        "return arguments[0].validity.valid;", phone_input
    )
    sleep(2)

    if not is_phone_valid:
        logging.error("Form submission blocked due to invalid phone number")
        raise AssertionError("Invalid phone number - form not submitted")

    logging.info("Form submitted successfully")


