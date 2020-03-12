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
from itsdangerous import URLSafeTimedSerializer
from flask import Flask, render_template, redirect, url_for, request, send_file, session, jsonify,Blueprint, flash
from utils.auth import *
from flask_mail import Mail, Message
from utils.login import *
from databaseAdapter import *
from functools import wraps
import os
from werkzeug.utils import secure_filename
from blueprints.manageDashboard import dashboard_page
from blueprints.manageGame import game_page
from utils.utils import *

emailVer = False

app = Flask(__name__)
app.register_blueprint(dashboard_page)
app.register_blueprint(game_page)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]


TEAMS = {}
port = int(os.getenv('PORT', 8000))


# Handles the [post] method for login
# Will be passed a username and a password
@app.route('/', methods=['POST'])
def login_post():
    email = request.form.get('email').lower()
    password = request.form.get('password')
    print("email",email)
    print("password",password)
    # Checks the username and password are correct
    token = verifyUser(password, email)

    if (token['VerificationToken']):
        if not (getVerificationStatus(token['Role'],email))[0]['VERIFIED']:

            flash("You have not verified your email")
            return redirect(url_for('login'))

        # Sets the role of the user in the session
        if (token['Role'] == 'student'):
            session['Role'] = 'student'

            session['studentID'] = token['ID'][0]['STUDENT_ID']
            print("studentID",session['studentID'])

            teamID = getTeamFromStudentID(session['studentID'])
            #print(teamID)
            #studentID = getStudentID(email)
            #teamID = getTeamFromStudentID(studentID[0]['STUDENT_ID'])

            if len(teamID) == 0:
                #print("REDIRECT")
                return redirect(url_for('game_page.loadJoinTeamPage'))
            else:
                teamID = teamID[0]['TEAM_ID']
                session['teamID'] = teamID
                #print("TEAM ID",teamID)
                if getTeamLeader(session["teamID"])[0]['TEAM_LEADER'] == session['studentID']:
                    session['teamLeader'] = True
                else:
                    session['teamLeader'] = False

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

            session['progress'] = getStudentProgress(session['studentID'])#[0]['PROGRESS'] MAYBE UNCOMMENT THIS
            #print("num of questions ", session['numOfQuestions'])

        elif (token['Role'] == 'tutor'):
            session['Role'] = 'staff'


        if (session['Role'] == "staff"):
            # If staff redirect to the dashboard
            return redirect(url_for('dashboard_page.dashboard'))

        elif (session['Role'] == "student"):
            # If student redirect to the game
            return redirect(url_for('game_page.showLocationClue'))
    else:
        # If neither redirect to login page and send error message
        flash("User does not exist")
        return redirect(url_for('login'))


# This is the first page of the app currently the login page but we could add a splash screen if wanted
@app.route('/')
def login():
    return render_template('Desktop/Game_Keeper_Login.html')


# Load registration window
@app.route('/register')
def register():
    gameTutors = getTutors()
    return render_template('Desktop/register.html', tutors=gameTutors)

