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
Updated doc strings

This file contains all the data regarding the dashboard funcctionality
"""
from flask import render_template, redirect, url_for, request, send_file, session, jsonify, Blueprint, flash
from databaseAdapter import *
from functools import wraps
import os
from werkzeug.utils import secure_filename

######################
# GAMEKEEPER DASHBOARD#
######################
#Sets up this page as a blueprint
dashboard_page = Blueprint('dashboard_page',__name__,template_folder='templates')

app = Flask(__name__)


def requires_access_level(access_level):
    """
    Decorator function use to lock parts of the site so that only staff memebers can gain access
    :return: Allows access if staff, redirects to login if user not logged in
    , redirects to game if user isstudent
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # if the session users role is not set send to login page
            if not session.get('Role'):
                return redirect(url_for('login'))
            # If the users session role is not high enough send them to the game page
            # They must be a student
            elif not session.get('Role') == access_level:
                return redirect(url_for('game_page.showLocationClue'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@dashboard_page.route('/dashboard')
@requires_access_level('staff')
def dashboard():
    """
    Loads the game keeper dashboard main page
    :return: Game keeper dashboard html
    """
    return render_template('Desktop/Game_Keeper_Page.html')



@dashboard_page.route('/Add_Location')
@requires_access_level('staff')
def addLocation():
    """
    Serves the addlocation screen
    :return: Add location html
    """
    return render_template('Desktop/add_location_page.html')


@dashboard_page.route('/Add_Location_Submit', methods=['POST'])
@requires_access_level('staff')
def addLocationSubmit():
    """
    Add a new location to the game
    :return: redirect to dashboard main screen with flash message
    """
    #Get form entry
    location = request.form.get('location')
    clue = request.form.get('clue')
    photo = request.files['location_photo']

    #Check if image has a file name
    if photo.filename == "":
        flash("Image must have a filename")
        return redirect(url_for('dashboard_page.dashboard'))
    #Check file is an image extension
    if not allowedImage(photo.filename):
        flash("Image extension is not allowed")
        return redirect(url_for('dashboard_page.dashboard'))
    #Save the image to the server and stor the name in the DB
    else:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join("static/images", photo.filename))

    # No checks
    insertLocation(location, clue, photo.filename)
    flash("Location "+location+" has successfully been added")

    return redirect(url_for('dashboard_page.dashboard'))


@dashboard_page.route('/Add_Question')
@requires_access_level('staff')
def addQuestion():
    """
    Serves the add location screen
    :return: add location html
    """
    gameLocations = getLocations()
    return render_template('Desktop/Add_Question_Page.html', locations=gameLocations)


@dashboard_page.route('/Add_Question_Submit', methods=['POST'])
@requires_access_level('staff')
def addQuestionSubmit():
    """
    Adds new question to the Db
    :return: the dashboard_page
    """
    location = request.form.get('location')
    question = request.form.get('question')
    answer_a = request.form.get('answer_a')
    answer_b = request.form.get('answer_b')
    answer_c = request.form.get('answer_c')
    answer_d = request.form.get('answer_d')
    correct_answer = request.form.get('correct_answer')
    # No checks for now
    insertQuestion(location, question, answer_a, answer_b, answer_c, answer_d, correct_answer)
    flash("Question has successfully been added")

    return redirect(url_for('dashboard_page.dashboard'))


@dashboard_page.route('/Delete_Location', methods=['POST'])
@requires_access_level('staff')
def deleteLocation():
    """
    Delete a location from the database
    :return: dashboard page
    """

    name = request.form.get('locations')
    removeLocation(name)
    locationNames = []
    locations = getLocations()
    locationNames = []
    for location in locations:
        locationNames.append(location['LOCATION_NAME'])

    return redirect(url_for('dashboard_page.dashboard'))



@dashboard_page.route('/Manage_Locations_Page')
@requires_access_level('staff')
def manageLocations():
    """
    Loads the manage location page with al the locations
    :return: object
    """
    # Creates a list of locations from the db
    locations = getLocations()
    locationNames = []
    for location in locations:
        locationNames.append(location['LOCATION_NAME'])

    return render_template('Desktop/Manage_Locations_Page.html', locations=locationNames)


# Loads the manage groups dashboard tool
@dashboard_page.route('/Manage_Groups_Page')
@requires_access_level('staff')
def manageGroups():
    """
    Show the manage groups page displaying all the groups teams and students
    :return: the manage groups template
    """
    tutors = getTutors()
    teams = getTeams()
    students = getStudents()

    return render_template('Desktop/Manage_Groups_Page.html', tutors=tutors, teams=teams, students=students)



@dashboard_page.route('/assignTeamLeader', methods=['POST'])
@requires_access_level('staff')
def assignUpdateTeamLeader():
    """
    Assign a new team leader to a team
    :return: Returns the dashboard with a confimartion message
    """
    teamID = request.form['team']
    studentID = request.form.get('student')
    name = getStudentName(studentID)[0]['NAME']

    team = getTeamFromStudentID(studentID)[0]['TEAM_NAME']
    #Set the new team leader
    updateTeamLeader(studentID, teamID)
    flash(name+' has been assigned as the team leader for team: '+team)
    return redirect(url_for('dashboard_page.dashboard'))



@dashboard_page.route('/Leaderboard_Page')
@requires_access_level('staff')
def leaderboard():
    """
    Load the leaderboard
    :return: leaderboard html
    """
    routes = getRoutes()
    return render_template('Desktop/Leaderboard_Page.html', routes=routes)

@dashboard_page.route('/Show_Leader_Board', methods=['POST'])
@requires_access_level('staff')
def process():
    """
    Filter the leaderboard based on route selected
    :return: json object containg team scores for given route
    """
    routeID = request.form['routeID']
    teams = getTeamScoresFromRouteID(routeID)

    return jsonify(teams)




@dashboard_page.route('/Manage_Routes_Page')
@requires_access_level('staff')
def manageRoutes():
    """
    Load the manage routes page giveing access to all the route data
    :return: the manageroutes.html
    """
    locationData = getLocations()
    locations = []
    for location in locationData :
        locations.append(location['LOCATION_NAME'])

    routeData = getRoutes()
    routes = []
    for route in routeData :
        routes.append(route['ROUTE_NAME'])

    return render_template('Desktop/Manage_Routes_Page.html', locations = locations, routes = routes)


# Functionality for creating a route from locations in the database
@dashboard_page.route('/Add_Route_Submit', methods=['POST'])
@requires_access_level('staff')
def addRouteSubmit():
    """
    Very basic implementation of the add route function
    Adds a route (location,question,order) to the dabase
    :return: object
    """
    #TODO completely redo this function
    form = request.form

    routeName = request.form.get('create_route_input')
    location1 = request.form.get('location_1')
    question1 = request.form.get('question_1')
    location2 = request.form.get('location_2')
    question2 = request.form.get('question_2')
    location3 = request.form.get('location_3')
    question3 = request.form.get('question_3')
    location4 = request.form.get('location_4')
    question4 = request.form.get('question_4')
    location5 = request.form.get('location_5')
    question5 = request.form.get('question_5')
    location6 = request.form.get('location_6')
    question6 = request.form.get('question_6')
    location7 = request.form.get('location_7')
    question7 = request.form.get('question_7')
    location8 = request.form.get('location_8')
    question8 = request.form.get('question_8')
    location9 = request.form.get('location_9')
    question9 = request.form.get('question_9')
    location10 = request.form.get('location_10')
    question10 = request.form.get('question_10')



    if location1 == "n/a":
        flash("You arent adding locations")
    elif location2 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
    elif location3 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
    elif location4 == "n/a":

        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
    elif location5 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
    elif location6 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location5)[0]['LOCATION_ID'], 4, getQuestionID(question5)[0]['QUESTION_ID'])
    elif location7 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location5)[0]['LOCATION_ID'], 4, getQuestionID(question5)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location6)[0]['LOCATION_ID'], 5, getQuestionID(question6)[0]['QUESTION_ID'])
    elif location8 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location5)[0]['LOCATION_ID'], 4, getQuestionID(question5)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location6)[0]['LOCATION_ID'], 5, getQuestionID(question6)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location7)[0]['LOCATION_ID'], 6, getQuestionID(question7)[0]['QUESTION_ID'])
    elif location9 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location5)[0]['LOCATION_ID'], 4, getQuestionID(question5)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location6)[0]['LOCATION_ID'], 5, getQuestionID(question6)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location7)[0]['LOCATION_ID'], 6, getQuestionID(question7)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location8)[0]['LOCATION_ID'], 7, getQuestionID(question8)[0]['QUESTION_ID'])
    elif location10 == "n/a":
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location5)[0]['LOCATION_ID'], 4, getQuestionID(question5)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location6)[0]['LOCATION_ID'], 5, getQuestionID(question6)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location7)[0]['LOCATION_ID'], 6, getQuestionID(question7)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location8)[0]['LOCATION_ID'], 7, getQuestionID(question8)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location9)[0]['LOCATION_ID'], 8, getQuestionID(question9)[0]['QUESTION_ID'])
    else:
        insertRoute(routeName)
        routeID = getRouteIDFromRouteName(routeName)[0]['ROUTE_ID']
        insertRouteSequence(routeID, getLocationID(location1)[0]['LOCATION_ID'], 0, getQuestionID(question1)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location2)[0]['LOCATION_ID'], 1, getQuestionID(question2)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location3)[0]['LOCATION_ID'], 2, getQuestionID(question3)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location4)[0]['LOCATION_ID'], 3, getQuestionID(question4)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location5)[0]['LOCATION_ID'], 4, getQuestionID(question5)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location6)[0]['LOCATION_ID'], 5, getQuestionID(question6)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location7)[0]['LOCATION_ID'], 6, getQuestionID(question7)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location8)[0]['LOCATION_ID'], 7, getQuestionID(question8)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location9)[0]['LOCATION_ID'], 8, getQuestionID(question9)[0]['QUESTION_ID'])
        insertRouteSequence(routeID, getLocationID(location10)[0]['LOCATION_ID'], 9, getQuestionID(question10)[0]['QUESTION_ID'])


    return redirect(url_for('dashboard_page.dashboard'))


