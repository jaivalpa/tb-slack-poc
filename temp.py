import os
import pandas as pd
from flask import Flask, jsonify
from google.cloud import bigquery, logging
from slack_sdk.webhook import WebhookClient

app = Flask(__name__)

# Set up Google Cloud credentials and logging client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/home/jaivalpatni/Documents/BQ Slack POC/tatvic-gcp-dev-team-d5df083fc125.json'
logging_client = logging.Client(project="tatvic-gcp-dev-team")
logger = logging_client.logger("trustbankpoc")

# Slack webhook URL
slack_webhook_url = 'https://hooks.slack.com/services/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'
slack_webhook_client = WebhookClient(slack_webhook_url)

@app.route('/runquery', methods=['POST'])
def run_query():
    query = "SELECT Ticket_ID FROM `tatvic-gcp-dev-team.freshwork_test.freshwork18` WHERE Created_By = 'CA00002328'"
    bq_client = bigquery.Client()

    try:
        query_job = bq_client.query(query)
        results = query_job.result()

        df = results.to_dataframe()
        row_count = len(df)
        logger.log_text(f'Query successful, retrieved {row_count} rows.')

        if row_count == 0:
            return jsonify({'message': 'No tickets found'}), 200

        message = "Ticket_IDs are:\n" + "\n".join(f"Ticket_ID: {row['Ticket_ID']}" for _, row in df.iterrows())

        # Send message to Slack
        slack_response = slack_webhook_client.send(text=message)
        if slack_response.status_code != 200:
            raise Exception(f"Slack notification failed with status code {slack_response.status_code}")

        return jsonify({'message': 'Query successful, and Slack notification sent.'}), 200

    except Exception as e:
        error_message = str(e)
        logger.log_text(f'Query failed: {error_message}', severity='ERROR')
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
