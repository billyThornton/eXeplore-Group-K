# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 10:27:48 2020

@author: billy
Edited: Jamie Butler

"""

import unittest

import flask_testing
import ibm_db

from databaseAdapter import getTeamLeader, getTeamID, createConnection, getStudentID, getTutorID
from manage import app, session


class BasicTests(flask_testing.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.secret_key = 'eXeplore_241199_brjbtk'
        app.SECURITY_PASSWORD_SALT = 'BFR241199'
        self.app = app.test_client()

        self.assertEqual(app.debug, False)

        return app

    # executed after each test
    def tearDown(self):
        pass

    ####################
    #### Constants ####
    ####################
    STUDENTNAME = 'Test student'
    STUDENTEMAIL = 'test1@exeter.ac.uk'
    STUDENTEMAIL2 = 'test2@exeter.ac.uk'
    PASSWORD = 'Password1'
    TUTORNAME = 'Test tutor'
    TUTOREMAIL = 'test@exeter.ac.uk'
    NOTAPPLICABLE = 'Not applicable'
    TEAMNAME = TUTORNAME.lower() + " team 1"

    ########################
    #### helper methods ####
    ########################
    def getStudentIDFromEmail(self, email):
        return getStudentID(email)[0]['STUDENT_ID']

    def registerIndividual(self, testClient, name, email, password, confirm, tutorname):
        return testClient.post('/registerSubmit',
                               data=dict(name=name, email=email, password=password, passwordConfirmation=confirm,
                                         tutorName=tutorname),
                               follow_redirects=True)

    def register(self, testClient, name, email, password, confirm, tutorname):
        db2conn = createConnection()

        if db2conn:
            sql = ("DELETE from student where email = '" + email + "'")
            # Prepare the statement
            stmt = ibm_db.prepare(db2conn, sql)
            ibm_db.execute(stmt)
            sql = ("DELETE from tutor where email = '" + email + "'")
            stmt = ibm_db.prepare(db2conn, sql)
            ibm_db.execute(stmt)
            ibm_db.close(db2conn)
        return self.registerIndividual(testClient, name, email, password, confirm, tutorname)

    def existingStudent(self, name, email, teamID, TutorName):
        db2conn = createConnection()
        name = name.lower()
        email = email.lower()
        TeamID = teamID
        TutorID = getTutorID(TutorName, "string")[0]['TUTOR_ID']
        if db2conn:
            # if we have a Db2 connection, query the database
            sql = (
                    "INSERT INTO STUDENT (NAME,EMAIL,TEAM_ID,TUTOR_ID,VERIFIED)"
                    " VALUES ('" + name + "','" + email + "'," + str(TeamID) + "," + str(TutorID) + ",TRUE);"
            )
            print(sql)
            # Prepare the statement
            stmt = ibm_db.prepare(db2conn, sql)
            # Execute the sql
            ibm_db.execute(stmt)
            # close database connection
            ibm_db.close(db2conn)

    def loginuser(self, testClient, email, password):
        return testClient.post('/', data=dict(email=email, password=password),
                               follow_redirects=True)

    def selectTeam(self, testClient, tutorName, teamName):
        return testClient.post('/assignTeam',
                               data=dict(tutor=getTutorID(tutorName, "string")[0]['TUTOR_ID'],
                                         team=getTeamID(teamName)[0]['TEAM_ID']),
                               follow_redirects=True)

    def selectRoute(self, testClient, routeID, teamName):
        return testClient.post('/routeSelect',
                               data=dict(route=routeID, teamName=teamName),
                               follow_redirects=True)

    def getQuestionTest(self, testClient):
        return testClient.post('/getQuestion', follow_redirects=True)

    def confirmAnswer(self, testClient, answer):
        return testClient.post('/confirmAnswer', data=dict(answer=answer), follow_redirects=True)

    def assignNewTeamLeader(self, testClient, teamname, email):
        return testClient.post('/assignTeamLeader',
                               data=dict(team=getTeamID(teamname)[0]['TEAM_ID'],
                                         student=self.getStudentIDFromEmail(email)),
                               follow_redirects=True)

    ###############
    #### tests ####
    ###############

    # TEST CORRECT ANSWER WORKS
    def test_dashboard_Assign_Team_Leader(self):
        # Set up the student with a team
        with app.test_client() as testClient:
            self.register(testClient, self.TUTORNAME, self.TUTOREMAIL, self.PASSWORD, self.PASSWORD, self.NOTAPPLICABLE)
            self.registerIndividual(testClient, self.STUDENTNAME, self.STUDENTEMAIL, self.PASSWORD, self.PASSWORD,
                                    self.TUTORNAME.lower())
            self.registerIndividual(testClient, self.STUDENTNAME + "2", self.STUDENTEMAIL2, self.PASSWORD,
                                    self.PASSWORD, self.TUTORNAME.lower())

            self.loginuser(testClient, self.STUDENTEMAIL, self.PASSWORD)
            self.selectTeam(testClient, self.TUTORNAME.lower(), self.TEAMNAME)
            self.selectRoute(testClient, 1, self.TEAMNAME)
            session.clear
            self.loginuser(testClient, self.STUDENTEMAIL2, self.PASSWORD)
            print("ASSERT")
            session.clear
            self.selectTeam(testClient, self.TUTORNAME.lower(), self.TEAMNAME)
            currentLeader = getTeamLeader(getTeamID(self.TEAMNAME)[0]['TEAM_ID'])[0]['TEAM_LEADER']
            studentID = self.getStudentIDFromEmail(self.STUDENTEMAIL)

            self.assertEqual(currentLeader, studentID)

            self.loginuser(testClient, self.TUTOREMAIL, self.PASSWORD)
            response = self.assignNewTeamLeader(testClient, self.TEAMNAME, self.STUDENTEMAIL2)
            newLeader = getTeamLeader(getTeamID(self.TEAMNAME)[0]['TEAM_ID'])[0]['TEAM_LEADER']
            studentID2 = self.getStudentIDFromEmail(self.STUDENTEMAIL2)
            self.assertEqual(currentLeader, studentID)
            self.assert_template_used('Desktop/Game_Keeper_Page.html')


if __name__ == "__main__":
    unittest.main()
