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
from flask import render_template, redirect, url_for, request, send_file, session, jsonify,Blueprint
from utils.auth import *
from utils.login import *
from databaseAdapter import *
from functools import wraps
import os
from werkzeug.utils import secure_filename
from blueprints.manageDashboard import dashboard_page
from blueprints.manageGame import game_page
from utils.utils import *

app = Flask(__name__)
app.register_blueprint(dashboard_page)
app.register_blueprint(game_page)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]


port = int(os.getenv('PORT', 8000))

# Handles the [post] method for login
# Will be passed a username and a password
@app.route('/', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    # Checks the username and password are correct
    token = verifyUser(password, email)

    if (token['VerificationToken']):
        # Sets the role of the user in the session
        if (token['Role'] == 'student'):
            session['Role'] = 'student'

            session['studentID'] = token['ID'][0]['STUDENT_ID']
            # get group ID

            teamID = getTeamFromStudentID(session['studentID'])
            print(teamID)

            if len(teamID) == 0:
                print("REDIRECT")
                return redirect(url_for('game_page.loadJoinTeamPage'))
            else:
                teamID = teamID[0]['TEAM_ID']
                session['teamID'] = teamID
            teamLeader = getTeamLeader(teamID)

            if teamLeader[0]['TEAM_LEADER'] is None:
                updateTeamLeader(session['studentID'], teamID)
                return redirect(url_for('game_page.loadFirstChoosePage'))

            # get the ID of the route the students are on
            routeID = getRouteID(session['teamID'])
            session['routeID'] = routeID[0]['CURRENT_ROUTE_ID']
            # Get the total number of questions so end screen can be displayed at the end
            numOfQuestions = getNumLocationOnRoute(session['routeID'])
            session['numOfQuestions'] = numOfQuestions[0]['1']
            session['teamScore'] = 100
            print("num of questions ", session['numOfQuestions'])

        elif (token['Role'] == 'tutor'):
            session['Role'] = 'staff'

    else:
        session['loginerror'] = "User does not exist"
        session['Role'] = 'NO_ROLE'

    print(session['Role'])
    if (session['Role'] == "staff"):
        # If staff redirect to the dashboard
        return redirect(url_for('dashboard_page.dashboard'))

    elif (session['Role'] == "student"):
        # If student redirect to the game
        return redirect(url_for('game_page.showLocationClue'))
    else:
        # If neither redirect to login page
        return redirect(url_for('login'))


# This is the first page of the app currently the login page but we could add a splash screen if wanted
@app.route('/')
def login():
    if 'loginerror' in session:
        errormessage = session['loginerror']
    else:
        errormessage = ""
        session['loginerror'] = ""
    session.clear()
    return render_template('Desktop/Game_Keeper_Login.html', error_message=errormessage)


# Load registration window
@app.route('/register')
def register():
    gameTutors = getTutors()
    # Checks if there is an error message is sent via a redirect
    if ('Error Message' in session):
        # dosplay the message
        errorMessage = session['Error Message']
    else:
        # If no message set set the message to be empty (No message)
        session['Error Message'] = ""
        errorMessage = ""
        # Redner the register page with the errormessage variable passes in
    return render_template('Desktop/register.html', error_message=errorMessage, tutors=gameTutors)


# Handles registration
@app.route('/registerSubmit', methods=['POST'])
def registerSubmit():
    global EMAILEXTENSION
    name = request.form.get('name')
    email = request.form.get('email')
    name = name.lower()
    email = email.lower()
    password = request.form.get('password')
    passwordConfirm = request.form.get('passwordConfirmation')
    tutorName = request.form.get('tutorName')
    # Check if passwords match if not reload page with error message
    if (password != passwordConfirm):
        session['Error Message'] = "Passwords are not the same"
        return redirect(url_for('register'))
    # Check if the email is an exeter email
    if checkEmail(email):
        # Check if email has numbers if yes they must be a student
        if (hasNumbers(email)):
            # Check if the email is already registered
            if (len(getStudentID(email)) == 0):
                # Get the tutor ID for the current student
                tutorID = getTutorID(tutorName)

                if (len(tutorID) == 0):
                    session['Error Message'] = ("That tutor does not exist")
                    return redirect(url_for("register"))
                tutorID = tutorID[0]['TUTOR_ID']
                # Hash the password
                hashedPassword = hashPassword(password)
                # Insert the student to the database
                # TODO fix/figure out how to send null
                insertStudentUser(email, name, 'NULL', tutorID)

                # Insert the password to the database
                studentID = getStudentID(email)[0]['STUDENT_ID']
                insertPasswordStudent(hashedPassword, studentID)
            else:
                # Catches if email is registered
                session['Error Message'] = ("Email is already used")
                return redirect(url_for('register'))

        else:
            # Check if the email is already registered
            if (len(getTutorID(name)) == 0):
                # Also adds first team
                insertTutorUser(email, 1, name)
                hashedPassword = hashPassword(password)
                tutorID = getTutorID(name)[0]['TUTOR_ID']
                insertPasswordTutor(hashedPassword, tutorID)
            else:
                session['Error Message'] = ("Email is already used")
                return redirect(url_for('register'))
        # Registration successful TODO add Success message
        session['loginerror'] = "registration successful"
        print(session)
        return redirect(url_for('login'))
    # Catch email of wrong extension
    else:
        session['Error Message'] = ("Please use an email of extension " + EMAILEXTENSION)
        return redirect(url_for('register'))


# Will redirect uses back to the login page if they fail the login procedure
@app.route('/redirect')
def redirectLogin():
    return render_template('Game_s_Keeper_Login.html')


@app.route('/Logout')
def logout():
    if 'resetTeamFlag' in session:
        if session['resetTeamFlag']:
            teamID = session['teamID']
            updateTeamLeader("null", teamID)
            updateTeamRoute("null", 0, teamID)
    session.clear()
    return redirect(url_for('login'))


@app.route('/images/Exeter_University.jpg')
def imageUni():
    return send_file('static/images/Exeter_University.jpg', mimetype='image/jpg')


@app.route('/static/Exeter_University.jpg')
def imageUniStatic():
    u = 2
    return send_file('static/images/Exeter_University.jpg', mimetype='image/jpg')





@app.route('/HelpPage')
def loadHelpPage():
    return render_template('mobile/Help_Page.html')


@app.route('/Map')
def loadMap():
    return render_template('mobile/Map.html')


@app.route('/Leaderboard')
def loadLeaderboardPage():
    gameTeams = getTeams()
    return render_template('mobile/Leaderboard.html', teams=gameTeams)


# Runs the app locally if not deployed to the server
if __name__ == '__main__':
    # insertTutorUser("testTutor@exeter.ac.uk",1,"TestTutor")
    # insertStudentUser("test201@exeter.ac.uk","TestBen",1,1)
    # insertTeam("TestTeam",1,1,1,0)
    # insertRoute(2,"Reverse")
    # insertScore(1,"Standard",1,100)
    # insertQuestion(9,"What does the sign behind the cafe say?","Physics is the universes operating system","Im with stupid","We have a latte fun","Flavour by nature","D")
    app.secret_key = 'eXeplore_241199_brjbtk'
    app.SECURITY_PASSWORD_SALT = 'BFR241199'
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
