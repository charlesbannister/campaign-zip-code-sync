from zip_sync.slack.slack_notifier import SlackNotifier
import os

def send_alert_slack(message: str):
    slack_alerts_webhook = os.getenv("SLACK_ALERTS_WEBHOOK", None)
    if not slack_alerts_webhook:
        raise ValueError("SLACK_ALERTS_WEBHOOK is not set in the environment variables")
    slack_notifier = SlackNotifier(slack_alerts_webhook=slack_alerts_webhook)
    slack_notifier.send_alerts_message(message)