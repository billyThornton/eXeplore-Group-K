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
from flask import Flask
from flask_testing import TestCase
#import databaseAdapter

from manage import app,session
import ibm_db
from databaseAdapter import createConnection, getStudentID,getTutorPassword,insertTutorUser
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
    
    def existingStudent(self,name,email,password):
        db2conn = createConnection()
        name = name.lower()
        email = email.lower()
        TeamID = 2
        TutorID = 1
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
        
        
    def loginuser(self,testClient,email,password):
        return testClient.post('/',
        data=dict(email=email,password=password),
        follow_redirects=True)

 
###############
#### tests ####
###############   
        
    def test_registation_incorrect_email_extension(self):
        with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test1@NotCorrectExtension.com','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assertIn('email of extension',session['Error Message'])
            
    def test_registration_existing_email(self):
        with app.test_client() as testClient:
            #Student exists
            self.existingStudent('Test entry','test1@exeter.ac.uk','password')
            response = self.registerIndividual(testClient,'Test entry','test1@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assert_context('error_message',"Email is already used")
            #tutor exists
            insertTutorUser('test@exeter.ac.uk',1,'test tester')
            response = self.registerIndividual(testClient,'Test entry','test@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assert_context('error_message',"Email is already used")
            
    
    def test_registration_valid_student(self):
        with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test1@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assert_context('error_message','registration successful')
            #Checks that user added to student but not tutor
            check = getStudentID('test1@exeter.ac.uk')
            self.assertGreater(len(check),0)
            check = getTutorPassword('test1@exeter.ac.uk')
            self.assertEqual(len(check),0)
    
    def test_registration_invalid_tutor_selection(self):
        with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test1@exeter.ac.uk','password','password','Test Tester')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/register.html')
            self.assert_context('error_message','That tutor does not exist')
    
    
    def test_registration_valid_tutor(self):
         with app.test_client() as testClient:
            response = self.register(testClient,'Test entry','test@exeter.ac.uk','password','password','matt')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('Desktop/Game_Keeper_Login.html')
            self.assert_context('error_message','registration successful')
            #Checks that user added to student but not tutor
            check = getStudentID('test@exeter.ac.uk')
            self.assertEqual(len(check),0)
            check = getTutorPassword('test@exeter.ac.uk')
            self.assertGreater(len(check),0)
            
    def test_login_student(self):
        with app.test_client() as testClient:
            response = self.loginuser(testClient,'test1@exeter.ac.uk','password')
            self.assertEqual(response.status_code,200)
            self.assert_template_used('mobile/Clue_Page.html')
    
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
            self.assert_context('error_message',"User does not exist")
            
            
    
    
    
    
            
        
     
if __name__ == "__main__":
    unittest.main()