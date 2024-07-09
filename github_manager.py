import os

from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

load_dotenv()


class GithubManager(object):
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')

    def get_prs_to_review(self, app):
        since_date = (datetime.utcnow() - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%SZ')
        app.logger.info(f'Since date: {since_date}')
        url = f'https://api.github.com/notifications'
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        app.logger.info(f'Fetching notifications from GitHub: {url}')
        response = requests.get(url, headers=headers)

        pr_notifications = []
        if response.status_code == 200:
            notifications = response.json()
            for notification in notifications:
                if notification['subject']['type'] == 'PullRequest' and notification['updated_at'] >= since_date:
                    pr_notifications.append({
                        'title': notification['subject']['title'],
                        'url': self.format_github_url(notification['subject']['url']),
                        'reason': notification['reason'],
                        'updated_at': notification['updated_at']
                    })
        else:
            app.logger.info(f'Failed to fetch notifications: {response.status_code}')
            app.logger.info(response.text)

        return pr_notifications

    def format_github_url(self, api_url):
        # Split the URL to extract necessary parts
        parts = api_url.split('/')

        # Check if the URL matches the expected GitHub API format
        if len(parts) >= 7 and parts[2] == 'api.github.com' and parts[3] == 'repos':
            user_repo = parts[4:6]
            pull_number = parts[-1]

            # Construct the new GitHub web URL
            web_url = f"https://github.com/{user_repo[0]}/{user_repo[1]}/pull/{pull_number}"
            return web_url
        else:
            raise ValueError("Invalid GitHub API URL format")
