import requests
import time
import webbrowser

# Use your key that starts with CHASECK_TEST-
CHASECK_TEST = 'CHASECK_TEST-rR3oj56cDtlEKEFNk9jUVK4wTAKZUuo3'

def initialize_payment(amount, email, tx_ref,callback_url,return_url):
    """Step 1: Get the checkout URL for the user"""
    url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {'Authorization': f'Bearer {CHASECK_TEST}'}
    
    payload = {
        'amount': str(amount),
        'currency': 'ETB',
        'email': email,
        'tx_ref': tx_ref,
        'callback_url': callback_url, # Replace with your URL
        'return_url': return_url,   # Replace with your URL
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()['data']['checkout_url']

def verify_payment(tx_ref):
    """Step 2: Check if the payment was actually successful"""
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {'Authorization': f'Bearer {CHASECK_TEST}'}
    
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Check if the status is 'success' according to Chapa's API
    if data.get('status') == 'success' and data.get('data', {}).get('status') == 'success':
        return True
    return False

# --- Testing the Flow ---

# 1. Create a unique reference
my_tx_ref = f"order-{int(time.time())}" 

# 2. Start the payment
# init_res = initialize_payment(100, "customer@mail.com", my_tx_ref)

# if init_res.get('status') == 'success':
#     print(f"Please pay here: {init_res['data']['checkout_url']}")
#     webbrowser.open(init_res['data']['checkout_url'])
#     # 3. In a real app, you wait for the user to finish. 
#     # For this test, we'll wait 20 seconds then check.
#     print("Waiting 20 seconds for you to simulate a payment...")
#     time.sleep(20) 
    
#     is_paid = verify_payment(my_tx_ref)
    
#     if is_paid:
#         print("✅ Status: True (Payment Successful)")
#     else:
#         print("❌ Status: False (Payment Not Completed)")
# else:
#     print(f"Error initializing: {init_res.get('message')}")