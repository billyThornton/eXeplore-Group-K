from flask import Flask, render_template, request, session
import atexit
import os
import json
import ibm_db
import jwt

app = Flask(__name__, static_url_path='')
localFlag = True
db_name = 'mydb'
client = None
db = None

class ServiceConfig():
    REDIRECT_URI = "redirectUri"
    def getParamFromVcap(parsedVcap,serviceName,field):
        return parsedVcap.get(serviceName)[0]['credentials'][field]
    def getRedirectUri():
        redirectUri=os.environ.get('REDIRECT_URI')
        if not redirectUri:
            vcapApplication=os.environ.get('VCAP_APPLICATION')
            if vcapApplication:
                vcapApplication=json.loads(vcapApplication)
                redirectUri = "https://{}/afterauth".format(vcapApplication["application_uris"][0]);
            else:
                redirectUri='http://localhost:5000/afterauth'
        return redirectUri
    serverUrl='https://appid-oauth.ng.bluemix.net/oauth/v3/stub'
    VCAP_SERVICES=os.environ.get('VCAP_SERVICES')
    if VCAP_SERVICES:
        parsedVcap = json.loads(VCAP_SERVICES)
        serviceName=None
        if (parsedVcap.get('AdvancedMobileAccess')):
            serviceName='AdvancedMobileAccess'
        elif (parsedVcap.get('AppID')):
            serviceName='AppID'
        if(serviceName):
            serverUrl=getParamFromVcap(parsedVcap,serviceName,'oauthServerUrl')
            secret=getParamFromVcap(parsedVcap,serviceName,'secret')
            clientId=getParamFromVcap(parsedVcap,serviceName,'clientId')
            redirectUri=getRedirectUri()
    if (not serverUrl):
        raise 'please choose server url'


    @property
    def get_clientId(self):
        return 'clientId'

    @property
    def get_secret(self):
        return secret

    @property
    def get_serverUrl(self):
        return serverUrl

    def get_redirectUri(self):
        return redirectUri

    def __repr__(self):
        print ('{} {} {} {} '.format(clientId,secret,tokenEndpoint,redirectUri))
        return '<serviceConfig %r>' % (self.client_id)


if 'VCAP_SERVICES' in os.environ:
    db2info = json.loads(os.environ['VCAP_SERVICES'])['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]
    appenv = json.loads(os.environ['VCAP_APPLICATION'])
elif localFlag:
    connectionInfo = ["DATABASE=BLUDB;HOSTNAME=dashdb-txn-sbox-yp-lon02-02.services.eu-gb.bluemix.net;PORT=50000;UID=xkm27482;PWD=70852r6bqw-s8dgn;", "", ""]
else:
    raise ValueError('Expected cloud environment')
    
# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

def getStudent():
    if localFlag:
        db2conn= ibm_db.connect(connectionInfo[0],connectionInfo[1],connectionInfo[2])
    else:
        db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")
    if db2conn:
        # we have a Db2 connection, query the database
        sql="select * from STUDENT"
        # Note that for security reasons we are preparing the statement first,
        # then bind the form input as value to the statement to replace the
        # parameter marker.
        stmt = ibm_db.prepare(db2conn,sql)
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        print(rows)
    return rows


@app.route('/')
def root():
    rows = []
    return render_template('Game_s_Keeper_Login.html', returner=rows)
    #return app.send_static_file('Game_s_Keeper_Login.html')


@app.route('/dashboard')
def dashboard():
    return render_template('Game_Keeper_Page.html')
    

@atexit.register
def shutdown():
    if client:
        client.disconnect()
        
WebAppStrategy['AUTH_CONTEXT'] = "APPID_AUTH_CONTEXT";

@app.route('/protected')
def protected():
    tokens = session.get(WebAppStrategy['AUTH_CONTEXT'])
    if (tokens):
        publickey = retrievePublicKey(ServiceConfig.serverUrl)
        pem = getPublicKeyPem(publickey)
        idToken = tokens.get('id_token')
        accessToken = tokens.get('access_token')
        idTokenPayload = verifyToken(idToken,pem)
        accessTokenPayload = verifyToken(accessToken,pem)
        if (not idTokenPayload or not accessTokenPayload):
            session[WebAppStrategy['AUTH_CONTEXT']] = None
            return startAuthorization()
        else:
            print('idTokenPayload')
            print (idTokenPayload)
            return render_template('Add_Location_Page.html')
    else:
        return startAuthorization()
       
@app.route('/startAuthorization')
def startAuthorization():
    serviceConfig = ServiceConfig()
    clientId = serviceConfig.clientId

    authorizationEndpoint = serviceConfig.serverUrl + AUTHORIZATION_PATH
    redirectUri = serviceConfig.redirectUri
    return redirect("{}?client_id={}&response_type=code&redirect_uri={}&scope=appid_default".format(authorizationEndpoint,clientId,redirectUri))
    
@app.route('/afterauth')
def afterauth():
    error = request.args.get('error')
    code = request.args.get('code')
    if error:
        return error
    elif code:
        return handleCallback(code)
    else:
        return '?'
        
        
def retriveTokens(grantCode):
    serviceConfig = ServiceConfig()
    clientId = serviceConfig.clientId
    secret = serviceConfig.secret
    tokenEndpoint = serviceConfig.serverUrl + TOKEN_PATH
    redirectUri = serviceConfig.redirectUri
#    requests.post(url, data={}, auth=('user', 'pass'))
    r = requests.post(tokenEndpoint, data={"client_id": clientId,"grant_type": "authorization_code","redirect_uri": redirectUri,"code": grantCode
		}, auth = HTTPBasicAuth(clientId, secret))
    print(r.status_code, r.reason)
    if (r.status_code is not 200):
        return 'fail'
    else:
        return r.json()

def handleCallback(grantCode):
    tokens = retriveTokens(grantCode)
    if (type(tokens) is str):
        return tokens#it's error
    else:
        if (tokens['access_token']):
            session[WebAppStrategy['AUTH_CONTEXT']] = tokens
            return protected()
        else:
            return 'fail'
        
PUBLIC_KEY_PATH = "/publickey";
publickey = retrievePublicKey(ServiceConfig.serverUrl)
pem = getPublicKeyPem(publickey)
token = '{{some token}}'
verifyToken(token,pem)
def verifyToken(token,pemVal):
    try:
        payload = jwt.decode(token, pemVal, algorithms=['RS256'], options={'verify_aud':False})
        print('verified')
        return payload
 except:
        print ('not verified')
        return False
def retrievePublicKey(serverUrl):
    serverUrl = serverUrl + PUBLIC_KEY_PATH;
    content = urllib2.urlopen(serverUrl).read()
    publicKeyJson = content;
    return  publicKeyJson


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True,use_reloader=False)
