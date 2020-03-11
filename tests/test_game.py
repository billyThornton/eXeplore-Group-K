# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 10:27:48 2020

@author: billy
Edited: Jamie Butler

"""

import os

import flask
import unittest
import flask_testing
import unittest
from flask import Flask
from flask_testing import TestCase
#import databaseAdapter

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

########################
#### helper methods ####
########################
    def registerIndividual(self,testClient,name,email,password,confirm,tutorname):
        return testClient.post('/registerSubmit',
            data=dict(name=name, email=email, password=password, passwordConfirmation=confirm,tutorName=tutorname),
            follow_redirects=True)

    def register(self,testClient, name, email, password, confirm, tutorname):
        db2conn = createConnection()

        if db2conn:
            sql = ( "DELETE from student where email = '"+email+"'")
            # Prepare the statement
            stmt = ibm_db.prepare(db2conn,sql)
            ibm_db.execute(stmt)
            sql = ("DELETE from tutor where email = '"+email+"'")
            stmt = ibm_db.prepare(db2conn,sql)
            ibm_db.execute(stmt)
            ibm_db.close(db2conn)
        return self.registerIndividual(testClient,name,email,password,confirm,tutorname)



    def loginuser(self,testClient,email,password):
        return testClient.post('/',
        data=dict(email=email,password=password),
        follow_redirects=True)

    def selectTeam(self, testClient, tutorName, teamName):
        return testClient.post('/assignTeam',
                               data=dict(tutor = getTutorID(tutorName,"string")[0]['TUTOR_ID'],
                               team = getTeamID(teamName)[0]['TEAM_ID']),
                               follow_redirects=True)

    def selectRoute(self,testClient, routeID, teamName):
        return testClient.post('/routeSelect',
                               data = dict(route = routeID,teamName = teamName),
                               follow_redirects=True)


    def getQuestionTest(self,testClient):
        return testClient.post('/getQuestion',follow_redirects=True)

    def confirmAnswer(self,testClient,answer):
        return testClient.post('/confirmAnswer',data=dict(answer = answer),follow_redirects = True)



###############
#### tests ####
###############

    # TEST CORRECT ANSWER WORKS
    def test_game_correct_answer(self):
        with app.test_client() as testClient:
            self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'Not applicable')
            self.register(testClient,'Test entry','test1@exeter.ac.uk','Password1','Password1','test entry')
            self.loginuser(testClient,'test1@exeter.ac.uk','Password1')
            self.selectTeam(testClient, "test entry", "test entry team 1")
            self.selectRoute(testClient, 1, "TEST NEW NAME")
            response = self.getQuestionTest(testClient)
            response2 = self.confirmAnswer(testClient,'c')
            self.assertEqual(response2.status_code,200)
            self.assert_template_used('mobile/Clue_Page.html')
            self.assertEqual(session['teamScore'], 100)

    # TEST WRONG ANSWER FAILS
    def test_game_incorrect_answer(self):
        with app.test_client() as testClient:
            self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'Not applicable')
            self.register(testClient,'Test entry','test1@exeter.ac.uk','Password1','Password1','test entry')
            self.loginuser(testClient,'test1@exeter.ac.uk','Password1')
            self.selectTeam(testClient, "test entry", "test entry team 1")
            self.selectRoute(testClient, 1, "TEST NEW NAME")
            response = self.getQuestionTest(testClient)
            response2 = self.confirmAnswer(testClient,'a')
            self.assertEqual(response2.status_code,200)
            self.assert_template_used('mobile/Answer_Page.html')
            self.assertEqual(session['teamScore'], 97)


    def test_game_finishes(self):
        with app.test_client() as testClient:
            self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'Not applicable')
            self.register(testClient,'Test entry','test1@exeter.ac.uk','Password1','Password1','test entry')
            self.loginuser(testClient,'test1@exeter.ac.uk','Password1')
            self.selectTeam(testClient, "test entry", "test entry team 1")
            self.selectRoute(testClient, 1, "TEST NEW NAME")
            answers = ["c", "b", "d", "b", "a", "d", "b", "a"]
            for letter in answers:
                self.getQuestionTest(testClient)
                self.confirmAnswer(testClient, letter)
            self.assert_template_used('mobile/End_Game_Page.html')


if __name__ == "__main__":
    unittest.main()
