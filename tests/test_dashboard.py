# -*- coding: utf-8 -*-
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
Created on 10/03/2020
@author: Billy Thornton
@Last Edited: 12/03/2020
@edited by: Billy Thornton

This is the test suite for the gamekeeper dashboard functions
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

    ########################################################################
    #### helper methods: Copied not imported so tests can run independently####
    ########################################################################
    def getStudentIDFromEmail(self, email):
        """
        Gets the student id when given a student email
        :return: Int studentID
        """
        return getStudentID(email)[0]['STUDENT_ID']

    def registerIndividual(self, testClient, name, email, password, confirm, tutorname):
        """
        Registers a new user
        :return: the response of the post
        """
        return testClient.post('/registerSubmit',
                               data=dict(name=name, email=email, password=password, passwordConfirmation=confirm,
                                         tutorName=tutorname),
                               follow_redirects=True)

    def register(self, testClient, name, email, password, confirm, tutorname):
        """
        Deletes the test users and then re registers them
        :return: the response of the insert
        """
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
        """
        Adds a student into the database witthout dropping the user
        :return: nothing
        """
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
        """
        Logs in the user to the system
        :return: the response from the login
        """
        return testClient.post('/', data=dict(email=email, password=password),
                               follow_redirects=True)

    def selectTeam(self, testClient, tutorName, teamName):
        """
        Selects a team from the database given a team name and tutor name
        :return: object
        """
        return testClient.post('/assignTeam',
                               data=dict(tutor=getTutorID(tutorName, "string")[0]['TUTOR_ID'],
                                         team=getTeamID(teamName)[0]['TEAM_ID']),
                               follow_redirects=True)

    def selectRoute(self, testClient, routeID, teamName):
        """
        Selects the route for a team
        :return: returns the response of this request
        """
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
        """
        Register a new tutor and two new users, then assign one user as the team leader of the tutors first team
        And Then assign the second to be the team leader. Assert that these changes are made
        """
        # Set up the student with a team
        with app.test_client() as testClient:
            ###Register Users###
            self.register(testClient, self.TUTORNAME, self.TUTOREMAIL, self.PASSWORD, self.PASSWORD, self.NOTAPPLICABLE)
            self.registerIndividual(testClient, self.STUDENTNAME, self.STUDENTEMAIL, self.PASSWORD, self.PASSWORD,
                                    self.TUTORNAME.lower())
            self.registerIndividual(testClient, self.STUDENTNAME + "2", self.STUDENTEMAIL2, self.PASSWORD,
                                    self.PASSWORD, self.TUTORNAME.lower())

            ###Login user1 and assign team and route###
            self.loginuser(testClient, self.STUDENTEMAIL, self.PASSWORD)
            self.selectTeam(testClient, self.TUTORNAME.lower(), self.TEAMNAME)
            self.selectRoute(testClient, 1, self.TEAMNAME)
            session.clear

            ###Login user2 and assign team###
            self.loginuser(testClient, self.STUDENTEMAIL2, self.PASSWORD)
            self.selectTeam(testClient, self.TUTORNAME.lower(), self.TEAMNAME)

            ###Check current teamleader is user 1###
            currentLeader = getTeamLeader(getTeamID(self.TEAMNAME)[0]['TEAM_ID'])[0]['TEAM_LEADER']
            studentID = self.getStudentIDFromEmail(self.STUDENTEMAIL)
            self.assertEqual(currentLeader, studentID)

            ###Login tutor and assign new team leader (user 2)###
            self.loginuser(testClient, self.TUTOREMAIL, self.PASSWORD)
            response = self.assignNewTeamLeader(testClient, self.TEAMNAME, self.STUDENTEMAIL2)

            ###Check the team leader is now user 2###
            newLeader = getTeamLeader(getTeamID(self.TEAMNAME)[0]['TEAM_ID'])[0]['TEAM_LEADER']
            studentID2 = self.getStudentIDFromEmail(self.STUDENTEMAIL2)
            self.assertEqual(currentLeader, studentID)
            self.assert_template_used('Desktop/Game_Keeper_Page.html')


if __name__ == "__main__":
    unittest.main()
