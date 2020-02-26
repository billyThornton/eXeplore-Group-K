import flask
from flask import Flask, render_template, request, session, redirect, url_for
import atexit
import os
import json
import ibm_db
import jwt
import requests
from flask_httpauth import HTTPBasicAuth
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

app = Flask(__name__)
localFlag = False

if 'VCAP_SERVICES' in os.environ:
    vcapEnv = json.loads(os.environ['VCAP_SERVICES'])
    appIDInfo = vcapEnv['AppID'][0]['credentials']
    app.config.update({'SERVER_NAME': json.loads(os.environ['VCAP_APPLICATION'])['uris'][0],
                      'SECRET_KEY': 'my_not_so_dirty_secret_key',
                      'PREFERRED_URL_SCHEME': 'https',
                      'PERMANENT_SESSION_LIFETIME': 1800, # session time in second (30 minutes)
                      'DEBUG': False})
    
    
else:
    print("local")
    with open('config.json') as confFile:
        print (confFile)
        # load JSON data from file
        appConfig=json.load(confFile)
        # Extract AppID configuration
        appIDInfo=appConfig['AppID']
        app.config.update({'SERVER_NAME': '10.173.84.95:8000',
        'SECRET_KEY': 'my_secret_key',
        'PREFERRED_URL_SCHEME': 'http',
        'PERMANENT_SESSION_LIFETIME': 2592000, # session time in seconds (30 days)
        'DEBUG': True})
    
appID_clientinfo=ClientMetadata(client_id=appIDInfo['clientId'],client_secret=appIDInfo['secret'])
appID_config = ProviderConfiguration(issuer=appIDInfo['oauthServerUrl'],client_metadata=appID_clientinfo)
auth = OIDCAuthentication({'default': appID_config}, app)
basicauth = HTTPBasicAuth()

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))


@app.route('/')
def root():
    rows = []
    return render_template('Game_s_Keeper_Login.html', returner=rows)
    #return app.send_static_file('Game_s_Keeper_Login.html')

@app.route('/login')
@auth.oidc_auth('default')
def index():
    if (flask.session['id_token']['email'])!="":
        return redirect(url_for('dashboard'))
    else:
        print("Test")
        return redirect(url_for('logout'))
    return render_template('Game_Keeper_Page.html')

@app.route('/dashboard')
@auth.oidc_auth('default')
def dashboard():
    return render_template('Leaderboard_Page.html')

@app.route('/redirect')
def logout():
    return render_template('Game_s_Keeper_Login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True,use_reloader=False)
