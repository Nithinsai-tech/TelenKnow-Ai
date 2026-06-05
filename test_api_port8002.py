import requests
import json
import time

def test_query():
    base_url = "http://localhost:8002"
    
    # 1. Trigger Indexing
    print("Triggering document indexing on port 8002...")
    try:
        response = requests.post(f"{base_url}/index-sample-docs")
        print(f"Index status: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Indexing error: {e}")
        return

    # Give it a moment to settle
    time.sleep(2)
    
    # 2. Test queries
    queries = [
        "What is the target MTTR for Enterprise Fiber?",
        "What is the maximum power consumption of a 5G base station?"
    ]
    
    headers = {"Content-Type": "application/json"}
    
    for query in queries:
        print(f"\n--- Testing Query: {query} ---")
        payload = {"question": query}
        try:
            response = requests.post(f"{base_url}/query", json=payload, headers=headers)
            if response.status_code == 200:
                print("Answer:")
                print(response.json().get("answer", "No answer found."))
                print("Sources:")
                print(response.json().get("sources", []))
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    test_query()
