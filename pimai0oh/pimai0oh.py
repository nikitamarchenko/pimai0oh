from flask import Flask
from flask import render_template
from flask import request, session, redirect, url_for, abort

from pprint import pprint
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


@app.route('/report', methods=['POST'])
def report():
    if not session.get('logged_in'):
        abort(401)

    error = None
    if request.method == 'POST':

        status = request.form.getlist('status')
        priority = request.form.getlist('priority')
        epic = request.form.get('epic', 'No Epic')
        period_start = request.form.get('period-start')
        period_end = request.form.get('period-end')

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

        search = ' and '.join(search)

        fields = 'status,created,summary'

        print search

        jql = urlencode(OrderedDict(jql=search, fields=fields))

        url = '{}/rest/api/latest/search?{}'.format(JIRA_URL, jql)

        response = requests.get(url, auth=session['jira_cred'])

        isues = {}
        if response.status_code == 200:
            isues = response.json()
        else:
            error = 'Get Isuses error ({} {})'.format(response.status_code,
                                                        response.reason)

    return render_template('report.html',
                           isues=isues.get('issues', []),
                           error=error)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
