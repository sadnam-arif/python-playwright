import json
import time
import urllib.parse
from pathlib import Path
from playwright.sync_api import sync_playwright

CREDENTIALS_FILE = Path("fixtures/user_credentials.json")

def test_create_new_user():
    timestamp = int(time.time())
    email = f"user_{timestamp}@test.com"
    password = "Test@1234"

    payload = {
        "name": "Test user1",
        "email": email,
        "password": password,
        "title": "Mr",
        "birth_date": "15",
        "birth_month": "01",
        "birth_year": "1992",
        "firstname": "Test",
        "lastname": "user1",
        "company": "Test Company",
        "address1": "123 mohammadpur",
        "address2": "road 7",
        "country": "Bangladesh",
        "zipcode": "12345",
        "state": "California",
        "city": "Dhaka",
        "mobile_number": "1234567890"
    }

    encoded_payload = urllib.parse.urlencode(payload)

    with sync_playwright() as p:
        request_context = p.request.new_context()

        response = request_context.post(
            "https://automationexercise.com/api/createAccount",
            data=encoded_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        print(response.status)
        print(response.json())

        assert response.status == 200, f"got {response.status}"
        json_response = response.json()

        assert json_response.get("message") == "User created!", \
            f"Unexpected API message: {json_response}"

    credentials = {"email": email, "password": password}
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_text(json.dumps(credentials, indent=4))

    return credentials
