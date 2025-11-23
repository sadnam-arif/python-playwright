import time
import urllib.parse
import requests
import pytest

BASE_URL = "https://automationexercise.com/api/createAccount"


def generate_unique_email():
    return f"user_{int(time.time())}@test.com"


def build_payload(email):
    payload = {
        "name": "Test API User",
        "email": email,
        "password": "Test@12345",
        "title": "Mr",
        "birth_date": "15",
        "birth_month": "01",
        "birth_year": "1992",
        "firstname": "Test",
        "lastname": "User2",
        "company": "Test company 2",
        "address1": "123 Mohammadpur",
        "address2": "Road 7",
        "country": "Bangladesh",
        "zipcode": "123456",
        "state": "California",
        "city": "Dhaka",
        "mobile_number": "1234567890"
    }

    return urllib.parse.urlencode(payload)


def test_api_user_registration():
    email = generate_unique_email()
    encoded_payload = build_payload(email)

    response_1 = requests.post(
        BASE_URL,
        data=encoded_payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response_1.status_code == 201, \
        f"Expected 201, got {response_1.status_code}"

    json_res_1 = response_1.json()
    assert json_res_1.get("message") == "User created!", \
        f"Expected 'User created!', got {json_res_1}"

    print("User created successfully:", json_res_1)


  
    # Try creating again with same email (expect 400)
  
    response_2 = requests.post(
        BASE_URL,
        data=encoded_payload,  
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response_2.status_code == 400, \
        f"Expected 400, got {response_2.status_code}"

    json_res_2 = response_2.json()
    assert "Email already exists" in json_res_2.get("message", ""), \
        f"Expected 'Email already exists', got {json_res_2}"

    print("Duplicate registration rejected:", json_res_2)
