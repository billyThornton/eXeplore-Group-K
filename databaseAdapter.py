from flask import Flask, render_template, request, session
import atexit
import os
import json
import ibm_db
import requests

app = Flask(__name__)
localFlag = True
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


def createConnection():
    if localFlag:
        db2conn= ibm_db.connect(connectionInfo[0],connectionInfo[1],connectionInfo[2])
    else:
        db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")

    return db2conn


def getStudent(tutor):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT s.name, s.email"
        " FROM student s"
        " INNER JOIN tutor t"
        " ON s.tutor_id = t.tutor_id"
        " WHERE tutor_name = '" + tutor +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getTeamMembers(teamName):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT s.name, s.email"
        " FROM student s"
        " INNER JOIN team t"
        " ON s.team_id = t.team_id"
        " WHERE team_name = '" + teamName +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getRouteLocations(routeName): #Need to check the SQL - might be confusing route_id and route_name

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT l.location_name"
        " FROM location l"
        " INNER JOIN route r"
        " ON l.location_id = r.location_id"
        " WHERE route_name = '" + routeName +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getTeamFromStudent(student):


    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT t.team_name, t.progress, r.route_name"
        " FROM team t"
        " INNER JOIN student s"
        " ON t.team_id = s.team_id"
        " INNER JOIN route r"
        " ON t.route_id = r.route_id"
        " WHERE s.name = '" + student +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows

def getTeamFromID(teamID):


    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT t.team_name, t.progress, r.route_name"
        " FROM team t"
        " INNER JOIN route r"
        " ON t.route_id = r.route_id"
        " WHERE t.team_id = " + str(teamID) +
        ";"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getStudentProgress(student):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT t.progress"
        " FROM team t"
        " INNER JOIN student s"
        " ON t.team_id = s.team_id"
        " WHERE name = '" + student +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getTutorOffice(tutor):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT o.office_name"
        " FROM office o"
        " INNER JOIN tutor t"
        " ON t.office_id = o.office_id"
        " WHERE tutor_name = '" + tutor +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getRouteID(teamID):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT route_id"
        " FROM team"
        " WHERE team_id = " + str(teamID) +
        ";"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getOfficeLocation(officeID):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT office_name, location_id"
        " FROM office"
        " WHERE office_id = " + str(officeID) +
        ";"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getLocationClues(locationID):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT contents"
        " FROM clue"
        " WHERE location_id = " + str(locationID) +
        ";"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getStudentPassword(student):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT p.password"
        " FROM student_password p"
        " INNER JOIN student s"
        " ON s.student_id = p.student_id"
        " WHERE name = '" + student +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def getTutorPassword(tutor):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT p.password"
        " FROM tutor_password p"
        " INNER JOIN student s"
        " ON t.tutor_id = p.tutor_id"
        " WHERE tutor_name = '" + tutor +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows

def getTutorID(tutorName):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT TUTOR_ID"
        " FROM TUTOR"
        " WHERE tutor_name = '" + tutorName +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows

def getStudentID(email):
    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT STUDENT_ID"
        " FROM STUDENT"
        " WHERE EMAIL = '" + email +
        "';"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        rows=[]
        # fetch the result
        result = ibm_db.fetch_assoc(stmt)
        while result != False:
            rows.append(result.copy())
            result = ibm_db.fetch_assoc(stmt)
        # close database connection
        ibm_db.close(db2conn)
        # Print to screen the result
        print(rows)
    return rows


def insertStudentUser(email,name,TeamID,password,TutorID):
    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "INSERT INTO STUDENT (NAME,EMAIL,TEAM_ID,TUTOR_ID)"
        " VALUES ('"+name+"',"+email+","+TeamID+","+TutorID+");"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        pepper= "fill"
        studentID = getStudentID(email)
        sql = (
        "INSERT INTO STUDENT_PASSWORD (STUDENT_ID,PASSWORD,PEPPER)"
        " VALUES ('"+studentID+"',"+password+","+pepper+");"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
       
    return rows