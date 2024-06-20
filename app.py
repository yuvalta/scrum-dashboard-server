from flask import Flask
from jira_manager import JiraManager
app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello World!'


@app.route('/dashboard')
def dashboard():

    return 'dashboard'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
