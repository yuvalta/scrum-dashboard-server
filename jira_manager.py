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
from common_functions import days_between_dates
import os

load_dotenv()


class JiraManager(object):
    def __init__(self):
        self.jira = JIRA('https://zadara.atlassian.net',
                         basic_auth=(os.getenv('JIRA_USERNAME'), os.getenv('JIRA_API_KEY')))

    def get_time_in_status_for_ticket(self, ticket_key):
        """
        Get the time in each status for a specific ticket
        Converting -
            Triaging -> Closed on 2024-06-19T09:20:53.760+0300
            Backlog -> Triaging on 2024-06-17T13:12:19.063+0300
            Waiting for More Info -> Backlog on 2024-06-17T10:31:59.750+0300
            Backlog -> Waiting for More Info on 2024-06-16T10:35:20.825+0300

        to -
            {"Waiting for More Info": 1, "Backlog": 1, "Triaging": 2}

        :param ticket_key: The ticket key (e.g. NK-1234)
        :return: A dictionary with the time in each status
        """
        ticket = self.jira.issue(ticket_key, expand='changelog')
        statues_changes_list = []

        for history in ticket.changelog.histories:
            for item in history.items:
                if item.field == 'status':
                    statues_changes_list.append((item.fromString, item.toString, history.created))

        time_in_status_dict = {}
        for i in range(len(statues_changes_list) - 1, 0, -1):
            current_days_count = time_in_status_dict.get(statues_changes_list[i - 1][0], 0)
            time_in_status_dict[statues_changes_list[i - 1][0]] = current_days_count + days_between_dates(
                statues_changes_list[i - 1][2], statues_changes_list[i][2])
        return time_in_status_dict

    def get_time_in_status_for_all_tickets_in_sprint_for_user(self, sprint_id, user_id):
        jql = f'project = NK AND Sprint = {sprint_id} AND assignee = {user_id}'  # or was assigned
        issues = self.jira.search_issues(jql)

        for issue in issues:
            self.get_time_in_status_for_ticket(issue.key)
