from flask import Flask, render_template, request, session
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
db_name = 'mydb'
client = None
db = None

if 'VCAP_SERVICES' in os.environ:
    vcapEnv = json.loads(os.environ['VCAP_SERVICES'])
    db2info = vcapEnv['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]
    appIDInfo = vcapEnv['AppID'][0]['credentials']
    
    provider_config={
     "issuer": "appid-oauth.ng.bluemix.net",
     "authorization_endpoint": appIDInfo['oauthServerUrl']+"/authorization",
     "token_endpoint": appIDInfo['oauthServerUrl']+"/token",
     "userinfo_endpoint": appIDInfo['profilesUrl']+"/api/v1/attributes",
     "jwks_uri": appIDInfo['oauthServerUrl']+"/publickeys"
    }
    client_info={
        "client_id": appIDInfo['clientId'],
        "client_secret": appIDInfo['secret']
    }
elif localFlag:
    connectionInfo = ["DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-lon02-02.services.eu-gb.bluemix.net;PORT=50000;UID=xkm27482;PWD=70852r6bqw-s8dgn;", "", ""]
else:
    raise ValueError('Expected cloud environment')
	
def getStudent():
    if localFlag:
        db2conn= ibm_db.connect(connectionInfo[0],connectionInfo[1],connectionInfo[2])
    else:
        db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    if db2conn:
        # if we have a Db2 connection, query the database
        sql="select * from STUDENT"
        #Prepare the statement 
        stmt = ibm_db.prepare(db2conn,sql)
		#Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        #Print to screen the result
		print(rows)
    return rows