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

Created on 19/02/2020 
@author: Billy Thornton
@Last Edited: 26/02/2020
@edited by: Billy Thornton

This file contains all the URL routing for the backend/front end, it takes urls
and displays the required html files.
It also processes data passed using post/get request.
"""
import flask
from flask import Flask, render_template, redirect, url_for, request,send_file,session
from itsdangerous import URLSafeTimedSerializer
import os
import auth
import databaseAdapter
from functools import wraps

exec(open('utils/utils.py').read())

app = Flask(__name__)
port = int(os.getenv('PORT', 8000))

#Used to restrict access to ceratin site areas
def requires_access_level(access_level):
    #Uses a decorator function
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            #if the session users role is not set send to login page
            if not session.get('Role'):
                return redirect(url_for('login'))
            #If the users session role is not high enough send them to the game page
            #They must be a student
            elif not session.get('Role') == access_level:
                return redirect(url_for('showLocationClue'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

#Handles the [post] method for login
#Will be passed a username and a password
@app.route('/',methods = ['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    #Checks the username and password are correct
    token = auth.verifyUser(password,email)
    
    if(token['VerificationToken']):
        #Sets the role of the user in the session
        if(token['Role']=='student'):
            session['Role'] = 'student'
            print(token)
            session['studentID'] = token['ID'][0]['STUDENT_ID']
            #get group ID
            print("session",session['studentID'])
            groupID = databaseAdapter.getTeamFromStudentID(session['studentID'])[0]['TEAM_ID']
            print("groupID",groupID)
            session['groupID'] = groupID
            routeID = databaseAdapter.getRouteID(session['groupID'])
            session['routeID'] = routeID[0]['ROUTE_ID']
            
        if(token['Role']=='tutor'):
            session['Role'] = 'staff'
            session['tutorID'] = token['tutorID']
        
    if(session['Role'] == "staff"):
        #If staff redirect to the dashboard
        return redirect(url_for('dashboard'))
    
    elif(session['Role'] == "student"):
        #If student redirect to the game
        return redirect(url_for('showLocationClue'))
    else:
        #If neither redirect to lgoin page
        return redirect(url_for('login'))

    
#This is the first page of the app currently the login page but we could add a splash screen if wanted
@app.route('/')
def login():
    session.clear()
    return render_template('Desktop/Game_Keeper_Login.html')

#Load registration window
@app.route('/register')
def register():
    #Checks if there is an error message is sent via a redirect
    if('Error Message' in session):
        #dosplay the message
        errorMessage = session['Error Message']
    else:
        #If no message set set the message to be empty (No message)
        session['Error Message'] = ""
        errorMessage = ""
        #Redner the register page with the errormessage variable passes in
    return render_template('Desktop/register.html',error_message = errorMessage)

#Handles registration
@app.route('/registerSubmit',methods = ['POST'])
def registerSubmit():
    global EMAILEXTENSION
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    passwordConfirm = request.form.get('passwordConfirmation')
    tutorName = request.form.get('tutorName')
    
    #Check if passwords match if not reload page with error message
    if(password != passwordConfirm):
        session['Error Message'] = "Passwords are not the same"
        return redirect(url_for('register'))
    #Check if the email is an exeter email
    if checkEmail(email):
        #Check if email has numbers if yes they must be a student
        if(hasNumbers(email)):
            
            #Check if the email is already registered
            if(len(databaseAdapter.getStudentID(email))==0):
                #TODO set team id by user preference
                teamID = 1
                #Get the tutor ID for the current student
                tutorID = databaseAdapter.getTutorID(tutorName)[0]['TUTOR_ID']
                #Hash the password
                hashedPassword = auth.hashPassword(password)
                #Inser the student to the database
                databaseAdapter.insertStudentUser(email,name,teamID,tutorID)
                
                #Insert the password to the database
                studentID = databaseAdapter.getStudentID(email)[0]['STUDENT_ID']
                databaseAdapter.insertPasswordStudent(hashedPassword,studentID)
            else:
                #Catches if email is registered
                session['Error Message'] = ("Email is already used")
                return redirect(url_for('register'))
                
        else:
            #Check if the email is already registered
            if(len(databaseAdapter.getTutorID(name))==0):
                databaseAdapter.insertTutorUser(email,1,name)
                hashedPassword = auth.hashPassword(password)
                tutorID = databaseAdapter.getTutorID(name)[0]['TUTOR_ID']
                databaseAdapter.insertPasswordTutor(hashedPassword,tutorID)
            else:
                session['Error Message'] = ("Email is already used")
                return redirect(url_for('register'))
        #Regsitration successful TODO add Success message
        return redirect(url_for('login'))
    #Catch email of wrong extension
    else:
        session['Error Message'] = ("Please use an email of extension "+EMAILEXTENSION)
        return redirect(url_for('register'))

#Will redirect uses back to the login page if they fail the login procedure
@app.route('/redirect')
def redirectLogin():
    return render_template('Game_s_Keeper_Login.html')

@app.route('/Logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/images/Exeter_University.jpg')
def imageUni():
    return send_file('static/images/Exeter_University.jpg',mimetype='image/jpg') 

@app.route('/static/Exeter_University.jpg')
def imageUniStatic():
    u = 2
    return send_file('static/images/Exeter_University.jpg',mimetype='image/jpg')     
######################
#GAMEMASTER DASHBOARD#
######################
#Loads the dashboard for game masters
@app.route('/dashboard')
@requires_access_level('staff')
def dashboard():
    return render_template('Desktop/Game_Keeper_Page.html')

@app.route('/Add_Location')
@requires_access_level('staff')
def addLocation():
    return render_template('Desktop/Add_Location_Page.html')

@app.route('/Edit_Location')
@requires_access_level('staff')
def editLocation():
    return render_template('Desktop/Edit_Location_Page.html')


#Loads the gamekeepers dashboard tool
@app.route('/Manage_Locations_Page')
@requires_access_level('staff')
def manageLocations():
    return render_template('Desktop/Manage_Locations_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Manage_Groups_Page')
@requires_access_level('staff')
def manageGroups():
    return render_template('Desktop/Manage_Groups_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Leaderboard_Page')
def leaderboard():
    return render_template('Desktop/Leaderboard_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Manage_Routes_Page')
@requires_access_level('staff')
def manageRoutes():
    return render_template('Desktop/Manage_Routes_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Assign_Routes_Page')
@requires_access_level('staff')
def assignRoutes():
    return render_template('Desktop/Assign_Routes_Page.html')

######################
#Student Game Pages  #
######################
#Displays the location clue page at an appropriate progression point
@app.route('/Game')
def showLocationClue():
    #get progress from db
    if 'progress' in session:
        progress = session['progress']
    else:
        session['progress'] = 0
        progress = 0
        
    #Check if route id is in session
    if 'routeID' in session:
        routeID = session['routeID']
    
    print(progress)
    locationID = databaseAdapter.getLocation(routeID,progress)[0]['LOCATION_ID']
    session['locationID'] = locationID
    print("LocationID",locationID)
    #check if there are no maore lcations
    if(len(databaseAdapter.getLocationClues(locationID))==0):
        return redirect(url_for('endScreen'))
    
    cluemessage = databaseAdapter.getLocationClues(locationID)[0]['CONTENTS']
    print(cluemessage)
    #progress value = get User.progress from db
    #clue message = get clue for position = progress from db
    imageLocation = url_for('static',filename='images/Exeterforum.jpg')
    print(imageLocation)
    return render_template('mobile/Clue_Page.html',progress_value = progress,clue_message = cluemessage,clue_location=imageLocation)

@app.route('/getQuestion',methods = ['POST'])
def getQuestion():
    progress = request.form.get('progress')
    questionData = databaseAdapter.getQuestion(session['locationID']+1)
    imageLocation = url_for('static',filename='images/Exeterforum.jpg')
    questionText = questionData[0]['QUESTION_CONTENT']
    a= questionData[0]['MULTIPLE_CHOICE_A']
    b= questionData[0]['MULTIPLE_CHOICE_B']
    c= questionData[0]['MULTIPLE_CHOICE_C']
    d= questionData[0]['MULTIPLE_CHOICE_D']
    return render_template('mobile/Answer_Page.html',progress_value = progress,clue_message = "Question: "+questionText,clue_location=imageLocation,
                           answer_a = a, answer_b = b, answer_c = c, answer_d = d)

@app.route('/getQuestionRedirect')
def retryQuestion():
    if('QuestionMessage' in session):
        #dosplay the message
        error_message = session['QuestionMessage']
    else:
        #If no message set set the message to be empty (No message)
        session['QuestionMessage'] = ""
        error_message = ""
    progress = request.form.get('progress')
    progress = request.form.get('progress')
    questionData = databaseAdapter.getQuestion(session['locationID']+1)
    imageLocation = url_for('static',filename='images/Exeterforum.jpg')
    questionText = questionData[0]['QUESTION_CONTENT']
    a= questionData[0]['MULTIPLE_CHOICE_A']
    b= questionData[0]['MULTIPLE_CHOICE_B']
    c= questionData[0]['MULTIPLE_CHOICE_C']
    d= questionData[0]['MULTIPLE_CHOICE_D']
    return render_template('mobile/Answer_Page.html',error_message=error_message,progress_value = progress,clue_message = "Question: "+questionText,clue_location=imageLocation,
                           answer_a = a, answer_b = b, answer_c = c, answer_d = d)
@app.route('/confirmAnswer',methods = ['POST'])
def checkQuestion():
    maxProgress = 10
    progress = request.form.get('progress')
    answer = request.form.get('answer')
    questionData = databaseAdapter.getQuestion(session['locationID']+1)
    answer = answer.upper()
    correctAnswer = questionData[0]['ANSWER'];
    print(type(answer),type(correctAnswer))
    print("answer",answer[0])
    print("Wesution",correctAnswer[0])
    if(str(answer[0]) == str(correctAnswer[0])):
        print("SAME")
        #print(int(progress), answer, int(maxProgress))
        if (int(progress) == int(maxProgress)):
            return redirect(url_for('endScreen'))
        else:
            session['progress'] = session.get('progress')+1
            return redirect(url_for('showLocationClue'))
    else:
        session['QuestionMessage'] = 'Wrong answer try again'
        #redirect to the question page but with error message
        return redirect(url_for('retryQuestion'))
    
@app.route('/finished')
def endScreen():
    groupName = "Group1"
    finalScore = "100"
    finalPosition = "1st"
    return render_template('mobile/End_Game_Page.html',group_name = groupName,final_score = finalScore,final_position = finalPosition)

@app.route('/HelpPage')
def loadHelpPage():
    return render_template('mobile/Help_Page.html')


#Runs the app locally if not deployed to the server
if __name__ == '__main__':
    app.secret_key = 'eXeplore_241199_brjbtk' 
    app.SECURITY_PASSWORD_SALT = 'BFR241199'
    app.run(host='0.0.0.0', port=port, debug=True,use_reloader=False)
