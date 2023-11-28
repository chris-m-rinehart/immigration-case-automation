import requests
from bs4 import BeautifulSoup

def submit_a_number(session, client_a_number):
    url = 'https://acis.eoir.justice.gov/en/'

    # Ensure client_a_number is a string and has the correct length
    client_a_number = str(client_a_number)
    if len(client_a_number) != 9:
        raise ValueError("A-Number must be 9 digits long")

    # Splitting the A-Number into individual digits
    digits = list(client_a_number)

    # Constructing data payload for the POST request
    data = {}
    for i, digit in enumerate(digits):
        input_id = f"3e9af2d5-6fd2-44bf-9391-f86e83d609c4-{i}"
        data[input_id] = digit

    # Sending a POST request to the URL with the constructed data payload
    response = session.post(url, data=data)
    return response



def get_court_date_info(session):
    url = 'https://acis.eoir.justice.gov/en/caseInformation'
    response = session.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Searching for the first 'section' element in the HTML
        # This is where the court information is assumed to be present
        court_info_section = soup.find('section')
        return court_info_section.get_text().strip() if court_info_section else "Court date not found"
    else:
        return "Failed to retrieve data"

def main():
    # Initialize an empty list to store client "A-Numbers"
    clients = []

    # Prompt the user to enter "A-Numbers" and quit when done
    print('Please enter client "A-Numbers". Enter "quit" when done:')
    while True:
        a_number = input('Enter "A-Number": ')
        if a_number.lower() == 'quit':
            break  # Exit the loop if user enters 'quit'
        clients.append(a_number)  # Append the entered "A-Number" to the clients list

    # Create a session object from requests library to persist session across HTTP requests
    with requests.Session() as session:
        for client in clients:
            try:
                # Attempt to submit the client's "A-Number" using the submit_a_number function
                submit_response = submit_a_number(session, client)

                # Check if the submission was successful (HTTP status code 200)
                if submit_response.status_code == 200:
                    # Retrieve court date information using the get_court_date_info function
                    result = get_court_date_info(session)
                    print(f"Court date for {client}: {result}")
                else:
                    # If submission failed, print the status code for debugging
                    print(f"Failed to submit data for {client}: {submit_response.status_code}")
            except requests.exceptions.RequestException as e:
                # Handle network-related exceptions such as connection errors or timeouts
                print(f"Network error occurred: {e}")
            except Exception as e:
                # Handle any other unexpected exceptions
                print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
