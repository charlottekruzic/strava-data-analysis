from strava_api import StravaAPI


def main():
    st = StravaAPI()
    st.get_athlete()
    st.get_athlete_activities()
    st.get_activity_id()
    st.get_activities_infos()
    st.get_activities_streams()
    print(f"All data successfully saved to '{st.RAW_DATA_DIR}'.")


if __name__ == "__main__":
    main()
