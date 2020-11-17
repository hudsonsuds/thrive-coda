import requests

from sensitive_info import coda_api_token
from sensitive_info import thrive_headers


def create_bio(companies_object):
    company_list = []

    for company in companies_object:
        company_list.append(company['name'])
    company_list = set(company_list)

    bulleted_list = ""

    for company in company_list:
        bulleted_list = bulleted_list + company + '\n'

    return (bulleted_list)


def get_thrive_data():
    # Get Thrive data
    thrive_url = "https://[instance].thrivetrm.com/api/v1/searches/[search #]/candidacies"
    thrive_payload = {}

    print("Retrieving Thrive data...")
    thrive_response = requests.request("GET", thrive_url, headers=thrive_headers, data=thrive_payload)
    return (thrive_response)


def upload_to_coda(thrive_response):
    # Upload to Coda

    coda_headers = {'Authorization': 'Bearer %s' % coda_api_token}
    coda_uri = 'https://coda.io/apis/v1/docs/[doc_id]/tables/[table_id]/rows'

    rows = []

    data = thrive_response.json()["candidacies"]

    for idx, row in enumerate(data):

        contact = row["contact"]

        rows.append({
            'cells': [
                {
                    'column': '[column_id]',
                    'value': contact["full_name"] or ""
                },  # Name
                {
                    'column': '[column_id]',
                    'value': contact["primary_company_name"] or ""
                },  # Current company
                {
                    'column': '[column_id]',
                    'value': row["candidacy_stage"]["name"] or ""
                },  # Thrive stage
                {
                    'column': '[column_id]',
                    'value': contact["linkedin_url"] or ""
                },  # LinkedIn
                {
                    'column': '[column_id]',
                    'value': contact["location"] or ""
                },  # Location
                {
                    'column': '[column_id]',
                    'value': contact["avatar_url"] or ""
                },  # Avatar URL
                {
                    'column': '[column_id]',
                    'value': contact["primary_title"] or ""
                },  # Current Title
                {
                    'column': '[column_id]',
                    'value': row['id'] or ""
                },  # Thrive ID
                {
                    'column': '[column_id]',
                    'value': create_bio(contact["companies"]) or ""
                },  # Bio
                {
                    'column': '[column_id]',
                    'value': row["rejection_reason"] or ""
                },  # Rejection reason
            ],
        })

    coda_payload = {'rows': rows, 'keyColumns': ['[column_id]']}

    print("Uploading to Coda...")
    req = requests.post(coda_uri, headers=coda_headers, json=coda_payload)
    req.raise_for_status()  # Throw if there was an error.
    res = req.json()

    print('Upserted %s rows' % len(rows))


## Main
thrive_data = get_thrive_data()
upload_to_coda(thrive_data)
