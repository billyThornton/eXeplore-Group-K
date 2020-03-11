# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 10:27:48 2020

@author: billy
"""

import os

import flask
import unittest
import flask_testing
import unittest
unittest.TestLoader.sortTestMethodsUsing = None
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

    def existingStudent(self,name,email,teamID,TutorName):
        db2conn = createConnection()
        name = name.lower()
        email = email.lower()
        TeamID = teamID
        TutorID = getTutorID(TutorName,"string")[0]['TUTOR_ID']
        if db2conn:
            # if we have a Db2 connection, query the database
            sql = (
            "INSERT INTO STUDENT (NAME,EMAIL,TEAM_ID,TUTOR_ID,VERIFIED)"
            " VALUES ('"+name+"','"+email+"',"+str(TeamID)+","+str(TutorID)+",TRUE);"
            )
            print(sql)
            # Prepare the statement
            stmt = ibm_db.prepare(db2conn,sql)
    		# Execute the sql
            ibm_db.execute(stmt)
            # close database connection
            ibm_db.close(db2conn)


    def loginuser(self,testClient,email,password):
        return testClient.post('/',
        data=dict(email=email,password=password),
        follow_redirects=True)

    def selectTeam(self, testClient, tutorName, teamName):
        return testClient.post('/assignTeam',
                               data=dict(tutor = getTutorID(tutorName,"string")[0]['TUTOR_ID'],
                                         team = getTeamID(teamName)[0]['TEAM_ID']),
                               follow_redirects=True)

    def selectRoute(selfself,testClient, routeID, teamName):
        return testClient.post('/routeSelect',
                               data = dict(route = routeID,teamName = teamName),
                               follow_redirects=True)


###############
#### tests ####
###############

    def test_registation_incorrect_email_extension(self):
        with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test1@NotCorrectExtension.com','password','password','matt colinson')
            self.assertEqual(response.status_code,200)
            #self.assertIn('email of extension',session['Error Message'])
            self.assertIn(b"email of extension", response.data)


    def test_registration_existing_email(self):
        with app.test_client() as testClient:
            self.register(testClient,'Test entry','test@exeter.ac.uk','password','password','matt colinson')
            #Student exists
            self.existingStudent('Test entry','test1@exeter.ac.uk','NULL','test entry')
            response = self.registerIndividual(testClient,'Test entry','test1@exeter.ac.uk','password','password','matt colinson')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assertIn(b"Email is already in use", response.data)

            #tutor exists
            insertTutorUser('test@exeter.ac.uk',1,'test tester')
            response = self.registerIndividual(testClient,'Test entry','test@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assertIn(b"Email or tutor name is already in use", response.data)


    def test_registration_valid_student(self):
        with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test1@exeter.ac.uk','password','password','Not applicable')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assertIn(b"registration successful", response.data)
            #Checks that user added to student but not tutor
            check = getStudentID('test1@exeter.ac.uk')
            self.assertGreater(len(check),0)
            check = getTutorPassword('test1@exeter.ac.uk')
            self.assertEqual(len(check),0)

    def test_registration_invalid_tutor_selection(self):
        with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test1@exeter.ac.uk','password','password','test tester')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assertIn(b'That tutor does not exist', response.data)


    def test_registration_valid_tutor(self):
         with app.test_client() as testClient:
            response = self.register(testClient,'Test Entry','test@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            #assert b"Tutor registration successful" in response.data
            self.assertIn(b"Tutor registration successful", response.data)
            #Checks that user added to student but not tutor
            check = getStudentID('test@exeter.ac.uk')
            self.assertEqual(len(check),0)
            check = getTutorPassword('test@exeter.ac.uk')
            self.assertGreater(len(check),0)

    def test_login_tutor(self):
        with app.test_client() as testClient:
            response = self.loginuser(testClient,'test@exeter.ac.uk','password')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Page.html')

    def test_login_wrong_password(self):
        with app.test_client() as testClient:
            response = self.loginuser(testClient,'test@exeter.ac.uk','notcorrectpassword')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assertIn(b"User does not exist", response.data)

    def test_login_new_user_no_team(self):
        with app.test_client() as testClient:
            response = self.loginuser(testClient, 'test1@exeter.ac.uk', 'password')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('mobile/Join_Team.html')

    def test_login_team_selection_no_leader(self):
        with app.test_client() as testClient:
            response = self.register(testClient, 'Test Entry', 'test@exeter.ac.uk', 'password', 'password', 'test entry')
            self.loginuser(testClient, 'test1@exeter.ac.uk', 'password')


            response = self.selectTeam(testClient,"test entry","test entry team 1")
            checkUserTeam = getTeamFromStudentID(getStudentID('test1@exeter.ac.uk')[0]['STUDENT_ID'])

            self.assertEqual(response.status_code,200)
            self.assert_template_used('mobile/First_Choose.html')
            self.assertEqual(checkUserTeam[0]['TEAM_ID'],getTeamID('test entry team 1')[0]['TEAM_ID'])


            response = self.selectRoute(testClient,1,"TEST NEW NAME")
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('mobile/Clue_Page.html')
            checkTeam = getTeamID("TEST NEW NAME")
            self.assertGreater(len(checkTeam),0)
            checkRoute = getRouteID(session['teamID'])
            self.assertEqual(checkRoute[0]['CURRENT_ROUTE_ID'],1)

    def test_login_team_set(self):
        with app.test_client() as testClient:
            self.loginuser(testClient, 'test1@exeter.ac.uk', 'password')
            checkUserTeam = getTeamFromStudentID(getStudentID('test1@exeter.ac.uk')[0]['STUDENT_ID'])

            if checkUserTeam[0]['TEAM_NAME'] != "TEST NEW NAME":
                self.selectTeam(testClient, "test entry", "test entry team 1")
                self.selectRoute(testClient, 1, "TEST NEW NAME")
        app.test_client().delete()
        with app.test_client() as testClient:
            self.register(testClient,"test user2","test2@exeter.ac.uk","password","password","test entry")
            self.loginuser(testClient, 'test2@exeter.ac.uk', 'password')
            response = self.selectTeam(testClient, "test entry", "TEST NEW NAME")
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('mobile/Clue_Page.html')
            checkUserTeam = getTeamFromStudentID(getStudentID('test2@exeter.ac.uk')[0]['STUDENT_ID'])
            self.assertEqual(checkUserTeam[0]['TEAM_ID'], getTeamID('TEST NEW NAME')[0]['TEAM_ID'])


if __name__ == "__main__":
    unittest.main()
