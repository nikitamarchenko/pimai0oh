from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for, abort

import requests


app = Flask(__name__)
app.secret_key = 'pimai0oh+secret_key'
JIRA_URL = 'https://vetakoko.atlassian.net'
QA_LEAD = 'QA lead'


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        url = '{}/rest/api/latest/myself?expand=groups'.format(JIRA_URL)

        response = requests.get(url, auth=(username, password))

        if response.status_code == 200:
            session['logged_in'] = True
            session['jira_cred'] = (username, password)
            session[QA_LEAD] = False
            result = response.json()

            session[QA_LEAD] = \
                QA_LEAD in [i['name'] for i in result['groups']['items']]

            return redirect(url_for('projects'))

        error = 'Login failed ({} {})'.format(response.status_code, response.reason)

    return render_template('login.html', error=error)


@app.route('/projects', methods=['GET', 'POST'])
def projects():
    if not session.get('logged_in'):
        abort(401)

    url = '{}/rest/api/latest/project?expand=description'.format(JIRA_URL)
    response = requests.get(url, auth=session['jira_cred'])
    projects_list = []
    error = ''
    if response.status_code == 200:
        projects_list = response.json()
        projects_list[0]['active'] = 'active'
        print projects
    else:
        error = 'Get Projects error ({} {})'.format(response.status_code, response.reason)

    return render_template('projects.html', error=error, projects=projects_list)


@app.route('/query/<int:project_id>', methods=['GET', 'POST'])
def query(project_id):
    if not session.get('logged_in'):
        abort(401)

    url = '{}/rest/api/latest/status'.format(JIRA_URL)
    response = requests.get(url, auth=session['jira_cred'])
    statuses = response.json()

    url = '{}/rest/api/latest/priority'.format(JIRA_URL)
    response = requests.get(url, auth=session['jira_cred'])
    prioritys = response.json()

    url = '{}/rest/api/latest/search?jql=type=epic&fields=id'.format(JIRA_URL)
    response = requests.get(url, auth=session['jira_cred'])
    epics = response.json()

    #from pprint import pprint

    #pprint(epics['issues'])

    #"epic link" = AA-13

    return render_template('query.html',
                           project_id=project_id,
                           statuses=statuses,
                           prioritys=prioritys,
                           epics=epics['issues'])


if __name__ == '__main__':
    app.run(debug=True, port=8080)

