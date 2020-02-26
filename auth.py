# -*- coding: utf-8 -*-
"""
Created on 26/02/2020

@author: Billy Thornton
@Last Edited: 26/02/2020
@edited by: Billy Thornton
"""
from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import models

PEPPER = "B24B11T99" 
def verifyEmail(email):
    #dbquery for email
    global PEPPER
    #replace with get from db
    password_text = "password"+PEPPER
    listInfo = {"email":"test","password":generate_password_hash(password_text,"sha256")}
    if( len(listInfo)>0):
        return listInfo

def verifyPassword(passwordEntered, hashedPassword):
    if(passwordEntered!=""):
        global PEPPER
        checkingPassword = passwordEntered+(PEPPER)
        if(check_password_hash(hashedPassword,checkingPassword)):
            print(hashedPassword,checkingPassword)
            return True
        else:
            return False

def verifyUser(passwordEntered,emailEntered):
    userInfo = verifyEmail(emailEntered)
    if(len(userInfo)>0):
        if(verifyPassword(passwordEntered,userInfo['password'])):
            #get user info and return
            return True
        else:
            return False
    else:
        return False
    
def hashPassword(password):
    global PEPPER
    password_text = password+PEPPER
    hashedPass = generate_password_hash(password_text,"sha256")
    return hashedPass
    
def generate_confirmation_token(email,app):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])