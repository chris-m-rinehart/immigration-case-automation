from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def submit_a_number(driver, client_a_number):
    url = 'https://acis.eoir.justice.gov/en/'

    # Ensure client_a_number is a string and has the correct length
    client_a_number = str(client_a_number)
    if len(client_a_number) != 9:
        raise ValueError("A-Number must be 9 digits long")

    try:
        # Open the website
        driver.get(url)

        time.sleep(7)

        try:
            accept_button = WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I Accept')]"))
            )
            accept_button.click()
        except Exception as e:
            printf(f"An error occurred when trying to click the accept buitton: {e} ")
            # If the pop-up doesn't exist or there's an error, continue
            pass

        digits = list(client_a_number)

        # Find and interact with the input fields using WebDriverWait
        for i, digit in enumerate(digits):
            input_id = f"3e9af2d5-6fd2-44bf-9391-f86e83d609c4-{i}"
            input_field = WebDriverWait(driver, 100).until(
                EC.presence_of_element_located((By.ID, input_id))
            )
            input_field.send_keys(digit)

        # Submit the form     
        submit_button = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.ID, 'btn_submit'))
        )
        submit_button.click()

        # Wait for the redirection to the new URL (adjust the timeout as needed)
        WebDriverWait(driver, 50).until(
            EC.url_to_be('https://acis.eoir.justice.gov/en/caseInformation')
        )

        return driver

    except Exception as e:
        print(f"An error occurred during submission: {e}")
        return None

def get_court_date_info(driver):
    try:
        # Wait for the court information to load
        # This locator assumes that 'Hearing' is a unique word preceding the date
        hearing_info_element = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'hearing')]"))
        )

        # Extract the text, which is expected to be the hearing date
        # The following sibling should contain the date based on the structure seen in the screenshot
        court_date_element = hearing_info_element.find_element_by_xpath('./following-sibling::strong')
        court_date_text = court_date_element.text

        return court_date_text.strip() if court_date_text else "Court date not found"

    except Exception as e:
        print(f"An error occurred while retrieving court information: {e}")
        return "Failed to retrieve data"




def main():

    clients = []

    print('Please enter client "A-Numbers"(no symbols, just nine digits). Enter "done" when done:')
    while True:
        a_number = input('Enter "A-Number": ')
        if a_number.lower() == 'done':
            break  # Exit the loop if the user enters 'quit'
        clients.append(a_number)  # Append the entered "A-Number" to the clients list

    chrome_options = Options()
    user_agent = "Penelope Cerrundolo"
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the WebDriver with the Chrome options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


    with driver:
        for client in clients:
            try:
                # Attempt to submit the client's "A-Number" using the submit_a_number function
                driver = submit_a_number(driver, client)

                if driver:
                    # At this point, you are on the new URL where the court date info is present
                    # Retrieve court date information using the get_court_date_info function
                    result = get_court_date_info(driver)
                    print(f"Court date for {client}: {result}")
                else:
                    print(f"Failed to submit data for {client}")

            except Exception as e:
                print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
