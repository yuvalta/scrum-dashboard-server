from jira import JIRA
from dotenv import load_dotenv
from common_functions import days_between_dates
import os
import plotly.express as px
import pandas as pd

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

    def get_user_by_name(self, user_name):
        return self.jira.search_users(query=user_name)

    def get_time_in_status_for_all_tickets_in_sprint_for_user(self, sprint_id, user_id):
        jql = f'project = NK AND Sprint = {sprint_id} AND assignee = {user_id}'  # or was assigned
        issues = self.jira.search_issues(jql)

        for issue in issues:
            self.get_time_in_status_for_ticket(issue.key)

    def get_pie_chart_for_time_in_status_for_ticket(self, ticket_key):
        time_in_status_dict = self.get_time_in_status_for_ticket(ticket_key)
        df = pd.DataFrame(time_in_status_dict, index=[0])
        fig = px.pie(df, names=df.columns, values=df.iloc[0])
        fig.update_traces(textposition='inside', textinfo='percent+label+value', textfont_size=20,
                          marker=dict(line=dict(color='#000000', width=2)))
        image_path = f'images/{ticket_key}.png'
        fig.write_image("static/" + image_path)
        return image_path, time_in_status_dict

    def get_sprint_report_for_user(self, user_name, app):
        user_id = self.get_user_by_name(user_name)[0].accountId
        user_display_name = self.get_user_by_name(user_name)[0].displayName
        jql = f'project = "NK" AND assignee was {user_id} AND Sprint in openSprints() ORDER BY status DESC, created DESC'
        issues = self.jira.search_issues(jql)
        app.logger.info(issues)

        tickets = []
        for issue in issues:
            app.logger.info(issue.fields.status.name)
            if issue.fields.status.name == 'Closed' or issue.fields.status.name == 'Ready for Testing':
                chart_path, _ = self.get_pie_chart_for_time_in_status_for_ticket(issue.key)
                if chart_path:
                    tickets.append(issue.key)

        return tickets, user_display_name, jql

    def get_new_tickets_in_last_24_hours(self, app):
        jql = 'project = zCompute  and "Scrum Team[Dropdown]" = SYS and (createdDate >= -2d or updatedDate >= -2d) and status = BACKLOG and Sprint is EMPTY and fixVersion = zCompute-24.03 and type != Epic'
        issues = self.jira.search_issues(jql)

        app.logger.info(issues)

        last_issues_list = []
        for issue in issues:
            last_issues_list.append({
                'key': issue.key,
                'summary': issue.fields.summary,
                'created': issue.fields.created,
                'url': f'https://zadara.atlassian.net/browse/{issue.key}'
            })
        return last_issues_list
