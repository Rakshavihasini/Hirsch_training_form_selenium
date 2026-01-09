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
        logging.info(f"Title test passed: '{title}'")
    except AssertionError:
        logging.error(f"Title test failed: '{title}'")

    fill_contact(driver)
    fill_institution(driver)
    download_logo_pdf(driver, download_dir)  
    click_footer_link(driver)
    submit_form(driver)
    

    

def fill_contact(driver):
    logging.info(f"Filling contact info: name- {test_data.name} , email- {test_data.email} , phone number-{test_data.phone}, dob-{test_data.dob}")
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
    logging.info("Filling education info")
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

    
    

    lang_checkbox = driver.find_element(By.ID, "lang1")
    driver.execute_script("arguments[0].click();", lang_checkbox)
    

def download_logo_pdf(driver, download_dir):
    logging.info("Attempting to download logo PDF")

    logo_link = driver.find_element( By.XPATH, "//a[img[contains(@alt, 'Logo')]]")

    logo_link.click()

    # Wait for download
    sleep(4)

    pdfs = [f for f in os.listdir(download_dir) if f.endswith(".pdf")]

    assert len(pdfs) > 0, "Logo PDF was not downloaded"
    logging.info(f"PDF downloaded successfully: {pdfs}")

def click_footer_link(driver):
    # Store parent tab
    parent_window = driver.current_window_handle

    # Open footer link 3 times
    footer_links = []
    for i in range(3):
        #  switch back to parent window to find the footer link
        driver.switch_to.window(parent_window)

        # Store existing windows BEFORE click
        existing_windows = set(driver.window_handles)

        footer_link = driver.find_element(By.LINK_TEXT, "Hirsch Secure")
        footer_link.click()
        logging.info(f"Opened footer link {i+1}")

        # Wait until a NEW window appears
        WebDriverWait(driver, 10).until(
            lambda d: len(d.window_handles) > len(existing_windows)
        )

        # Identify the NEW tab
        new_window = list(set(driver.window_handles) - existing_windows)[0]
        footer_links.append(new_window)

        # Switch to NEW tab
        driver.switch_to.window(new_window)
        logging.info(f"Switched to footer link tab {i+1}")

        try:
            footer_element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Contact"))
            )
            logging.info(f"Footer page {i+1} loaded successfully - Contact link is accessible and clickable")

        except Exception as e:
            logging.error(f"Footer page {i+1} element validation FAILED")
            logging.error(str(e))
            raise AssertionError(f"Footer link page {i+1} did not load correctly - Contact link not accessible")

        sleep(2)

    # Close the last opened link (3rd tab)
    driver.switch_to.window(footer_links[2])
    driver.close()
    logging.info("Closed the last opened footer tab")
    sleep(2)

    # Switch back to ORIGINAL parent tab
    driver.switch_to.window(parent_window)
    logging.info("Switched back to main tab")

    

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

    if not is_phone_valid:
        logging.error("Form submission blocked due to invalid phone number")
        raise AssertionError("Invalid phone number - form not submitted")

    logging.info("Form submitted successfully")


