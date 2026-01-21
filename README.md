# Strava Data Analysis Project

This data engineering project using Strava data is in an early stage.

The current stage of the project covers **OAuth authentication** and **data ingestion**. It allows you to download your Strava data (account information and activities, including details and streams) in JSON format.

## Getting Started

### Prerequisites

- Python 3.12.1
- A Strava account and API credentials

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/charlottekruzic/strava-data-analysis.git
   ```

2. Navigate to the project directory:

   ```bash
   cd strava-data-analysis
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. [Log in](https://www.strava.com/register) to your Strava account

2. Obtain Strava API credentials by [creating an app](https://www.strava.com/settings/api)

3. Create a `.env` file and add your credentials:

   ```env
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret
   ```

## Run the project

```bash
python ./ingestion/fetch_data.py
```

> Execution may take some time due to the [Strava API rate limits](https://developers.strava.com/docs/rate-limits/), which allow only 100 read requests every 15 minutes.
