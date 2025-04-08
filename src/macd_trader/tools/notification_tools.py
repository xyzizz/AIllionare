import logging
import os

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class WechatNotificationToolInput(BaseModel):
    subject: str = Field(
        default="Trade Notification", description="The subject of the notification."
    )
    body: str = Field(..., description="The body of the notification.")


class WechatNotificationTool(BaseTool):
    name: str = "Wechat Notification Tool"
    description: str = (
        "Tool for sending notifications via WeChat using PushPlus service."
    )
    args_schema: type[BaseModel] = WechatNotificationToolInput

    def wechat_pushplus_notification(self, subject: str, body: str) -> str:
        """Sends a notification via WeChat using PushPlus service."""
        pushplus_token = os.getenv("PUSHPLUS_TOKEN")

        if not pushplus_token:
            logging.warning(
                "PushPlus Token not found in environment variables. Cannot send notification."
            )
            return "WeChat notification skipped: PushPlus Token not configured."

        logging.info("Attempting to send WeChat notification.")

        try:
            response = requests.post(
                "https://www.pushplus.plus/send",
                params={
                    "token": pushplus_token,
                    "title": subject,
                    "content": body,
                    "channel": "wechat",
                },
                timeout=10,
            )
            response.raise_for_status()  # Raise an exception for bad status codes

            logging.info(
                "WeChat notification sent successfully (based on status code)."
            )
            return "WeChat notification sent successfully."

        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending WeChat notification: {e}", exc_info=True)
            return f"Error sending WeChat notification: {e}"
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during WeChat notification: {e}",
                exc_info=True,
            )
            return f"Unexpected error sending WeChat notification: {e}"

    def _run(self, subject: str, body: str) -> str:
        """
        Sends notification via WeChat.
        """
        wechat_status = self.wechat_pushplus_notification(subject, body)
        return f"WeChat Status: {wechat_status}"
