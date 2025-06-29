import requests
from app import create_app

class Paystack:
    def __init__(self):
        self.app = create_app()
        self.secret_key = self.app.config["PAYSTACK_SECRET_KEY"]
        self.base_url = "https://api.paystack.co"

    def initiate_payment(self, email, amount, reference, callback_url):
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        data = {
            "email": email,
            "amount": int(amount * 100),  # Convert to kobo
            "reference": reference,
            "callback_url": callback_url
        }
        try:
            response = requests.post(f"{self.base_url}/transaction/initialize", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Paystack error: {str(e)}")

    def verify_payment(self, reference):
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        try:
            response = requests.get(f"{self.base_url}/transaction/verify/{reference}", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Paystack error: {str(e)}")