This project captures real-time events from a GitHub repository using Webhooks and displays them on a live dashboard.

## Tech Stack
- **Backend:** Flask (Python)
- **Database:** MongoDB
- **Frontend:** HTML/CSS with JS Polling (15s)
- **Tunneling:** ngrok

## How it works:
1. GitHub sends a payload to the `/webhook` endpoint.
2. The Flask app parses the action (PUSH, PULL_REQUEST, MERGE).
3. Data is stored in MongoDB with Indian Standard Time (IST).
4. The UI fetches the latest 10 actions every 15 seconds.
