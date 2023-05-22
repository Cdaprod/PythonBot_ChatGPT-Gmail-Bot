import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from your_ml_model import predict_job_offer  # Import your trained model

# Load API keys and tokens from environment variables
gmail_token = os.getenv("GMAIL_TOKEN")
slack_token = os.getenv("SLACK_API_TOKEN")

# Initialize the Gmail API
creds = Credentials.from_authorized_user_file(gmail_token)
service = build('gmail', 'v1', credentials=creds)
user_id = 'me'

# Initialize the Slack API
client = WebClient(token=slack_token)

# Get the list of emails
try:
    results = service.users().messages().list(userId=user_id, q="subject:(job offer)").execute()
    messages = results.get('messages', [])
except HttpError as error:
    print(f'An error occurred: {error}')
    return

for message in messages:
    try:
        msg = service.users().messages().get(userId=user_id, id=message['id']).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
        continue

    payload = msg['payload']
    headers = payload['headers']
    subject = [x['value'] for x in headers if x['name'] == 'Subject'][0]
    body = payload['body']

    # Use your trained model to analyze the email body
    is_job_offer = predict_job_offer(subject, body)

    if is_job_offer:
        # Send a notification to Slack
        try:
            response = client.chat_postMessage(
                channel="job-offers",
                text=f"New job offer: {subject}"
            )
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")
