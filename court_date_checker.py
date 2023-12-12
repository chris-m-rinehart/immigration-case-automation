from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

def submit_a_number(driver, client_a_number):
    url = 'https://acis.eoir.justice.gov/en/'

    # Ensure client_a_number is a string and has the correct length
    client_a_number = str(client_a_number)
    if len(client_a_number) != 9:
        raise ValueError("A-Number must be 9 digits long")

    try:
        # Open the website
        driver.get(url)
        time.sleep(.5)

        try:
            accept_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'I Accept')]"))
            )
            if accept_button:
                accept_button.click()
        except Exception as e:
            print(f"Accept button not found. Continuing without clicking.")
            # If the pop-up doesn't exist or there's an error, continue
            pass

        digits = list(client_a_number)
        
        # Find and interact with the input fields using WebDriverWait
        for i, digit in enumerate(digits):
            input_id = f"3e9af2d5-6fd2-44bf-9391-f86e83d609c4-{i}"
            input_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, input_id))
            )
            input_field.send_keys(digit)
            time.sleep(.3)

        # Submit the form    
        submit_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, 'btn_submit'))
        )
        submit_button.click()

        # Wait for the redirection to the new URL (adjust the timeout as needed)
        WebDriverWait(driver, 15).until(
            EC.url_to_be('https://acis.eoir.justice.gov/en/caseInformation')
        )
        return driver
    except Exception as e:
        print(f"An error occurred during submission: {traceback.print_exc()}")
        return None

def get_relevant_info(driver, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Check for the first class
    first_class_content = soup.find_all(class_="bg-white-actual px-3 py-4 text-center")
    if first_class_content:
        # Process and return something specific for the first class
        return process_info(driver, first_class_content)

    # Return a default value or handle the case when neither class is found
    return "No relevant information found"

def process_info(driver, content):

    try:
        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all strong tags in the page
        strong_tags = soup.find_all('strong')
        span_tags = soup.find_all('span')

        time.sleep(1.2)

        # Extract date and time from the strong tags
        # (Modify the indices according to where the date and time are actually found)

        name_text = span_tags[5].get_text() if len(span_tags) > 5 else "Name not found"
        appeal_text = span_tags[6].get_text() if len(span_tags) > 6 else "No appeal was received for this case"
        address_text = span_tags[7].get_text() if len(span_tags) > 7 else "Address not found"
        state_and_zip_text = span_tags[8].get_text() if len(span_tags) > 8 else "State and Zip not found"

        date_text = strong_tags[3].get_text() if len(strong_tags) > 3 else "There are no future hearings for this case."
        time_text = strong_tags[4].get_text() if len(strong_tags) > 4 else ""

        return {
            "client_name": f"{name_text}",
            "court_date": f"{date_text} at {time_text}",
            "address_name": f"{address_text} - {state_and_zip_text}",
            "appeal_info": f"{appeal_text}"
        }
    except Exception as e:
        print(f"An error occurred while retrieving court information: {e}")
        return None

#MAIN CLASS
def main():
    clients = []
    results = []

    print('Please enter client "A-Numbers"(no symbols, just nine digits). Enter "done" when done, or quit to terminate: ')
    while True:
        a_number = input('Enter "A-Number": ')
        if a_number.lower() == 'done':
            break  # Exit the loop if the user enters 'quit'
        if a_number.lower() == 'quit':
            return "Succesfully exited"
        clients.append(a_number)  # Append the entered "A-Number" to the clients list

    chrome_options = webdriver.ChromeOptions()

    chrome_profile_path = r"C:\Users\Chris Rinehart\AppData\Local\Google\Chrome\User Data"
    chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")
    chrome_options.add_argument('profile-directory=Profile 4')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument('--user-agent=Penelope_Gene')

    chrome_service = Service(ChromeDriverManager().install())
    # Initialize the WebDriver with the Chrome options
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    with driver:
        for client in clients:
            try:
                driver = submit_a_number(driver, client)
           
                if driver:
                    # Get the page source from the driver
                    html_content = driver.page_source
                    # Pass both driver and html_content to the get_relevant_info function
                    result = get_relevant_info(driver, html_content)
                    if result:
                        results.append(result)
                    else:
                        print(f"Failed to retrieve data for {client}")
                else:
                    print(f"Failed to submit data for {client}")

            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    # Print all results at the end
    for result in results:
        print(f"*********************************************\n")
        print(f"\nName and A-Number: {result['client_name']},\nCourt Date: {result['court_date']}\nAddress: {result['address_name']}\nAppeal status: {result['appeal_info']}\n")

if __name__ == "__main__":
    main()
