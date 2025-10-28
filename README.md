# Contact Checker Setup Guide

## Step 1 — Create a Data Extension

1. In your **Target** root account, create a new **Data Extension**.
2. Add a single field:

   * Name: `SubscriberCount`
   * Data Type: `Number`

---

## Step 2 — Create the Automation in Automation Studio

1. Go to **Automation Studio → New Automation → SQL Query**.
2. Create a new SQL Query with the following query:

```sql
SELECT COUNT(*) AS SubscriberCount
FROM _Subscribers
```

3. Set the automation to **run every hour** and target the Data Extension created in Step 1.

---

## Step 3 — Download and Configure the Script

1. Download the [script file](https://github.com/perites/ETContactsChecker/blob/master/contacts-checker.py) and save it as:
   **`contract_name-contacts-checker.py`**
2. Open the file in a text editor (e.g., VS Code, Sublime, or TextEdit).
3. Locate the **Config Section** at the top of the script and fill in the required fields:

**Note:** To find “Prod fields”: go to [**Prod OAuth connections**](https://prodepc.com/pages/brand/oauth-connection), search for your contract, and press **Update**.

| Field                    | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| **CONTRACT_NAME**        | Any name that identifies your contract                        |
| **SLACK_USER_ID**        | In Slack: **Profile → ⋯ (three dots) → Copy Member ID**       |
| **WORKFLOW_WEBHOOK_URL** | The Slack webhook URL provided for your workflow              |
| **SFMC_SUBDOMAIN**       | **API Endpoint** from Prod                                    |
| **CLIENT_ID**            | **Client ID** from Prod                                       |
| **CLIENT_SECRET**        | **Client Secret** from Prod                                   |
| **DE_KEY**               | External Key of the Data Extension created in Step 1          |
| **MAX_CONTACTS_LIMIT**   | Contact threshold that triggers a Slack warning               |
| **IGNORE_WARNING**       | `True` or `False` — if `True`, Slack warnings will be ignored |
| **DELETE_REPEATER**      | `True` or `False` — set `True` to stop or reset the checker   |

4. Save the changes after filling in all fields.

---

## Step 4 — Run the Script

1. Copy the full path of the script file:

   * In Finder, select the file.
   * Press **Command + C** to copy its location.
2. Open **Terminal**.
3. Type **`python`**, then a **space**, and paste the file path with **Command + V**.
4. Press **Enter** to run the script.
5. If configured correctly, you will see a confirmation message in Slack indicating the script is active.
6. Once your total contact count exceeds `MAX_CONTACTS_LIMIT`, the script will automatically send a Slack alert.

---

## Important Notes

* **Do not move or delete** this script file — it will stop working.
* If you need to move it to another folder:

  1. Set `DELETE_REPEATER = True`.
  2. Run the script once to disable the current scheduled task.
  3. Move the file to the new location.
  4. Set `DELETE_REPEATER = False` and run it from the new location.
* **The contact checks depend on this script **running on your machine** and having an active internet connection. If your computer is turned off or offline, the checks will not be performed.**
