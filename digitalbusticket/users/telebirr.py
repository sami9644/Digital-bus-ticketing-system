from telebirr import Telebirr
def requestpayment():
    private_key = "YOUR PUBLIC KEY FORM TELEBIRR ADMIN"
    telebirr = Telebirr(
        app_id="YOUR APP ID FROM TELEBIRR ADMIN",
        app_key="YOUR APP KEY FROM TELEBIRR ADMIN",
        public_key=private_key,
        notify_url="https://example.com/telebirr/121232",
        receive_name="Your company name",
        return_url="https://example.com/",
        short_code="SHORT CODE FROM TELEBIRR ADMIN",
        subject="Test",
        timeout_express="30",
        total_amount="10",
        nonce="UNIQUE",
        out_trade_no="UNIQUE"
    )
    response = telebirr.send_request()

def getres():
    public_key = "YOUR PUBLIC KEY FORM TELEBIRR ADMIN"
    payload = "Payload coming from telebirr" # If you are using django it means request.body

    decrypted_data = Telebirr.decrypt(public_key=public_key, payload=payload)
    return decrypted_data
   