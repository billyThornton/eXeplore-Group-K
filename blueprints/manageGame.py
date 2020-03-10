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
from utils.utils import *

game_page = Blueprint('game_page',__name__,template_folder='templates')



######################
# Student Game Pages  #
######################

@game_page.route('/Join')
def loadJoinTeamPage():
    gameTeams = getTeams()
    gameTutors = getTutors()
    return render_template('mobile/Join_Team.html', teams=gameTeams, tutors=gameTutors)


@game_page.route('/assignTeam', methods=['POST'])
def assignTeam():
    print("TEAM ASSIGN START")
    # TODO update the student to store updated  tutorID?
    studentID = session['studentID']
    tutorID = request.form['tutor']
    print(tutorID)
    teamID = request.form.get('team')
    session['teamID'] = teamID
    print(teamID)
    updateStudentTeam(studentID, teamID)
    teamLeader = getTeamLeader(teamID)
    print("Team Leader")
    print(teamLeader)
    if teamLeader[0]['TEAM_LEADER'] is None:
        updateTeamLeader(studentID, teamID)
        return redirect(url_for('game_page.loadFirstChoosePage'))
    else:
        # TODO wait here until route selected by team leader
        routeID = getRouteID(session['teamID'])
        while routeID[0]['CURRENT_ROUTE_ID'] is None:
            routeID = getRouteID(session['teamID'])

        session['routeID'] = routeID[0]['CURRENT_ROUTE_ID']
        return redirect(url_for('game_page.showLocationClue'))


@game_page.route('/firstChoose')
def loadFirstChoosePage():
    gameRoutes = getRoutes();
    return render_template('mobile/First_Choose.html', routes=gameRoutes)


@game_page.route('/routeSelect', methods=['POST'])
def routeSelect():
    routeID = request.form['route']
    teamName = request.form['teamName']
    teamID = session['teamID']
    session['routeID'] = routeID
    updateTeamRoute(routeID, 0, teamID)
    updateTeamName(teamName, teamID)
    numOfQuestions = getNumLocationOnRoute(session['routeID'])
    session['numOfQuestions'] = numOfQuestions[0]['1']
    return redirect(url_for('game_page.showLocationClue'))


# Displays the location clue page at an appropriate progression point

@game_page.route('/loadFirstTeam', methods=['POST'])
def loadFirstTeam():
    routeID = request.form['route']
    teamName = request.form['teamName']
    # add or update database now here maybe
    return redirect(url_for('game_page.showLocationClue'))


# Displays the location clue page at an appropriate progression point
@game_page.route('/Game')
def showLocationClue():
    # get progress from db
    if 'progress' in session:
        progress = session['progress']
    else:
        session['progress'] = 0
        progress = 0

    # Check if route id is in session
    if 'routeID' in session:
        routeID = session['routeID']

    print('Progress: ', progress)

    print(' ')
    print(session['routeID'])
    print(session['progress'])
    print(' ')

    # Get the location ID for the clue
    locationData = getLocation(session['routeID'], session['progress'])
    print("LOCATION DATA: " + str(session['routeID']) + " " + str(session['progress']))
    print('LOCAION DATA IS: ', locationData)

    locationID = locationData[0]['LOCATION_ID']
    # Shows the next locations image
    imageURL = getLocation(session['routeID'], session['progress'])[0]['LOCATION_IMAGE_URL']
    imageLocation = url_for('static', filename='images/' + imageURL)
    print("LocationID", locationID)
    # check if there are no more locations
    if (len(getLocationClues(locationID)) == 0):
        return redirect(url_for('game_page.endScreen'))

    cluemessage = getLocationClues(locationID)[0]['CLUE']
    print(cluemessage)
    # progress value = get User.progress from db
    # clue message = get clue for position = progress from db

    print(imageLocation)
    return render_template('mobile/Clue_Page.html', progress_value=progress, clue_message=cluemessage,
                           clue_location=imageLocation)


