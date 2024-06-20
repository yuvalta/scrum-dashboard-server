import json
from flask import Flask
from jira_manager import JiraManager

app = Flask(__name__)
jira_manager = JiraManager()


@app.route('/')
def home():
    return 'Hello World!'


@app.route('/dashboard')
def dashboard():
    return 'dashboard'


@app.route('/time_in_status/<ticket_number>')
def time_in_status(ticket_number):
    statuses_changes_dict = jira_manager.get_time_in_status_for_ticket(ticket_number)
    return_page = f"<h3>{ticket_number}</h3> <br>"
    return_page += "<br>".join([f"{key}: {value}" for key, value in statuses_changes_dict.items()])
    return return_page


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
