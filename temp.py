from fastapi import FastAPI, HTTPException
import os
import pandas as pd
from google.cloud import bigquery, logging
from slack_sdk.webhook import WebhookClient
import uvicorn

app = FastAPI()

# Set up environment variables
project_id = os.getenv('PROJECT_ID')
credentials_path = os.getenv('BQ_CREDENTIALS_PATH')
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

# Set up Google Cloud credentials and logging client
if credentials_path:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
else:
    raise ValueError("Environment variable BQ_CREDENTIALS_PATH not set")

# logging_client = logging.Client()
# logger = logging_client.logger(name="trustbankpoc")

if not slack_webhook_url:
    raise ValueError("Environment variable SLACK_WEBHOOK_URL not set")

slack_webhook_client = WebhookClient(slack_webhook_url)

@app.post("/runquery")
async def run_query():
    query = f"SELECT Ticket_ID FROM `{project_id}.freshwork_test.freshwork18` WHERE Created_By = 'CA00002328'"
    bq_client = bigquery.Client()
    try:
        query_job = bq_client.query(query)
        results = query_job.result()
        df = results.to_dataframe()
        row_count = len(df)
        print(f'Query successful, retrieved {row_count} rows.')
        if row_count == 0:
            return {"message": "No tickets found"}

        message = " ".join(f"Ticket_ID: {row['Ticket_ID']}" for _, row in df.iterrows())
        print(message)

        # # Send message to Slack
        slack_response = slack_webhook_client.send(text=message)
        if slack_response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Slack notification failed with status code {slack_response.status_code}")

        return {"message": "Query successful, and Slack notification sent."}

    except Exception as e:
        print(f'Query failed: {str(e)}', severity='ERROR')
        raise HTTPException(status_code=500, detail=str(e))