@game_page.route('/getQuestion', methods=['POST'])
def getQuestion():
    progress = session['progress']
    print("progress: ", progress)
    # Get the location ID for the question
    locationData = getLocation(session['routeID'], session['progress'])

    locationID = locationData[0]['LOCATION_ID']

    print(" ")
    print("big check ", locationID)
    print(" ")

    questionData = getQuestionLocationID(locationID)
    print("questionData: ", questionData)

    imageURL = locationData[0]['LOCATION_IMAGE_URL']
    imageLocation = url_for('static', filename='images/' + imageURL)

    print(questionData[0]['QUESTION_CONTENT'])
    questionText = questionData[0]['QUESTION_CONTENT']

    a = questionData[0]['MULTIPLE_CHOICE_A']
    b = questionData[0]['MULTIPLE_CHOICE_B']
    c = questionData[0]['MULTIPLE_CHOICE_C']
    d = questionData[0]['MULTIPLE_CHOICE_D']
    return render_template('mobile/Answer_Page.html', progress_value=progress, clue_message="Question: " + questionText,
                           clue_location=imageLocation,
                           answer_a=a, answer_b=b, answer_c=c, answer_d=d)


@game_page.route('/getQuestionRedirect')
def retryQuestion():
    if ('QuestionMessage' in session):
        # dosplay the message
        error_message = session['QuestionMessage']
    else:
        # If no message set set the message to be empty (No message)
        session['QuestionMessage'] = ""
        error_message = ""

    progress = session['progress']
    locationData = getLocation(session['routeID'], session['progress'])
    locationID = locationData[0]['LOCATION_ID']
    questionData = getQuestionLocationID(locationID)
    imageURL = locationData[0]['LOCATION_IMAGE_URL']
    imageLocation = url_for('static', filename='images/' + imageURL)
    questionText = questionData[0]['QUESTION_CONTENT']
    a = questionData[0]['MULTIPLE_CHOICE_A']
    b = questionData[0]['MULTIPLE_CHOICE_B']
    c = questionData[0]['MULTIPLE_CHOICE_C']
    d = questionData[0]['MULTIPLE_CHOICE_D']
    return render_template('mobile/Answer_Page.html', error_message=error_message, progress_value=progress,
                           clue_message="Question: " + questionText, clue_location=imageLocation,
                           answer_a=a, answer_b=b, answer_c=c, answer_d=d)


@game_page.route('/confirmAnswer', methods=['POST'])
def checkQuestion():
    # chscks he progress of the student to ensure the correct question is loaded
    progress = session['progress']
    # Get their answer to the question
    answer = request.form.get('answer')
    if answer is None:
        session['QuestionMessage'] = 'Please submit an answer try again'
        return redirect(url_for('game_page.retryQuestion'))
    # Retreive the correct answer
    locationID = getLocation(session['routeID'], session['progress'])[0]['LOCATION_ID']
    questionData = getQuestionLocationID(locationID)
    answer = answer.upper()
    correctAnswer = questionData[0]['ANSWER'];

    if (str(answer[0]) == str(correctAnswer[0])):
        # If it was the las question load the end screen
        if (int(progress) == int(session['numOfQuestions'])):
            return redirect(url_for('game_page.endScreen'))
        else:
            # If not load the lext location clue
            session['progress'] = session.get('progress') + 1
            return redirect(url_for('game_page.showLocationClue'))
    else:
        session['teamScore'] = session['teamScore'] - 3
        session['QuestionMessage'] = 'Wrong answer try again'
        # redirect to the question page but with error message
        return redirect(url_for('game_page.retryQuestion'))


@game_page.route('/finished')
def endScreen():
    teamID = session['teamID']
    teamscore = session['teamScore']
    routeID = session['routeID']
    routeName = getRouteName(routeID)[0]['ROUTE_NAME']
    if 'resetTeamFlag' not in session:
        insertScore(routeID, routeName, teamID, teamscore)
    print(' ')
    print('error here ', teamID)
    print(' ')
    teamName = getTeamFromID(teamID)[0]['TEAM_NAME']
    teamreturn = getTeamsScores()
    # teams = []
    """for team in teamreturn:
        teams.append({'group_name': team['TEAM_NAME'], 'final_score': score['VALUE']})
    """
    session['resetTeamFlag'] = True

    return render_template('mobile/End_Game_Page.html', group_name=teamName, final_score=teamscore,
                           final_position="1st", teams=teamreturn)

