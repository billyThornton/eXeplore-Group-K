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
@Last Edited: 12/03/2020
@edited by: Billy Thornton
Updated comments

This file contains all the routing and backend handling for the user login section of the site
Handles email verification send an check as well
"""
from itsdangerous import URLSafeTimedSerializer
import os
from flask import Flask, render_template, redirect, url_for, request, send_file, session, Blueprint, flash
from utils.auth import *
from flask_mail import Mail, Message
from databaseAdapter import *
from blueprints.manageDashboard import dashboard_page
from blueprints.manageGame import game_page
from utils.utils import *


with open('servicesConfig.json') as json_file:
    data = json.load(json_file)
    data['dashDB For Transactions'][0]['credentials']

emailVer = True;


app = Flask(__name__)
app.register_blueprint(dashboard_page)
app.register_blueprint(game_page)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["PNG", "JPG", "JPEG"]

port = int(os.getenv('PORT', 8000))


# Handles the [post] method for login
# Will be passed a username and a password
@app.route('/', methods=['POST'])
def login_post():
    """
    Handles a user login, sets up the session and verifiers username and password
    Session Setup includes:
    session[]: Role, studentID, teamID, teamLeader, routeID, startingScore, numOfQuestions, progress
    :return: redirect to another URL dependent on login outcome
    """
    email = request.form.get('email').lower()
    password = request.form.get('password')
    
    # Checks the username and password are correct
    token = verifyUser(password, email)

    #If verification is successful
    if (token['VerificationToken']):

        #Check if the users email is verified
        if not (getVerificationStatus(token['Role'], email))[0]['VERIFIED']:

            flash("You have not verified your email")
            return redirect(url_for('login'))

        # Sets the role of the user in the session
        if (token['Role'] == 'student'):
            #Set this sessions user type
            session['Role'] = 'student'

            session['studentID'] = token['ID'][0]['STUDENT_ID']

            teamID = getTeamFromStudentID(session['studentID'])
            #If the len of the teamID result set is 0 the team hasnt been set for the user
            if len(teamID) == 0:
                return redirect(url_for('game_page.loadJoinTeamPage'))



            teamID = teamID[0]['TEAM_ID']
            session['teamID'] = teamID

            teamLeader = getTeamLeader(teamID)
            #Team leader isnt set set current user to team leader
            if teamLeader[0]['TEAM_LEADER'] is None:
                updateTeamLeader(session['studentID'], teamID)
                return redirect(url_for('game_page.loadFirstChoosePage'))

            else:
                # Check if this user is the team leader for the team they belong to
                if teamLeader[0]['TEAM_LEADER'] == session['studentID']:
                    session['teamLeader'] = True
                    session['teamScore'] = 100
                else:
                    session['teamLeader'] = False

            # get the ID of the route the students are on
            routeID = getRouteID(session['teamID'])
            session['routeID'] = routeID[0]['CURRENT_ROUTE_ID']
            # Get the total number of questions so end screen can be displayed at the end
            numOfQuestions = getNumLocationOnRoute(session['routeID'])
            session['numOfQuestions'] = numOfQuestions[0]['1']
            return redirect(url_for('game_page.showLocationClue'))

        elif (token['Role'] == 'tutor'):
            session['Role'] = 'staff'
            return redirect(url_for('dashboard_page.dashboard'))

    else:
        # If neither redirect to login page and send error message
        flash("User does not exist")
        return redirect(url_for('login'))


@app.route('/')
def login():
    """
    The initial page for the app
    :return: Redirect to the login page
    """
    return render_template('Desktop/Game_Keeper_Login.html')


# Load registration window
@app.route('/register')
def register():
    """
    Load the register screen
    :return: Returns the registerscreen with a list of all active tutors
    """
    gameTutors = getTutors()
    return render_template('Desktop/register.html', tutors=gameTutors)


@app.route('/confirm/<token>')
def confirm_email(token):
    """
    This is the url that you get redirected to in an email verification link
    It checks if you the token is correct and verifies the user
    :return: flash message reflecting status
    """
    try:
        #Check if the token is valid
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    #Check if email belongs to a student or staff
    if hasNumbers(email):
        userType = "student"
    else:
        userType = "tutor"
    #Check if the user is already verified
    if getVerificationStatus(userType, email)[0]['VERIFIED']:
        flash('Account already confirmed. Please login.', 'success')
    else:
        updateVerififcationStatus(userType, email, "TRUE")
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))



@app.route('/registerSubmit', methods=['POST'])
def registerSubmit():
    """
    Handles the user registration screen registering users and storing their password in hashed form
    Sends the verification email
    :return: Flash and redirect
    """
    global EMAILEXTENSION
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    passwordConfirm = request.form.get('passwordConfirmation')
    tutorName = request.form.get('tutorName')

    name = name.lower()
    email = email.lower()


    # Check if passwords match if not reload page with error message
    if password != passwordConfirm:
        flash("Passwords are not the same")
        return redirect(url_for('register'))

    # Check if the email is an exeter email
    if not checkEmail(email):
        flash("Please use an email of extension " + EMAILEXTENSION)
        return redirect(url_for('register'))

    # Check if email has numbers if yes they must be a student
    if hasNumbers(email):
        # Check if the email is already registered
        if len(getStudentID(email)) > 0:
            # Catches if email is registered
            flash("Email is already in use")
            return redirect(url_for('register'))

        # Get the tutor ID for the current student
        tutorID = getTutorID(tutorName, email)

        if len(tutorID) == 0:
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

        #If email verification enabled
        if not emailVer:
            updateVerififcationStatus("student", email, "TRUE")

    else:
        # Check if the email is already registered
        if len(getTutorID(name, email)) > 0:
            flash("Email or tutor name is already in use")
            return redirect(url_for('register'))

        # Also adds first team
        insertTutorUser(email, 1, name)

        hashedPassword = hashPassword(password)
        tutorID = getTutorID(name, email)[0]['TUTOR_ID']
        insertPasswordTutor(hashedPassword, tutorID)

        flash("Tutor registration successful", 'success')

        # If email verification enabled
        if not emailVer:
            updateVerififcationStatus("tutor", email, "TRUE")
    if emailVer:
        #Send verification Email
        token = generate_confirmation_token(email)
        #Custom redirect url
        confirm_url = url_for('confirm_email', token=token, _external=True)
        #Html template for the email
        emailHtml = render_template('emailTemplate.html', confirm_url=confirm_url)
        emailSubject = "Please Confirm Your eXeplore email"
        send_email(email, emailSubject, emailHtml)
    return redirect(url_for('login'))


@app.route('/Logout')
def logout():
    """
    On logout we clear all the session values of the user
    We also reset the team information (leader and route) if the reset flag is set
    (IF the end of the game is reached)
    :return: redirect to login screen
    """
    if 'resetTeamFlag' in session:
        if session['resetTeamFlag']:
            teamID = session['teamID']
            updateTeamLeader("null", teamID)
            updateTeamRoute("null", 0, teamID)
    session.clear()
    return redirect(url_for('login'))


@app.route('/images/Exeter_University.jpg')
def imageUni():
    """
    Used to serve an image
    :return: Serves the Exeter_university image
    """
    return send_file('static/images/Exeter_University.jpg', mimetype='image/jpg')


@app.route('/static/Exeter_University.jpg')
def imageUniStatic():
    """
        Used to serve an image
        :return: Serves the Exeter_university image
    """
    u = 2
    return send_file('static/images/Exeter_University.jpg', mimetype='image/jpg')

@app.route('/HelpPage')
def loadHelpPage():
    """
    Used by the toolbar to load the help page
    :return: Loads the help page
    """
    return render_template('mobile/Help_Page.html')



@app.route('/Map')
def loadMap():
    """
    Redirects to the google map page from the toolbar
    :return: loads the map page
    """
    return render_template('mobile/Map.html')

@app.route('/Leaderboard')
def loadLeaderboardPage():
    """
    Loads the scores of all teams from the database and loads it into the leaderboard
    :return: Redirects to the laderboard with the scores of all teams
    """
    gameTeams = getTeamsScores()
    return render_template('mobile/Leaderboard.html', teams=gameTeams)


@app.route('/FAQPage')
def loadFAQPage():
    """
    Redirects to the FAQ page
    :return: FAQ page redirect
    """
    return render_template('mobile/FAQ_Page.html')


@app.route('/Resources')
def loadResourcesPage():
    """
        Redirects to the FAQ page
        :return: resources page redirect
    """
    return render_template('mobile/Resources.html')



@app.route('/ProfilePage')
def loadProfilePage():
    """
    Loads the user profile Page with all the info of the current user
    :return: Redirects to the profile page with relevant data loaded
    """
    name = getStudentName(session['studentID'])[0]['NAME']
    tutor = getTutorNameFromStudentID(session['studentID'])[0]['TUTOR_NAME']
    team = getTeamFromStudentID(session['studentID'])[0]['TEAM_NAME']
    progress = session['progress']

    return render_template('mobile/Profile_Page.html', student_name=name, student_tutor=tutor, team_name=team,
                           curr_progress=progress)


def send_email(to, subject, template):
    """
    Sends a verification email using flask_mail
    :return: A email to send
    """
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


def generate_confirmation_token(email):
    """
    Generates a unique token to redirect to for the email verification system
    :return: a unique token including the users email
    """
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    """
    Checks to ensure the toke is valid if it is retrieves the email hidden in the token
    :return: Email string if valid false if not
    """
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



if __name__ == '__main__':
    app.secret_key = data['Security'][0]['credentials']['secret_key']
    app.config.update(SECURITY_PASSWORD_SALT = data['Email settings'][0]['credentials']['security_password_salt'])
    app.config.update(MAIL_SERVER = data['Email settings'][0]['credentials']['mail_server'])
    app.config.update(MAIL_PORT = data['Email settings'][0]['credentials']['mail_port'])
    app.config.update(MAIL_USE_TLS = data['Email settings'][0]['credentials']['mail_use_tls'])
    app.config.update(MAIL_USE_SSL = data['Email settings'][0]['credentials']['mail_use_ssl'])

    print(data['Email settings'][0]['credentials']['mail_server'])
    # gmail authentication
    app.config.update(MAIL_USERNAME = data['Email settings'][0]['credentials']['mail_username'])
    app.config.update(MAIL_PASSWORD = data['Email settings'][0]['credentials']['mail_password'])

    # mail accounts
    app.config.update(MAIL_DEFAULT_SENDER = data['Email settings'][0]['credentials']['mail_default_sender'])
    mail = Mail(app)

    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