@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')

    if hasNumbers(email):
        userType = "student"
    else:
        userType = "tutor"
    if getVerificationStatus(userType,email)[0]['VERIFIED']:
        flash('Account already confirmed. Please login.', 'success')
    else:
        updateVerififcationStatus(userType,email,"TRUE")
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))

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
        flash("Passwords are not the same")
        return redirect(url_for('register'))
    # Check if the email is an exeter email
    if checkEmail(email):
        # Check if email has numbers if yes they must be a student
        if (hasNumbers(email)):
            # Check if the email is already registered
            if (len(getStudentID(email)) == 0):
                # Get the tutor ID for the current student
                tutorID = getTutorID(tutorName,email)

                if (len(tutorID) == 0):
                    flash("That tutor does not exist")
                    return redirect(url_for("register"))
                tutorID = tutorID[0]['TUTOR_ID']
                # Hash the password
                hashedPassword = hashPassword(password)
                # Insert the student to the database
                insertStudentUser(email, name, 'NULL', tutorID)

                # Insert the password to the database
                studentID = getStudentID(email)[0]['STUDENT_ID']
                insertPasswordStudent(hashedPassword, studentID)
                flash("Student registration successful")

                if emailVer:
                    token = generate_confirmation_token(email)
                    confirm_url = url_for('confirm_email', token=token, _external=True)
                    emailHtml = render_template('emailTemplate.html',confirm_url = confirm_url)
                    emailSubject = "Please Confirm Your eXeplore email"
                    send_email(email,emailSubject,emailHtml)
                else:
                    updateVerififcationStatus("student", email, "TRUE")
            else:
                # Catches if email is registered
                flash("Email is already in use")
                return redirect(url_for('register'))

        else:
            # Check if the email is already registered
            if (len(getTutorID(name,email)) == 0):
                # Also adds first team
                insertTutorUser(email, 1, name)
                hashedPassword = hashPassword(password)
                tutorID = getTutorID(name,email)[0]['TUTOR_ID']
                insertPasswordTutor(hashedPassword, tutorID)
                flash("Tutor registration successful", 'success')

                if emailVer:
                    token = generate_confirmation_token(email)
                    confirm_url = url_for('confirm_email', token=token, _external=True)
                    emailHtml = render_template('emailTemplate.html',confirm_url = confirm_url)
                    emailSubject = "Please Confirm Your eXeplore email"
                    send_email(email,emailSubject,emailHtml)
                else:
                    updateVerififcationStatus("tutor", email, "TRUE")

            else:
                flash("Email or tutor name is already in use")
                return redirect(url_for('register'))
        # Registration successful TODO add Success message
        return redirect(url_for('login'))
    # Catch email of wrong extension
    else:
        flash("Please use an email of extension "+EMAILEXTENSION)
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

# Redirect for Game Help Page
@app.route('/HelpPage')
def loadHelpPage():
    return render_template('mobile/Help_Page.html')

# Redirect for Google Map Page
@app.route('/Map')
def loadMap():
    return render_template('mobile/Map.html')

# Redirect for Game Leaderboard Page
@app.route('/Leaderboard')
def loadLeaderboardPage():
    gameTeams = getTeamsScores()
    return render_template('mobile/Leaderboard.html', teams=gameTeams)

# Redirect for Game FAQs Page
@app.route('/FAQPage')
def loadFAQPage():
	return render_template('mobile/FAQ_Page.html')

# Redirect for Game Resources Page
@app.route('/Resources')
def loadResourcesPage():
	return render_template('mobile/Resources.html')

# Redirect for Game Profile Page
@app.route('/ProfilePage')
def loadProfilePage():
    name = getStudentName(session['studentID'])[0]['NAME']
    tutor = getTutorNameFromStudentID(session['studentID'])[0]['TUTOR_NAME']
    team = getTeamFromStudentID(session['studentID'])[0]['TEAM_NAME']
    progress = session['progress']
    return render_template('mobile/Profile_Page.html', student_name=name, student_tutor=tutor, team_name=team, curr_progress=progress )


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

# Runs the app locally if not deployed to the server
if __name__ == '__main__':
    # insertTutorUser("testTutor@exeter.ac.uk",1,"TestTutor")
    # insertStudentUser("test201@exeter.ac.uk","TestBen",1,1)
    # insertTeam("TestTeam",1,1,1,0)
    # insertRoute(2,"Reverse")
    # insertScore(1,"Standard",1,100)
    # insertQuestion(9,"What does the sign behind the cafe say?","Physics is the universes operating system","Im with stupid","We have a latte fun","Flavour by nature","D")
    app.secret_key = 'eXeplore_241199_brjbtk'
    app.config.update(SECURITY_PASSWORD_SALT = 'BFR241199')
    app.config.update(MAIL_SERVER = 'smtp.googlemail.com')
    app.config.update(MAIL_PORT = 465)
    app.config.update(MAIL_USE_TLS = False)
    app.config.update(MAIL_USE_SSL = True)

    # gmail authentication
    app.config.update(MAIL_USERNAME = "exeploregeneral")
    app.config.update(MAIL_PASSWORD = "24BBT11TR99")

    # mail accounts
    app.config.update(MAIL_DEFAULT_SENDER='exeploregeneral@example.com')
    mail = Mail(app)

    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)