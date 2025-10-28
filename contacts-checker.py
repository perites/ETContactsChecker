import json
import os
import sys
import plistlib
import subprocess
from pathlib import Path

try:
    import requests
except ImportError:
    print("`requests` not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


# ------------------------------
# CONFIG
# ------------------------------

CONTRACT_NAME = "xxx"

SLACK_USER_ID = "xxx"
WORKFLOW_WEBHOOK_URL = "xxx"

SFMC_SUBDOMAIN = "xxx"
CLIENT_ID = "xxx"
CLIENT_SECRET = "xxx"
DE_KEY = "xxx"

MAX_CONTACTS_LIMIT = 2_800_000

IGNORE_WARNING = False
DELETE_REPEATER = False

# ------------------------------
# CONFIG END
# ------------------------------

class TargetHelper:
    def __init__(self, sfmc_subdomain, client_id, client_secret, de_key):
        self.sfmc_subdomain = sfmc_subdomain
        self.client_id = client_id
        self.client_secret = client_secret
        self.de_key = de_key

        self.access_token = self.get_access_token()


    def get_access_token(self):
        url = f"https://{self.sfmc_subdomain}.auth.marketingcloudapis.com/v2/token"
        payload = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        res = requests.post(url, json=payload)
        res.raise_for_status()
        return res.json()["access_token"]


    def get_subscriber_count(self):
        url = f"https://{self.sfmc_subdomain}.rest.marketingcloudapis.com/data/v1/customobjectdata/key/{self.de_key}/rowset"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()

        row = data["items"][0]
        values = row.get("values", {})
        count_str = list(values.values())[0]
        return int(count_str)
        


class SlackHelper:
    def __init__(self, slack_user_id, workflow_webhook_url):
        self.workflow_webhook_url = workflow_webhook_url

        self.slack_user_id = slack_user_id


    def send_message(self, message):
        payload = {
            "message": message,
            "slack_user_id": self.slack_user_id  
        }

        headers = {"Content-Type": "application/json"}

        response = requests.post(
            self.workflow_webhook_url,
            headers=headers,
            data=json.dumps(payload)
        )


class PlistHelper:
    def __init__(self):
        self.script_path = os.path.abspath(sys.argv[0])
        self.plist_label= "com.ETContactsAlerts.mytask"
        self.plist_name = f"{self.plist_label}.plist"
        self.plist_path= Path.home() / "Library" / "LaunchAgents" / self.plist_name
        self.run_interval_seconds = 3600

    def create_plist(self):
        plist_content = {
            "Label": self.plist_label,
            "ProgramArguments": [sys.executable, self.script_path],
            "StartInterval": self.run_interval_seconds,
            "RunAtLoad": True
        }
        with open(self.plist_path, "wb") as f:
            plistlib.dump(plist_content, f)


    def load_plist(self):
        subprocess.run(["launchctl", "load", "-w", str(self.plist_path)])


    def disable_plist(self):
        subprocess.run(["launchctl", "remove", str(self.plist_label)])
        if self.plist_path.exists():
            self.plist_path.unlink()
            return True



if __name__ == "__main__":
    th = TargetHelper(SFMC_SUBDOMAIN, CLIENT_ID, CLIENT_SECRET, DE_KEY)
    sh = SlackHelper(SLACK_USER_ID, WORKFLOW_WEBHOOK_URL)
    ph = PlistHelper()

    try:
        if DELETE_REPEATER:
            result = ph.disable_plist()
            if result:
                sh.send_message(f"Repeater successfully disabled for contract {CONTRACT_NAME}")
            sys.exit(0)

        if not ph.plist_path.exists():
            ph.create_plist()
            ph.load_plist()
            sh.send_message(f"Loaded plist into launchd. The script will now run every {ph.run_interval_seconds} seconds and check contacts in {CONTRACT_NAME}.")
        
        total_contacts_count = th.get_subscriber_count()
        if (total_contacts_count > MAX_CONTACTS_LIMIT) and (not IGNORE_WARNING):
            sh.send_message(f"⚠️ ALARM!\nMax contacts limit reached in: {CONTRACT_NAME}\nContacts Now: {total_contacts_count}\nContacts Limit: {MAX_CONTACTS_LIMIT}")
    
    except Exception as e:
        sh.send_message(f"🤭 Error during target contacts check for {CONTRACT_NAME}. Details:\n{e}")
