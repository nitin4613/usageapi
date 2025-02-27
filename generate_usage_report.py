import os
import base64
import requests

# Read environment variables (set these in CircleCI project settings or contexts)
org_id = os.environ.get("ORG_ID")
usage_export_job_id = os.environ.get("USAGE_EXPORT_JOB_ID")
api_token = os.environ.get("CIRCLECI_API_TOKEN")

if not all([org_id, usage_export_job_id, api_token]):
    raise ValueError("ORG_ID, USAGE_EXPORT_JOB_ID, and CIRCLECI_API_TOKEN must be set")

# Create the Basic Auth header
auth_string = f"{api_token}:"
auth_bytes = auth_string.encode("ascii")
auth_base64 = base64.b64encode(auth_bytes).decode("ascii")
headers = {"Authorization": f"Basic {auth_base64}"}

# Construct the endpoint URL
url = f"https://circleci.com/api/v2/organizations/{org_id}/usage_export_job/{usage_export_job_id}"

# Make the GET request
response = requests.get(url, headers=headers)

# Check for success and write to file
if response.status_code == 200:
    with open("report.json", "w") as f:
        f.write(response.text)
    print("Usage report generated successfully.")
else:
    raise Exception(f"Failed to retrieve usage report: {response.status_code} - {response.text}")
