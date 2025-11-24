import requests
import config

class GraphHopperNav:
    def __init__(self):
        self.url = "http://localhost:8989"  # Direct URL since config might not have GRAPHHOPPER_URL

    def get_route(self, start_lat, start_lon, end_lat, end_lon):
        params = {
            'point': [f'{start_lat},{start_lon}', f'{end_lat},{end_lon}'],
            'profile': 'pedestrian',  # ✅ CHANGED from 'foot' to 'pedestrian'
            'points_encoded': 'false',  # Added this for better coordinate format
            'instructions': 'true',
            'elevation': 'false',
            'calc_points': 'true'
        }

        try:
            response = requests.get(f'{self.url}/route', params=params, timeout=10)  # Increased timeout

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError:
                    print("GraphHopper Error: Invalid JSON response")
                    return None
            else:
                print(f"GraphHopper API Error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"GraphHopper Client Error: {e} (Ensure local server is running on {self.url})")
            return None