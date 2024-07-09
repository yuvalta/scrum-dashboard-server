from flask import Flask, render_template
from jira_manager import JiraManager

app = Flask(__name__)
jira_manager = JiraManager()


@app.route('/')
def home():
    return render_template('index.html', title="Home", content="Hello, uv!")


@app.route('/dashboard')
def dashboard():
    return 'dashboard'


@app.route('/time_in_status/<ticket_number>')
def time_in_status(ticket_number):
    statuses_changes_dict = jira_manager.get_time_in_status_for_ticket(ticket_number)
    return_page = f"<h3>{ticket_number}</h3> <br>"
    return_page += "<br>".join([f"{key}: {value}" for key, value in statuses_changes_dict.items()])
    return return_page


@app.route('/dashboard/<ticket_number>')
def dashboard_ticket(ticket_number):
    pie_chart_path, time_in_status_dict = jira_manager.get_pie_chart_for_time_in_status_for_ticket(ticket_number)
    app.logger.info(pie_chart_path)

    return render_template('index.html', charts=[ticket_number],
                           title=f"Time spent on each status - {ticket_number}", content=time_in_status_dict)


@app.route('/user/<user_name>')
def user(user_name):
    user_details = jira_manager.get_user_by_name(user_name)
    if not user_details:
        return f"User {user_name} not found"

    return_page = f"<h3>{user_name}</h3> <br>"
    for current_user in user_details:
        return_page += "<br>".join(
            [current_user.displayName, current_user.emailAddress, current_user.accountId]) + "<br><br>"

    return return_page

@app.route('/user/<user_name>/sprint_report')
def user_sprint_report(user_name):
    tickets, user_display_name, jql = jira_manager.get_sprint_report_for_user(user_name, app)
    app.logger.info(tickets)
    return render_template('index.html', title=f"Sprint report for {user_display_name}", content="", tickets=tickets, jql=jql)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
