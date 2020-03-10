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
from flask import render_template, redirect, url_for, request, send_file, session, jsonify, Blueprint
from utils.auth import *
from utils.login import *
from databaseAdapter import *
from functools import wraps
import os
from werkzeug.utils import secure_filename

from utils.utils import *
######################
# GAMEKEEPER DASHBOARD#
######################
dashboard_page = Blueprint('dashboard_page',__name__,template_folder='templates')



# Used to restrict access to ceratin site areas
def requires_access_level(access_level):
    # Uses a decorator function
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # if the session users role is not set send to login page
            if not session.get('Role'):
                return redirect(url_for('login'))
            # If the users session role is not high enough send them to the game page
            # They must be a student
            elif not session.get('Role') == access_level:
                return redirect(url_for('showLocationClue'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator

# Loads the dashboard for game masters
@dashboard_page.route('/dashboard')
@requires_access_level('staff')
def dashboard():
    return render_template('Desktop/Game_Keeper_Page.html')


# Loads the add location form page
@dashboard_page.route('/Add_Location')
@requires_access_level('staff')
def addLocation():
    return render_template('Desktop/add_location_page.html')





def allowedImage(filename):
    if not "." in filename:
        return False

    extension = filename.rsplit(".", 1)[1]
    if extension.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


@dashboard_page.route('/Add_Location_Submit', methods=['POST'])
@requires_access_level('staff')
def addLocationSubmit():
    location = request.form.get('location')
    clue = request.form.get('clue')

    photo = request.files['location_photo']

    if photo.filename == "":
        print("Image must have a filename")
        return redirect(url_for('dashboard_page.dashboard'))

    if not allowedImage(photo.filename):
        print("Image extension is not allowed")
        return redirect(url_for('dashboard_page.dashboard'))
    else:
        filename = secure_filename(photo.filename)

        photo.save(os.path.join("static/images", photo.filename))

    # No checks
    insertLocation(location, clue, photo.filename)

    return redirect(url_for('dashboard_page.dashboard'))


@dashboard_page.route('/Add_Question')
@requires_access_level('staff')
def addQuestion():
    gameLocations = getLocations()
    return render_template('Desktop/Add_Question_Page.html', locations=gameLocations)


@dashboard_page.route('/Add_Question_Submit', methods=['POST'])
@requires_access_level('staff')
def addQuestionSubmit():
    location = request.form.get('location')
    question = request.form.get('question')
    answer_a = request.form.get('answer_a')
    answer_b = request.form.get('answer_b')
    answer_c = request.form.get('answer_c')
    answer_d = request.form.get('answer_d')
    correct_answer = request.form.get('correct_answer')
    # No checks for now
    insertQuestion(location, question, answer_a, answer_b, answer_c, answer_d, correct_answer)

    return redirect(url_for('dashboard_page.dashboard'))


@dashboard_page.route('/Delete_Location', methods=['POST'])
@requires_access_level('staff')
def deleteLocation():
    name = request.form.get('locations')
    removeLocation(name)
    locationNames = []
    locations = getLocations()
    locationNames = []
    for location in locations:
        locationNames.append(location['LOCATION_NAME'])

    return redirect(url_for('dashboard_page.dashboard'))


# Loads the gamekeepers dashboard tool
@dashboard_page.route('/Manage_Locations_Page')
@requires_access_level('staff')
def manageLocations():
    # Creates a list of locations from the db
    locations = getLocations()
    locationNames = []
    for location in locations:
        locationNames.append(location['LOCATION_NAME'])

    return render_template('Desktop/Manage_Locations_Page.html', locations=locationNames)


# Loads the gamekeepers dashboard tool
@dashboard_page.route('/Manage_Groups_Page')
@requires_access_level('staff')
def manageGroups():
    # Creates a list of locations from the db
    studentNames = getStudents()

    return render_template('Desktop/Manage_Groups_Page.html', students=studentNames)

    return render_template('Desktop/Manage_Groups_Page.html', students=studentNames)


# Loads the gamekeepers dashboard tool
@dashboard_page.route('/Leaderboard_Page')
def leaderboard():
    print("IN THE LEADERBOARD ROUTE")
    routes = getRoutes()
    return render_template('Desktop/Leaderboard_Page.html', routes=routes)


@dashboard_page.route('/Leaderboard_process', methods=['POST'])
def process():
    print("IN THE LEADERBOARD_PROCESS ROUTE")
    route_selected = request.form['route']
    teams = getTeamScoresFromRouteID(route_selected)

    return jsonify(teams)


# Loads the gamekeepers dashboard tool
@dashboard_page.route('/Manage_Routes_Page')
@requires_access_level('staff')
def manageRoutes():
    return render_template('Desktop/Manage_Routes_Page.html')


# Loads the gamekeepers dashboard tool
@dashboard_page.route('/Assign_Routes_Page')
@requires_access_level('staff')
def assignRoutes():
    gameTeams = getTeams()
    gameRoutes = getRoutes()

    return render_template('Desktop/Assign_Routes_Page.html', teams=gameTeams, routes=gameRoutes)


@dashboard_page.route('/assignRoute', methods=['POST'])
@requires_access_level('staff')
def assignUpdateRoute():
    teamNameID = request.form['team']
    routeNameID = request.form.get('route')
    updateTeamRoute(routeNameID, 0, teamNameID)

    return redirect(url_for('dashboard_page.assignRoutes'))