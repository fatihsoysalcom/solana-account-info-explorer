import http.client
import json
import sys

# --- Configuration ---
# Solana RPC endpoint (Devnet is used for demonstration)
RPC_HOST = "api.devnet.solana.com"
RPC_PORT = 443 # Default HTTPS port

# Public key of the account to query
# Example: Solana System Program ID (a well-known, always-present account)
TARGET_PUBLIC_KEY = "11111111111111111111111111111111"

# --- Main Logic ---
def get_solana_account_info(public_key: str):
    """
    Fetches Solana account information for a given public key using Python's http.client
    (standard library only, no external dependencies).
    """
    conn = None
    try:
        # Establish a secure HTTP connection to the Solana RPC endpoint
        conn = http.client.HTTPSConnection(RPC_HOST, RPC_PORT)

        # Construct the JSON RPC request payload for 'getAccountInfo'
        # This method allows querying details like lamports (balance), owner, executable status, and data.
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                public_key,
                {
                    "encoding": "base64" # Request account data in base64 format
                }
            ]
        }
        headers = {
            "Content-Type": "application/json"
        }

        # Send the POST request with the JSON payload
        conn.request("POST", "/", body=json.dumps(payload), headers=headers)

        # Get and decode the response
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')

        if response.status != 200:
            print(f"Error: RPC request failed with status {response.status}")
            print(f"Response: {response_data}")
            return None

        # Parse the JSON response
        parsed_response = json.loads(response_data)

        # Check for RPC errors within the response payload
        if 'error' in parsed_response:
            print(f"RPC Error: {parsed_response['error']['message']}")
            return None

        # Extract the account information from the 'result' field
        result = parsed_response.get('result', {}).get('value')

        if result is None:
            print(f"Account '{public_key}' not found or no information available.")
            return None

        return result

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return None
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print(f"Connecting to Solana Devnet RPC: {RPC_HOST}")
    print(f"Querying account: {TARGET_PUBLIC_KEY}\n")

    account_info = get_solana_account_info(TARGET_PUBLIC_KEY)

    if account_info:
        # Display the retrieved account information, simulating an account explorer
        print("--- Account Information ---")
        print(f"Public Key: {TARGET_PUBLIC_KEY}")
        print(f"Balance (Lamports): {account_info.get('lamports', 'N/A')}")
        # Convert lamports to SOL (1 SOL = 1,000,000,000 lamports)
        sol_balance = account_info.get('lamports', 0) / 1_000_000_000
        print(f"Balance (SOL): {sol_balance:.9f}")
        print(f"Owner Program: {account_info.get('owner', 'N/A')}")
        print(f"Executable: {account_info.get('executable', 'N/A')}")
        
        # The 'data' field contains the raw account data. We'll show its length.
        data = account_info.get('data')
        if data and isinstance(data, list) and len(data) > 0:
            # 'data' is typically [base64_string, encoding_type]
            print(f"Data Size (bytes): {len(data[0]) if data[0] else 0} (base64 encoded length)")
        else:
            print("Data Size (bytes): 0")
        
        print(f"Rent Epoch: {account_info.get('rentEpoch', 'N/A')}")
    else:
        print("Failed to retrieve account information.")
