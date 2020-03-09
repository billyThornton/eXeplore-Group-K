"""
Copyright (c) “2020, by Group K
Contributors: Jamie Butler, Rahul Pankhania, Teo Reed, Billy Thornton, Ben Trotter, Kristian Woolhouse
URL: https://github.com/billyThornton/eXeplore-Group-K ”
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials
provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAT PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Created on 19/02/2020
@author: Kris Woolhouse + Billy Thornton (Pair Programming)
@Last Edited: 26/02/2020
@edited by: Billy Thornton Added insert functions for passwords

This file contains the necessary information to make queries and enter data to/from
the datbase
"""
from flask import Flask
import os
import json
import ibm_db


app = Flask(__name__)
#Set to tru if running on local enviroment
localFlag = True

db_name = 'mydb'
client = None
db = None

#Loads the service credentials form the cloud envorioment if applicable
if 'VCAP_SERVICES' in os.environ:
    vcapEnv = json.loads(os.environ['VCAP_SERVICES'])
    db2info = vcapEnv['dashDB For Transactions'][0]
    db2cred = db2info["credentials"]


elif os.path.exists("servicesConfig.json"):
    with open('servicesConfig.json') as json_file:
        data = json.load(json_file)
        db2cred = data['dashDB For Transactions'][0]['credentials']

else:
    raise ValueError('Expected cloud environment')

#Create a connection to the database
def createConnection():
    db2conn = ibm_db.connect("DATABASE="+db2cred['db']+";HOSTNAME="+db2cred['hostname']+";PORT="+str(db2cred['port'])+";UID="+db2cred['username']+";PWD="+db2cred['password']+";","","")

    return db2conn


def getStudentName(studentID):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT name"
        " FROM student "
        " WHERE student_ID  = " + str(studentID) +
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


def getTeamFromStudentID(student):


    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT t.team_id,t.team_name, t.progress, r.route_name"
        " FROM team t"
        " INNER JOIN student s"
        " ON t.team_id = s.team_id"
        " INNER JOIN route r"
        " ON t.route_id = r.route_id"
        " WHERE s.student_id = " + str(student) +
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
        print(sql)
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

def getLocation(routeID,progress):
    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT l.location_id,l.location_image_url"
        " FROM location l"
        " INNER JOIN routelocationbridge r"
        " ON l.location_id = r.location_id"
        " WHERE route_id = " + str(routeID) +
        " and sequence_order = "+str(progress)+";"
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

def getNumLocationOnRoute(routeID):
    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT MAX(sequence_order)"
        " FROM routelocationbridge"
        " WHERE route_id = " + str(routeID) +";"
        )
        print(sql)
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

def getQuestionLocationID(locationID):
    db2conn = createConnection()

    if db2conn:
     # if we have a Db2 connection, query the database
        sql = (
        "SELECT question_content,MULTIPLE_CHOICE_A,MULTIPLE_CHOICE_B,MULTIPLE_CHOICE_C,MULTIPLE_CHOICE_D,ANSWER"
        " FROM question"
        " WHERE location_id = " + str(locationID)+";"
        )
        print("getQuestion ",sql)
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
        print("Get Question Result",rows)
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
        " WHERE email = '" + student +
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


def getTutorPassword(tutorEmail):

    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT p.password"
        " FROM tutor_password p"
        " INNER JOIN tutor t"
        " ON t.tutor_id = p.tutor_id"
        " WHERE email = '" + tutorEmail +
        "';"
        )
        print(sql)
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
        print(sql)
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

def getTutorIDFromStudentID(studentID):
    db2conn = createConnection()

    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "SELECT TUTOR_ID"
        " FROM STUDENT"
        " WHERE Student_id = " + str(studentID) +
        ";"
        )
        print(sql)
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

# Collects all locations for game keeper
def getLocations():
    db2conn = createConnection()
    # Query all locations
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = "SELECT location_name FROM location;"
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
    return rows
	
	# Returns all students in the database
def getStudents():
    db2conn = createConnection()
    # Query all locations
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = "SELECT name FROM student;"
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
    return rows


def getLocationID(locationName):
    db2conn = createConnection()
    # Query all locations
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = "SELECT location_id FROM location WHERE location_name = '" + str(locationName) + "';"
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
    return rows



def getTeams():
    db2conn = createConnection()
    # Query all locations
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = "SELECT team_id,team_name,current_route_id FROM Team ;"
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
    return rows

def getTutors():
    db2conn = createConnection()
    # Query all locations
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = "SELECT tutor_id,tutor_name FROM Tutor;"
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
    return rows

