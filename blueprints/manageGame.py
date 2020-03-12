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

This file controls all the logic for the actual game pregression

"""
from flask import render_template, redirect, url_for, request, send_file, session, jsonify, Blueprint, flash

from databaseAdapter import *

game_page = Blueprint('game_page',__name__,template_folder='templates')



######################
# Student Game Pages  #
######################

@game_page.route('/Join')
def loadJoinTeamPage():
    """
    Load the jointeams screen displaying all tutors and all teams
    :return: Renders the template for the join team html
    """
    gameTeams = getTeams()
    gameTutors = getTutors()
    return render_template('mobile/Join_Team.html', teams=gameTeams, tutors=gameTutors)


@game_page.route('/assignTeam', methods=['POST'])
def assignTeam():
    """
    Assigns the user to a team and sets the teamid and teamleader session
    :return: session that has team leader and teamid
    """

    studentID = session['studentID']

    teamID = request.form.get('team')
    session['teamID'] = teamID

    updateStudentTeam(studentID, teamID)
    teamLeader = getTeamLeader(teamID)

    session['teamScore'] = 100


    #If there is no team leader set this user to be team leader
    if teamLeader[0]['TEAM_LEADER'] is None:
        updateTeamLeader(studentID, teamID)
        #Set the session teamleader to be true to indicate this user is the team leader
        session['teamLeader'] = True
        return redirect(url_for('game_page.loadFirstChoosePage'))
    else:
        # TODO wait here until route selected by team leader
        routeID = getRouteID(session['teamID'])
        #Wait until the team leader has chosen a route
        while routeID[0]['CURRENT_ROUTE_ID'] is None:
            routeID = getRouteID(session['teamID'])

        session['routeID'] = routeID[0]['CURRENT_ROUTE_ID']
        session['teamLeader'] = False

        numOfQuestions = getNumLocationOnRoute(session['routeID'])
        session['numOfQuestions'] = numOfQuestions[0]['1']

        return redirect(url_for('game_page.showLocationClue'))


@game_page.route('/firstChoose')
def loadFirstChoosePage():
    """
    If the user is the first member of the team redirect to make them choose route
    :return: first choose template
    """
    gameRoutes = getRoutes();
    return render_template('mobile/First_Choose.html', routes=gameRoutes)


@game_page.route('/routeSelect', methods=['POST'])
def routeSelect():
    """
    Sets the current route for the team to be the selected route
    :return: The show location page with the session routeID set and numofquestions set
    """
    routeID = request.form['route']
    teamName = request.form['teamName']
    teamID = session['teamID']

    session['routeID'] = routeID
    #Sets the team route
    updateTeamRoute(routeID, 0, teamID)
    #sets the team name
    updateTeamName(teamName, teamID)
    #The max num of questions to catch when the game finishes
    numOfQuestions = getNumLocationOnRoute(session['routeID'])
    session['numOfQuestions'] = numOfQuestions[0]['1']

    return redirect(url_for('game_page.showLocationClue'))

# Displays the location clue page at an appropriate progression point
@game_page.route('/Game')
def showLocationClue():
    """
    Shows the clue for the next location with the image
    :return: returns the new clue page
    """
    # Check if route id is in session
    if 'routeID' in session:
        routeID = session['routeID']

    progress = getTeamFromStudentID(session['studentID'])[0]['PROGRESS']
    session['progress'] = progress

    #Game has finished
    if session['progress'] > session['numOfQuestions']:
        return redirect(url_for('game_page.endScreen'))

    # Get the location ID for the clue
    locationData = getLocation(session['routeID'], progress)
    locationID = locationData[0]['LOCATION_ID']

    # Shows the next locations image
    imageURL = getLocation(session['routeID'], progress)[0]['LOCATION_IMAGE_URL']
    imageLocation = url_for('static', filename='images/' + imageURL)

    cluemessage = getLocationClues(locationID)[0]['CLUE']

    return render_template('mobile/Clue_Page.html', progress_value=progress, clue_message=cluemessage,
                           clue_location=imageLocation, total=session['numOfQuestions'])


@game_page.route('/getQuestion', methods=['POST'])
def getQuestion():
    """
    Gets the next multiple choice question
    :return: returns the question screen
    """
    #You must be the team leader to answer questions
    if session['teamLeader']:

        progress = getTeamFromStudentID(session['studentID'])[0]['PROGRESS']
        # Get the location ID for the question
        locationData = getLocation(session['routeID'], progress)

        locationID = locationData[0]['LOCATION_ID']

        questionData = getQuestionLocationID(locationID)


        imageURL = locationData[0]['LOCATION_IMAGE_URL']
        imageLocation = url_for('static', filename='images/' + imageURL)


        questionText = questionData[0]['QUESTION_CONTENT']

        a = questionData[0]['MULTIPLE_CHOICE_A']
        b = questionData[0]['MULTIPLE_CHOICE_B']
        c = questionData[0]['MULTIPLE_CHOICE_C']
        d = questionData[0]['MULTIPLE_CHOICE_D']

        return render_template('mobile/Answer_Page.html', progress_value=progress, clue_message="Question: " + questionText,
                               clue_location=imageLocation,
                               answer_a=a, answer_b=b, answer_c=c, answer_d=d, total=session['numOfQuestions'])
    else:
        #Not team leader waits until the team leader to answer the question
        progress = getStudentProgress(session['studentID'])[0]['PROGRESS']
        if progress == int(session['numOfQuestions'])+1:
            return redirect(url_for('game_page.endScreen'))
        if progress == session['progress']:
            flash("Talk to the team leader to answer the question together")
        return redirect(url_for('game_page.showLocationClue'))


@game_page.route('/getQuestionRedirect')
def retryQuestion():
    """
    If you get the question wrong it reasks the question
    :return: retueern the question page
    """
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

    return render_template('mobile/Answer_Page.html', progress_value=progress,
                           clue_message="Question: " + questionText, clue_location=imageLocation,
                           answer_a=a, answer_b=b, answer_c=c, answer_d=d)


@game_page.route('/confirmAnswer', methods=['POST'])
def checkQuestion():
    """
    Checks the users answer is correct
    :return: returns a new clue if the answer is correct and reasks the question if wrong
    """
    # checks the progress of the student to ensure the correct question is loaded
    progress = session['progress']
    # Get their answer to the question
    answer = request.form.get('answer')
    if answer is None:
        flash('Please submit an answer try again')
        return redirect(url_for('game_page.retryQuestion'))
    # Retreive the correct answer
    locationID = getLocation(session['routeID'], session['progress'])[0]['LOCATION_ID']

    questionData = getQuestionLocationID(locationID)
    answer = answer.upper()
    correctAnswer = questionData[0]['ANSWER'];

    if str(answer[0]) == str(correctAnswer[0]):
        session['progress'] = session.get('progress') + 1
        updateTeamRoute(session['routeID'],session['progress'],session['teamID'])

        if int(progress) == int(session['numOfQuestions'])+1:
            return redirect(url_for('game_page.endScreen'))
        else:
            return redirect(url_for('game_page.showLocationClue'))
    else:
        session['teamScore'] = session['teamScore'] - 3
        flash('Wrong answer try again')
        # redirect to the question page but with error message
        return redirect(url_for('game_page.retryQuestion'))


@game_page.route('/finished')
def endScreen():
    """
    Shows the endgame leaderboard and marks the session for reset
    :return: the leaderboard
    """
    teamID = session['teamID']
    teamscore = session['teamScore']
    routeID = session['routeID']
    routeName = getRouteName(routeID)[0]['ROUTE_NAME']
    #Adds the score to the database unless its been done already
    if 'resetTeamFlag' not in session:
        insertScore(routeID, routeName, teamID, teamscore)

    teamName = getTeamFromID(teamID)[0]['TEAM_NAME']
    teamreturn = getTeamsScores()
    # marks the session for reset on logout
    session['resetTeamFlag'] = True

    return render_template('mobile/End_Game_Page.html', group_name=teamName, final_score=teamscore,
                           final_position="1st", teams=teamreturn)

