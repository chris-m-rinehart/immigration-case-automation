import requests
from bs4 import BeautifulSoup

def submit_a_number(session, client_a_number):
    url = 'https://acis.eoir.justice.gov/en/'

    # Splitting the A-Number into individual digits
    digits = list(client_a_number)
    
    # Constructing data payload for the POST request
    data = {}
    for i, digit in enumerate(digits):
        input_id = f"3e9af2d5-6fd2-44bf-9391-f86e83d609c4-{i}"
        data[input_id] = digit

    response = session.post(url, data=data)
    return response

def get_court_date_info(session):
    url = 'https://acis.eoir.justice.gov/en/caseInformation'
    response = session.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        court_info_section = soup.find('section')
        return court_info_section.get_text().strip() if court_info_section else "Court date not found"
    else:
        return "Failed to retrieve data"

def main():
    clients = []

    print('Please enter client "A-Numbers". Enter "quit" when done:')
    while True:
        a_number = input('Enter "A-Number": ')
        if a_number.lower() == 'quit':
            break
        clients.append(a_number)

    with requests.Session() as session:
        for client in clients:
            submit_response = submit_a_number(session, client)
            if submit_response.status_code == 200:
                result = get_court_date_info(session)
                print(f"Court date for {client}: {result}")
            else:
                print(f"Failed to submit data for {client}")

if __name__ == "__main__":
    main()
