import requests
from typing import Optional


class SlackNotifier:

    def __init__(
        self,
        slack_admin_webhook: Optional[str] = None,
        slack_alerts_webhook: Optional[str] = None
    ):
        self.slack_admin_webhook = slack_admin_webhook
        self.slack_alerts_webhook = slack_alerts_webhook
        
    def send_alerts_message(self, message: str) -> None:
        if not self.slack_alerts_webhook:
            raise ValueError("slack_alerts_webhook is not set")
        self._send_message(message, self.slack_alerts_webhook)

    def send_admin_message(self, message:str) -> None:
        """makes request using web_hook_url to send slack_data dictionary to slack channel
        associated with web_hook_url"""
        if not self.slack_admin_webhook:
            raise ValueError("slack_admin_webhook is not set")
        self._send_message(message, self.slack_admin_webhook)
    
    def _send_message(self, message: str, webhook_url: str) -> None:
        response = requests.post(
            webhook_url,
            json={'text': message},
            headers={"Content-Type": "application/json"},
        )
        if response.status_code != 200:
            print(f"error when sending slack notification: {response.status_code}")