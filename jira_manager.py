# In [33]: for history in stam.changelog.histories:
#     ...:     for item in history.items:
#     ...:         if item.field == 'status':
#     ...:             print('%s -> %s on %s'% (item.fromString, item.toString, history.created))


# Ready for integration -> Ready for Testing on 2024-06-06T15:39:23.421+0300
# Review -> Ready for integration on 2024-06-04T20:34:19.924+0300
# Development -> Review on 2024-06-02T09:47:35.724+0300
# Waiting for More Info -> Development on 2024-06-02T09:47:33.571+0300
# Development -> Waiting for More Info on 2024-05-15T10:06:44.512+0300
# Review -> Development on 2024-05-15T10:06:31.261+0300
# Development -> Review on 2024-03-31T10:05:02.198+0300
# Backlog -> Development on 2024-02-13T16:23:59.812+0200

from jira import JIRA
from dotenv import load_dotenv
import os
import json
import sys

load_dotenv()

# TODO: calculate the time spent on each status in days
jira = JIRA('https://zadara.atlassian.net', basic_auth=(os.getenv('JIRA_USERNAME'), os.getenv('JIRA_API_KEY')))


class JiraManager(object):
    def __init__(self):
        self.jira = JIRA('https://zadara.atlassian.net',
                         basic_auth=(os.getenv('JIRA_USERNAME'), os.getenv('JIRA_API_KEY')))

    def get_time_in_status_for_ticket(self, ticket_key):
        ticket = self.jira.issue(ticket_key, expand='changelog')
        statues_changes_list = []

        for history in ticket.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    print('%s -> %s on %s' % (item.fromString, item.toString, history.created))
                    statues_changes_list.append((item.fromString, item.toString, history.created))

        statues_changes_list.sort(key=lambda x: x[2])

        for status in range(1, len(statues_changes_list)):
            print(statues_changes_list[status][2] - statues_changes_list[status - 1][2])

    def get_time_in_status_for_all_tickets_in_sprint_for_user(self, sprint_id, user_id):
        jql = f'project = NK AND Sprint = {sprint_id} AND assignee = {user_id}'  # or was assigned
        issues = self.jira.search_issues(jql)

        for issue in issues:
            self.get_time_in_status_for_ticket(issue.key)
