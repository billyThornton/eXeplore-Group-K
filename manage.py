# -*- coding: utf-8 -*-
"""
Created on 19/02/2020 
@author: Billy Thornton
@Last Edited: 26/02/2020
@edited by: Billy Thornton

This file contains all the URL routing for the backend/front end, it takes urls
and displays the required html files.
It also processes data passed using post/get request.
"""
import flask
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint,send_file,session
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import os
import json
import models
import auth

#utils file
exec(open("utils/utils.py").read())
app = Flask(__name__)
port = int(os.getenv('PORT', 8000))


#Handles the [post] method for login
#Will be passed a username and a password
@app.route('/',methods = ['POST'])
def login_post():
    currentUser=None
    user = models.User("1","Billy","test","test","Staff")
    user2 = models.User("1","Billy","test","password","Student")
    email = request.form.get('email')
    password = request.form.get('password')
    print("Email:",email,"Password:",password)
    print(user.email,user.password)
    if(auth.verifyUser(password,email)):
        if(password == "password"):
            currentUser = user2
        else:
            currentUser = user
    else:
        currentUser = user
    if(currentUser.role == "Staff"):
        return redirect(url_for('dashboard'))
    elif(currentUser.role == "Student"):
        return redirect(url_for('showLocationClue'))
    else:
        return redirect(url_for('login'))
    #database.getuserdata(email)
    #if password+salt+pepper.hased == databasereturn.password
    #user = User(db.id,db.name,db.password,db.email)
    
#This is the first page of the app currently the login page but we could add a splash screen if wanted
@app.route('/')
def login():
    session.clear()
    return render_template('Desktop/Game_Keeper_Login.html')

@app.route('/register')
def register():
    if('Error Message' in session):
        errorMessage = session['Error Message']
    else:
        session['Error Message'] = ""
        errorMessage = ""
    return render_template('Desktop/register.html',error_message = errorMessage)

@app.route('/registerSubmit',methods = ['POST'])
def registerSubmit():
    global EMAILEXTENSION
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    passwordConfirm = request.form.get('passwordConfirmation')
    if(password != passwordConfirm):
        session['Error Message'] = "Passwords are not the same"
        return redirect(url_for('register'))
    if checkEmail(email):
        if(hasNumbers(email)):
            Role="Student"
            print(Role)
        else:
            Role = "Staff"
            print(Role)
        return redirect(url_for('login'))
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
def dashboard():
    return render_template('Desktop/Game_Keeper_Page.html')

@app.route('/Add_Location')
def addLocation():
    return render_template('Desktop/Add_Location_Page.html')

@app.route('/Edit_Location')
def editLocation():
    return render_template('Desktop/Edit_Location_Page.html')


#Loads the gamekeepers dashboard tool
@app.route('/Manage_Locations_Page')
def manageLocations():
    return render_template('Desktop/Manage_Locations_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Manage_Groups_Page')
def manageGroups():
    return render_template('Desktop/Manage_Groups_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Leaderboard_Page')
def leaderboard():
    return render_template('Desktop/Leaderboard_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Manage_Routes_Page')
def manageRoutes():
    return render_template('Desktop/Manage_Routes_Page.html')

#Loads the gamekeepers dashboard tool
@app.route('/Assign_Routes_Page')
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
        session['progress'] = 1
        progress = 1
    cluemessage = "Clue to location "+str(progress)
    #progress value = get User.progress from db
    #clue message = get clue for position = progress from db
    imageLocation = url_for('static',filename='images/Exeterforum.jpg')
    print(imageLocation)
    return render_template('mobile/Clue_Page.html',progress_value = progress,clue_message = cluemessage,clue_location=imageLocation)

@app.route('/getQuestion',methods = ['POST'])
def getQuestion():
    progress = request.form.get('progress')
    imageLocation = url_for('static',filename='images/Exeterforum.jpg')
    print(progress)
    return render_template('mobile/Answer_Page.html',progress_value = progress,clue_message = "Question: "+str(progress),clue_location=imageLocation)

@app.route('/getQuestionRedirect')
def retryQuestion():
    progress = request.form.get('progress')
    imageLocation = url_for('static',filename='images/Exeterforum.jpg')
    return render_template('mobile/AnswerPage.html',progress_value = progress,clue_message = "Question: "+str(progress),clue_location=imageLocation)

@app.route('/confirmAnswer',methods = ['POST'])
def checkQuestion():
    maxProgress = 6
    progress = request.form.get('progress')
    answer = request.form.get('answer')
       
    if(answer == "a"):
        print(int(progress), answer, int(maxProgress))
        if (int(progress) == int(maxProgress)):
            return redirect(url_for('endScreen'))
        else:
            session['progress'] = session.get('progress')+1
            return redirect(url_for('showLocationClue'))
    else:
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
