import requests
import json

token = 'olp_5A3TpWke7PGUWpV8DlNMWKPxEvUYOT0EiQ24'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

project_data = {
    'name': 'Intrinsic Response Sector as Dark Gravity'
}

response = requests.post(
    'https://api.overleaf.com/api/v0/projects',
    headers=headers,
    json=project_data
)

print(f'Status: {response.status_code}')
print(f'Response: {response.text}')

if response.status_code == 201:
    project = response.json()
    print(f"\n✅ Project created successfully!")
    print(f"Project ID: {project.get('project_id')}")
    print(f"Git URL: https://git.overleaf.com/{project.get('project_id')}")
else:
    print(f"\n❌ Failed to create project: {response.status_code}")
    print(f"Response: {response.json()}")
