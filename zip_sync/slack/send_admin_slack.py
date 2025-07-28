from zip_sync.slack.slack_notifier import SlackNotifier
import os

def send_admin_slack(message: str):
    slack_admin_webhook = os.getenv("SLACK_ADMIN_WEBHOOK", None)
    if not slack_admin_webhook:
        raise ValueError("SLACK_ADMIN_WEBHOOK is not set in the environment variables")
    slack_notifier = SlackNotifier(slack_admin_webhook=slack_admin_webhook)
    slack_notifier.send_admin_message(message)