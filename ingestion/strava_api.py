import requests
import os
from oauth import get_access_token
import json
import time


class StravaAPI:
    BASE_URL = "https://www.strava.com/api/v3"
    RAW_DATA_DIR = os.path.join("ingestion", "raw_data")

    def __init__(self):
        self.token = get_access_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def handle_rate_limit(self, headers):
        read_rate_limit = headers.get("x-readratelimit-limit")
        read_rate_usage = headers.get("x-readratelimit-usage")

        if read_rate_limit and read_rate_usage:

            rrl_15min, rrl_day = map(int, read_rate_limit.split(","))
            rru_15min, rru_day = map(int, read_rate_usage.split(","))

            left_15min = rrl_15min - rru_15min
            left_day = rrl_day - rru_day

            if left_day == 0:
                print("\tDaily rate limit reached - Try again tomorrow")
                exit()

            if left_15min <= 0:
                print("\tRate limit reached - Pausing for 15min")
                time.sleep(60 * 15)
            elif left_15min <= 10:
                print("\tLow rate limit - Pausing for 2min")
                time.sleep(60 * 2)
            elif left_15min <= 20:
                print("\tRate limit warning - Pausing for 30s")
                time.sleep(30)

    def make_request(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url=url, headers=self.headers, params=params)

        self.handle_rate_limit(response.headers)
        if response.status_code == 429:
            print("Error: rate limit exceeded")  # normally never reached

        return response

    def save_json(self, data, *file_path):
        path = os.path.join(self.RAW_DATA_DIR, *file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

    def load_json(self, *file_path):
        path = os.path.join(self.RAW_DATA_DIR, *file_path)
        with open(path, "r") as f:
            return json.load(f)

    def get_athlete(self):
        print("Fetching athlete information...")
        response = self.make_request("/athlete")
        athlete = response.json()
        self.save_json(athlete, "athlete.json")

    def get_athlete_activities(self):
        print("Fetching athlete activities (summary)...")
        page = 1
        activities = []

        while True:
            response = self.make_request(
                "/athlete/activities", {"page": page, "per_page": 200}
            )

            data = response.json()

            if not data:
                break

            activities.extend(data)
            page += 1

        self.save_json(activities, "activities.json")
        print(f"Retrieved {len(activities)} activities")

    def get_activity_id(self):
        print("Extracting activity IDs...")
        activities = self.load_json("activities.json")
        all_ids = [activity["id"] for activity in activities]
        self.save_json(all_ids, "ids.json")

    def get_activities_details(self, folder_name, endpoint_suffix="", params=None):
        data = self.load_json("ids.json")
        nb = len(data)

        for i, activity_id in enumerate(data, start=1):
            print(f"\tActivity {i}/{nb} (ID: {activity_id})")

            endpoint = f"/activities/{activity_id}{endpoint_suffix}"
            response = self.make_request(endpoint, params)

            activity = response.json()
            self.save_json(activity, folder_name, f"{activity_id}_{folder_name}.json")

    def get_activities_infos(self):
        print("Fetching detailed activity information...")
        self.get_activities_details("activity")

    def get_activities_streams(self):
        print("Fetching activity streams...")

        keys = [
            "time",
            "distance",
            "latlng",
            "altitude",
            "heartrate",
            "cadence",
            "moving",
            "velocity_smooth",
            "grade_smooth",
        ]
        keys = ",".join(keys)
        params = {"keys": keys, "key_by_type": True}

        self.get_activities_details("streams", "/streams", params)
