import requests

# Replace with access token after running spotifyHarmonize.py...
access_token = "BQAosCZC1y-Q5wHx11Bzewjtz09WYopBzFDu8yEJkFzrHZz0b42krp0pAQNMrOOvOigg-zUoFkJ_GnhJIy5nhG1LuxDpziHrILXIYC4_p2Y27SatAVgri2si2BZjVvNZS-NIqCwaFKtXnNIQEW6B8tDemWAIJdBZFRKVwlBWZnu6ccSLXSR_UoGxVWMkK8f4lsAf-mPvGJeJT5JOb3Rc1v-Y8hbn1HJBVKfr29Y70gzKTWzeJz0Ttm6rMNnUSVEzX8K7WjveOrIxseZBPwz9PA"

url = "https://api.spotify.com/v1/recommendations"
headers = {
    "Authorization": f"Bearer {access_token}"
}
params = {
    "seed_tracks": "6KB2OPefadupVDnVNYq23A",  # Replace with actual seed track ID
    "limit": 1
}

response = requests.get(url, headers=headers, params=params)

# Check if rate limited
if response.status_code == 429:
    print("Rate limited! Status Code:", response.status_code)
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        print(f"Retry after {retry_after} seconds.")
else:
    print("Status Code:", response.status_code)
    print(response.json())