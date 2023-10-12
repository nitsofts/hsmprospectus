from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def scrape_sebon_data(page_numbers):
    combined_data = []

    for page_number in page_numbers:
        # Define the URL for the given page
        url = f"https://www.sebon.gov.np/prospectus?page={page_number}"

        # Send a GET request to the URL
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table containing the prospectus data
            table = soup.find('table', class_='table')

            # Find all table rows (tr) within the table body (tbody)
            table_rows = table.select('tbody tr')

            # Initialize an empty list to store the data for this page
            data_list = []

            # Iterate through the table rows and extract data for each row
            for row in table_rows:
                row_data = row.find_all('td')
                if len(row_data) == 4:  # Check if the row has four columns
                    data = {
                        "Title": row_data[0].get_text(strip=True),
                        "Date": row_data[1].get_text(strip=True),
                        "English": row_data[2].find('a').get('href', '') if row_data[2].find('a') else '',
                        "Nepali": row_data[3].find('a').get('href', '') if row_data[3].find('a') else ''
                    }
                    data_list.append(data)

            combined_data.extend(data_list)
        else:
            print(f"Failed to retrieve page {page_number}. Status code:", response.status_code)

    return combined_data

@app.route('/get_prospectus/<page_numbers>', methods=['GET'])
def get_prospectus(page_numbers):
    # Split the comma-separated page numbers into a list
    page_numbers = [int(page) for page in page_numbers.split(',')]

    # Fetch data for the specified page numbers
    data = scrape_sebon_data(page_numbers)

    # Convert the data to JSON
    json_data = json.dumps(data, indent=None)

    return jsonify(json_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
