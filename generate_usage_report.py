import os
import time
import base64
import requests

# Read required environment variables
org_id = os.environ.get("ORG_ID")
api_token = os.environ.get("CIRCLECI_API_TOKEN")
start_date = os.environ.get("USAGE_START_DATE")  # e.g., "2025-01-01"
end_date = os.environ.get("USAGE_END_DATE")      # e.g., "2025-01-31"

if not all([org_id, api_token, start_date, end_date]):
    raise ValueError("Ensure ORG_ID, CIRCLECI_API_TOKEN, USAGE_START_DATE, and USAGE_END_DATE are set")

# Construct the Basic Auth header (API token as username, empty password)
auth_string = f"{api_token}:"
auth_bytes = auth_string.encode("ascii")
auth_base64 = base64.b64encode(auth_bytes).decode("ascii")
headers = {
    "Authorization": f"Basic {auth_base64}",
    "Content-Type": "application/json"
}

# --- Step 1: Trigger the Usage Export Job ---
post_url = f"https://circleci.com/api/v2/organizations/{org_id}/usage_export_job"
payload = {
    "start_date": start_date,
    "end_date": end_date
}

post_response = requests.post(post_url, json=payload, headers=headers)
if post_response.status_code != 200:
    raise Exception(f"Failed to trigger usage export job: {post_response.status_code} - {post_response.text}")

job_data = post_response.json()
# The job ID might be under a key like "usage_export_job_id" or "id"
usage_export_job_id = job_data.get("usage_export_job_id") or job_data.get("id")
if not usage_export_job_id:
    raise Exception("No usage export job id returned in the response.")

print(f"Triggered usage export job: {usage_export_job_id}")

# --- Step 2: Poll for the Usage Report Completion ---
get_url = f"https://circleci.com/api/v2/organizations/{org_id}/usage_export_job/{usage_export_job_id}"
max_attempts = 10
attempt = 0
while attempt < max_attempts:
    get_response = requests.get(get_url, headers=headers)
    if get_response.status_code != 200:
        raise Exception(f"Failed to get usage report: {get_response.status_code} - {get_response.text}")
    
    report_data = get_response.json()
    if report_data.get("status") == "completed":
        print("Usage report generation completed.")
        break
    
    print("Report not ready yet. Waiting for 30 seconds...")
    time.sleep(30)
    attempt += 1

if attempt == max_attempts:
    raise Exception("Usage export job did not complete within the expected time.")

# --- Step 3: Save the Report to a File ---
with open("usage_report.json", "w") as f:
    f.write(get_response.text)

print("Usage report saved as usage_report.json")
