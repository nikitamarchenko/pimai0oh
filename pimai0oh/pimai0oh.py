from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for, abort

from urllib import urlencode
from collections import OrderedDict
import requests


app = Flask(__name__)
app.secret_key = 'pimai0oh+secret_key'
JIRA_URL = 'https://koinakvioletta.atlassian.net'
QA_LEAD = 'QA lead'


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        url = '{}/rest/api/latest/myself?expand=groups'.format(JIRA_URL)


        try:
            response = requests.get(url, auth=(username, password))
        except requests.exceptions.ConnectionError as ex:
            error = 'Login failed ({}, {})'.format(ex.message.args[0], ex.message.args[1])
        else:
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
        print projects_list
    else:
        error = 'Get Projects error ({} {})'.format(response.status_code, response.reason)

    return render_template('projects.html', error=error, projects=projects_list)


@app.route('/query/<string:project_key>', methods=['GET', 'POST'])
def query(project_key):
    if not session.get('logged_in'):
        abort(401)

    url = '{}/rest/api/latest/status'.format(JIRA_URL)
    response = requests.get(url, auth=session['jira_cred'])
    statuses = response.json()

    url = '{}/rest/api/latest/priority'.format(JIRA_URL)
    response = requests.get(url, auth=session['jira_cred'])
    prioritys = response.json()

    url = '{}/rest/api/latest/search?jql=type=epic&fields=id&project={}'.format(JIRA_URL, project_key)
    response = requests.get(url, auth=session['jira_cred'])
    epics = response.json()

    if session[QA_LEAD]:
        url = '{}/rest/api/2/user/assignable/search?project={}'.format(JIRA_URL, project_key)
        response = requests.get(url, auth=session['jira_cred'])
        assignable_users = response.json()
    else:
        assignable_users = []

    return render_template('query.html',
                           project_key=project_key,
                           statuses=statuses,
                           prioritys=prioritys,
                           epics=epics['issues'],
                           assignable_users=assignable_users)


@app.route('/report', methods=['POST'])
def report():
    if not session.get('logged_in'):
        abort(401)

    error = None
    if request.method == 'POST':

        project_key = request.form.get('project-key')
        status = request.form.getlist('status')
        priority = request.form.getlist('priority')
        epic = request.form.get('epic', 'No Epic')
        period_start = request.form.get('period-start')
        period_end = request.form.get('period-end')
        assignee = request.form.get('assignee')
        creator = request.form.get('creator')

        search = []

        if status:
            status = ['"{0}"'.format(w) for w in status]
            search.append("status in ({})".format(','.join(status)))

        if priority:
            priority = ['"{0}"'.format(w) for w in priority]
            search.append("priority in ({})".format(','.join(priority)))

        if epic != 'No Epic':
            search.append('"epic link" = "{}"'.format(epic))

        if period_start:
            search.append('created >= "{}"'.format(period_start))

        if period_end:
            search.append('created <= "{}"'.format(period_end))

        if assignee:
            search.append('assignee = "{}"'.format(assignee))

        if creator:
            search.append('creator = "{}"'.format(creator))

        search = ' and '.join(search)

        fields = 'status,created,summary'

        print search

        jql = urlencode(OrderedDict(jql=search, fields=fields))

        url = '{}/rest/api/latest/search?{}'.format(JIRA_URL, jql)

        response = requests.get(url, auth=session['jira_cred'])

        isues = {}
        if response.status_code == 200:
            isues = response.json()
            url = '{}/rest/api/latest/project/{}'.format(JIRA_URL, project_key)
            response = requests.get(url, auth=session['jira_cred'])
            project = response.json()
        else:
            error = 'Get Isuses error ({} {})'.format(response.status_code,
                                                        response.reason)
            project = {}

    return render_template('report.html',
                           isues=isues.get('issues', []),
                           project=project,
                           error=error,
                           form=request.form,
                           status=request.form.getlist('status'),
                           priority=request.form.getlist('priority'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)
