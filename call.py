import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def make_api_call(index):
    try:
        response = requests.post('https://nz03.com/')
        return response.text
    except Exception as e:
        print(f"Error in request {index}: {str(e)}")
        return None

def run_concurrent_calls():
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=1000) as executor:
        # Submit 1000 API calls
        futures = [executor.submit(make_api_call, i) for i in range(2000)]
        
        # Get results
        results = [future.result() for future in futures]
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.2f} seconds")
    
    # Count successful calls
    successful = len([r for r in results if r is not None])
    print(f"Successful calls: {successful}/1000")

if __name__ == "__main__":
    run_concurrent_calls()