def getRoutes():
    db2conn = createConnection()
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = "SELECT route_id, route_name FROM Route;"
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
    return rows

def insertStudentUser(email,name,TeamID,TutorID):
    db2conn = createConnection()
    name = name.lower()
    email = email.lower()
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "INSERT INTO STUDENT (NAME,EMAIL,TEAM_ID,TUTOR_ID)"
        " VALUES ('"+name+"','"+email+"',"+str(TeamID)+","+str(TutorID)+");"
        )
        print(sql)
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)


def insertPasswordStudent(password,studentID):
    db2conn = createConnection()
    pepper= "fill"

    if db2conn:
        sql = (
            "INSERT INTO STUDENT_PASSWORD (STUDENT_ID,PASSWORD,PEPPER)"
            " VALUES ("+str(studentID)+",'"+password+"','"+pepper+"');"
            )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)

def insertTutorUser(email,office,name):
    db2conn = createConnection()
    name = name.lower()
    email = email.lower()
    #Override office to be 1 as office input isnt setup yet
    office = 1
    if db2conn:
        # if we have a Db2 connection, query the database
        sql = (
        "INSERT INTO TUTOR (OFFICE_ID,TUTOR_NAME,EMAIL)"
        " VALUES ("+str(office)+",'"+name+"','"+email+"');"
        )
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
		# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)


# Saves the hashed password
def insertPasswordTutor(password,tutorID):
    db2conn = createConnection()
    #pepper currently not implemented
    pepper= "fill"

    if db2conn:
        sql = (
            "INSERT INTO TUTOR_PASSWORD (TUTOR_ID,PASSWORD,PEPPER)"
            " VALUES ("+str(tutorID)+",'"+password+"','"+pepper+"');"
            )

        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)

def insertLocation(locationName):
    db2conn = createConnection()
    locationName = locationName.lower()
    if db2conn:
        sql = (
            "INSERT INTO location(location_name)"
            " VALUES('" + str(locationName) + "');"
            )

        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)

def insertQuestion(locationID, task, answerA, answerB, answerC, answerD, correctAnswer):
    db2conn = createConnection()

    if db2conn:
        sql = (
            "INSERT INTO question(location_id, question_content, multiple_choice_a, multiple_choice_b, multiple_choice_c, multiple_choice_d, answer)"
            " VALUES(" + str(locationID) + ", '" + str(task) + "', '" + str(answerA) + "', '" + str(answerB) + "', '" + str(answerC) + "', '" + str(answerD) + "', '" + str(correctAnswer) + "');"
            )

        print("SQL INSERT STATEMENT: ", sql)

        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)

def insertClue(locationID, clue):
    db2conn = createConnection()

    if db2conn:
        sql = (
            "INSERT INTO clue(location_id, contents)"
            " VALUES(" + str(location_id) + ", '" + str(clue) + "');"
            )

        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)
        

def insertTeam(teamName,routeID,tutorID,teamLeader,progress):
    db2conn = createConnection()

    if db2conn:
        sql = (
            "INSERT INTO TEAM (TEAM_NAME,CURRENT_ROUTE_ID,TUTOR_ID,TEAM_LEADER,PROGRESS)"
            " VALUES('" + teamName + "', " + str(routeID) + ", "+str(tutorID)
            +", "+str(teamLeader)+", "+str(progress)+");"
            )
        print(sql)
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)


def removeLocation(locationName):
    db2conn = createConnection()

    if db2conn:
        sql = (
            "DELETE FROM location"
            " WHERE location_name = '" + locationName + "';"
            )

        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
    	# Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)


def insertRoute(routeID,routeName):
    db2conn = createConnection()

    if db2conn:
        sql = (
            "INSERT INTO route (ROUTE_ID, ROUTE_NAME) VALUES("+str(routeID)+",'"+str(routeName)+"');"
            )

        print(sql)
        # Prepare the statement
        stmt = ibm_db.prepare(db2conn,sql)
        # Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)

def updateTeamRoute(routeID, teamID):
    db2conn = createConnection()

    if db2conn:
        print(teamID)
        print(routeID)
        sql = (
            "UPDATE team"
            " SET team.current_route_id = "+str(routeID)+"" 
            " WHERE team_id = "+str(teamID)+";"
            )

        print(sql)
        stmt = ibm_db.prepare(db2conn,sql)
        # Execute the sql
        ibm_db.execute(stmt)
        # close database connection
        ibm_db.close(db2conn)