@dashboard_page.route('/Display_Questions', methods=['POST'])
@requires_access_level('staff')
def displayQuestions():

    locationName = request.form['locationName']
    locationID = getLocationID(locationName)
    questionData = getQuestionLocationID(locationID[0]['LOCATION_ID'])
    questions = []

    for question in questionData :
        questions.append(question['QUESTION_CONTENT'])

        separator = "','"
        json = "{'questions' : ['" + separator.join(questions) + "'], LOCATION_ID : }"

        return jsonify(questions)


@dashboard_page.route('/Assign_Routes_Page')
@requires_access_level('staff')
def assignRoutes():
    """
    Loadds the asign routes page
    :return:
    """
    gameTeams = getTeams()
    gameRoutes = getRoutes()

    return render_template('Desktop/Assign_Routes_Page.html', teams=gameTeams, routes=gameRoutes)



@dashboard_page.route('/assignRoute', methods=['POST'])
@requires_access_level('staff')
def assignUpdateRoute():
    """
    Set the route for a given team to a given route
    :return: change the databse
    """
    teamNameID = request.form['team']
    routeNameID = request.form.get('route')
    updateTeamRoute(routeNameID, 0, teamNameID)

    return redirect(url_for('dashboard_page.dashboard'))


# Redirect for Dashboard FAQs Page
@dashboard_page.route('/FAQGameKeeper')
@requires_access_level('staff')
def loadFAQGameKeeperPage():

	return render_template('Desktop/FAQ_Staff_page.html')


# Redirect for Change Language Page
@dashboard_page.route('/Language')
@requires_access_level('staff')
def loadLanguagePage():
    return render_template('Desktop/Change_Lang_Page.html')


def allowedImage(filename):
    """
    Checks if the file uploaded is of the correct extension
    :return: True if file is of correct extension
    """
    if not "." in filename:
        return False

    extension = filename.rsplit(".", 1)[1]
    if extension.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False