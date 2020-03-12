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

This is the test suite for the game functionality
"""


import flask_testing
import unittest

from manage import app,session
import ibm_db
from databaseAdapter import createConnection,  getTeamID, getTutorID

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


    def getQuestionTest(self, testClient):
        return testClient.post('/getQuestion', follow_redirects=True)


    def confirmAnswer(self, testClient, answer):
        return testClient.post('/confirmAnswer', data=dict(answer=answer), follow_redirects=True)

###############
#### tests ####
###############


    def test_game_correct_answer(self):
        """
        Test that a correct answer progresses the game to the next location clue
        """
        with app.test_client() as testClient:
            ###Regitser a student and tutor user###
            self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'Not applicable')
            self.register(testClient,'Test entry','test1@exeter.ac.uk','Password1','Password1','test entry')

            ###Login the user and select a team and route###
            self.loginuser(testClient,'test1@exeter.ac.uk','Password1')
            self.selectTeam(testClient, "test entry", "test entry team 1")
            self.selectRoute(testClient, 1, "TEST NEW NAME")

            ###Get the question and submitt the correct answer check if the page loaded is the next question###
            self.getQuestionTest(testClient)
            response2 = self.confirmAnswer(testClient,'c')
            self.assertEqual(response2.status_code,200)
            self.assert_template_used('mobile/Clue_Page.html')

            ###Ensure the score is unchanged###
            self.assertEqual(session['teamScore'], 100)


    def test_game_incorrect_answer(self):
        """
        Test that an incorrect answer deducts 3 points and redirects back to the answer page for resubmission
        """
        with app.test_client() as testClient:
            ###Register a student and tutor user###
            self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'Not applicable')
            self.register(testClient,'Test entry','test1@exeter.ac.uk','Password1','Password1','test entry')

            ###Login the user and select a team and route###
            self.loginuser(testClient,'test1@exeter.ac.uk','Password1')
            self.selectTeam(testClient, "test entry", "test entry team 1")
            self.selectRoute(testClient, 1, "TEST NEW NAME")

            ###Get the question and submitt the correct answer check if the page loaded is the next question###
            self.getQuestionTest(testClient)
            response2 = self.confirmAnswer(testClient,'a')
            self.assertEqual(response2.status_code,200)
            self.assert_template_used('mobile/Answer_Page.html')

            ###Check score is reduced by 3###
            self.assertEqual(session['teamScore'], 97)


    def test_game_finishes(self):
        """
        Test a full run of the game answering all questions correctly
        :return: object
        """
        with app.test_client() as testClient:
            ###Register a student and tutor user###
            self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'Not applicable')
            self.register(testClient,'Test entry','test1@exeter.ac.uk','Password1','Password1','test entry')

            ###Login the user and select a team and route###
            self.loginuser(testClient,'test1@exeter.ac.uk','Password1')
            self.selectTeam(testClient, "test entry", "test entry team 1")
            self.selectRoute(testClient, 1, "TEST NEW NAME")

            ###Loop through route and check that score is unchanged and redirected to the ends screen###
            answers = ["c", "b", "d", "b", "a", "d", "b", "a"]
            for letter in answers:
                self.getQuestionTest(testClient)
                self.confirmAnswer(testClient, letter)

            self.assert_template_used('mobile/End_Game_Page.html')
            self.assertEqual(session['teamScore'], 100)

if __name__ == "__main__":
    unittest.main()
