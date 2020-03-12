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

This is the test suite for the login functionality
"""


import flask_testing
import unittest
unittest.TestLoader.sortTestMethodsUsing = None

from manage import app,session
import ibm_db
from databaseAdapter import createConnection, getStudentID,getTutorPassword,insertTutorUser, getTeamID, getTutorID, getRouteID, getTeamFromStudentID
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

########################################################################
#### helper methods: Copied not imported so tests can run independently####
########################################################################

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

    ###############
    #### tests ####
    ###############


    def test_registation_incorrect_email_extension(self):
        """
        Tests that if email with incorrect extension is passed the user is informed with a flash message
        """
        with app.test_client() as testClient:
            ###Create a user with incorrect email###
            response = self.register(testClient,'Test student','test1@NotCorrectExtension.com','password','password','matt colinson')
            self.assertEqual(response.status_code,200)
            self.assertIn(b"email of extension", response.data)


    def test_registration_existing_email(self):
        """
        Test to ensure if email that is already used is entered into registration registration is blacked
        """
        with app.test_client() as testClient:
            ###Register a tutor and student###
            self.register(testClient,'Test tutor','test@exeter.ac.uk','password','password','matt colinson')
            self.existingStudent('Test student','test1@exeter.ac.uk','NULL','test tutor')

            ###Try to register a student with the same email check that redirect occurs###
            response = self.registerIndividual(testClient,'Test student','test1@exeter.ac.uk','password','password','matt colinson')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assertIn(b"Email is already in use", response.data)

            ###Try to register a tutor with the same email check that redirect occurs###
            insertTutorUser('test@exeter.ac.uk',1,'test tester')
            response = self.registerIndividual(testClient,'Test tutor','test@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assertIn(b"Email or tutor name is already in use", response.data)


    def test_registration_valid_student(self):
        """
        Register a valid student and ensure they are redirected to the login page
        """
        with app.test_client() as testClient:
            ###Register a tutor and student###
            self.register(testClient, 'Test tutor', 'test@exeter.ac.uk', 'password', 'password', 'matt')
            response = self.register(testClient,'Test student','test1@exeter.ac.uk','password','password','test tutor')

            ###Check to see they are redirected to the login page###
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assertIn(b"registration successful", response.data)

            ###Checks that user added to student but not tutor###
            check = getStudentID('test1@exeter.ac.uk')
            self.assertGreater(len(check),0)
            check = getTutorPassword('test1@exeter.ac.uk')
            self.assertEqual(len(check),0)


    def test_registration_valid_tutor(self):
         """
         Register a valid tutor and ensure redirect to login pages
         """
         with app.test_client() as testClient:
             ###Register a tutor###
            response = self.register(testClient,'Test tutor','test@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assertIn(b"Tutor registration successful", response.data)

            #Checks that user added to student but not tutor
            check = getStudentID('test@exeter.ac.uk')
            self.assertEqual(len(check),0)
            check = getTutorPassword('test@exeter.ac.uk')
            self.assertGreater(len(check),0)

    def test_login_tutor(self):
        """
        Check that when a tutor logs in they are redirected to the dashboard
        """
        with app.test_client() as testClient:
            response = self.loginuser(testClient,'test@exeter.ac.uk','password')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Page.html')

    def test_login_wrong_password(self):
        """
        Test that when an incorrect password is entered the access is denied
        """
        with app.test_client() as testClient:
            response = self.loginuser(testClient,'test@exeter.ac.uk','notcorrectpassword')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assertIn(b"User does not exist", response.data)

    def test_login_new_user_no_team(self):
        """
        When a user with no team logs in redirect to the select team screen
        """
        with app.test_client() as testClient:
            ###Register the team and tutor###
            self.register(testClient, 'Test tutor', 'test@exeter.ac.uk', 'password', 'password', 'test entry')
            self.register(testClient, 'Test student', 'test1@exeter.ac.uk', 'password', 'password', 'test tutor')
            ###Login the user ensure redirect to the join team page###
            response = self.loginuser(testClient, 'test1@exeter.ac.uk', 'password')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('mobile/Join_Team.html')

    def test_login_team_selection_no_leader(self):
        """
        Ensure that when a user joins a team without a team leader they are selected as the leader
        """
        with app.test_client() as testClient:
            ###Register a tutor and student and login the user###
            self.register(testClient, 'Test tutor', 'test@exeter.ac.uk', 'password', 'password', 'test entry')
            self.register(testClient, 'Test student', 'test1@exeter.ac.uk', 'password', 'password', 'test tutor')
            self.loginuser(testClient, 'test1@exeter.ac.uk', 'password')

            ###Test that the select team feature works###
            response = self.selectTeam(testClient,"test tutor","test tutor team 1")
            checkUserTeam = getTeamFromStudentID(getStudentID('test1@exeter.ac.uk')[0]['STUDENT_ID'])

            self.assertEqual(response.status_code,200)
            self.assert_template_used('mobile/First_Choose.html')
            self.assertEqual(checkUserTeam[0]['TEAM_ID'],getTeamID('test tutor team 1')[0]['TEAM_ID'])

            ###Select a route and eneter a new name ensure the changes save###
            response = self.selectRoute(testClient,1,"TEST NEW NAME")
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('mobile/Clue_Page.html')
            checkTeam = getTeamID("TEST NEW NAME")
            self.assertGreater(len(checkTeam),0)
            checkRoute = getRouteID(session['teamID'])
            self.assertEqual(checkRoute[0]['CURRENT_ROUTE_ID'],1)

    def test_login_team_set(self):
        """
        Login a user who already has their team set
        """
        with app.test_client() as testClient:
            ###Create a student and join a team and select route###
            self.loginuser(testClient, 'test1@exeter.ac.uk', 'password')
            checkUserTeam = getTeamFromStudentID(getStudentID('test1@exeter.ac.uk')[0]['STUDENT_ID'])

            if len(checkUserTeam) ==0 or checkUserTeam[0]['TEAM_NAME'] != "TEST NEW NAME" :
                self.selectTeam(testClient, "test tutor", "test tutor team 1")
                self.selectRoute(testClient, 1, "TEST NEW NAME")
        app.test_client().delete()
        with app.test_client() as testClient:
            ###Login to the user and ensure they are redirected to the correct question###
            self.register(testClient,"test user2","test2@exeter.ac.uk","password","password","test tutor")
            self.loginuser(testClient, 'test2@exeter.ac.uk', 'password')
            response = self.selectTeam(testClient, "test tutor", "TEST NEW NAME")
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('mobile/Clue_Page.html')
            checkUserTeam = getTeamFromStudentID(getStudentID('test2@exeter.ac.uk')[0]['STUDENT_ID'])
            self.assertEqual(checkUserTeam[0]['TEAM_ID'], getTeamID('TEST NEW NAME')[0]['TEAM_ID'])


if __name__ == "__main__":
    unittest.main()
