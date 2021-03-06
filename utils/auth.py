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

Created on 26/02/2020

@author: Billy Thornton
@Last Edited: 26/02/2020
@edited by: Billy Thornton

This file contains all the necessary function to authorise a user for the app
"""
from werkzeug.security import generate_password_hash, check_password_hash


from databaseAdapter import getStudentID, getTutorPassword, getStudentPassword

# Appended to all passwords before hashing
PEPPER = "B24B11T99"


def verifyEmail(email):
    """
    Check if the given email belongs to either staff or student and retrives the password
    of the user who owns the email
    :param String email: the email entered
    :return: Verification token{bool VerificationToken: (success of verification),String role: (role of the user),
                                String hashedPassword: hashedpassword of the user, Int ID: studentID}

    """
    global PEPPER
    # Gets a result set for all students with the gievn email
    studentID = getStudentID(email)
    # Gets a result set for all the tutors of a given email
    tutorID = getTutorPassword(email)

    # Check if the email belongs to a student of staff
    if (studentID is not None and len(studentID) > 0):
        hashedPassword = getStudentPassword(email)
        # If student return the hased password and set role to staff
        return {'VerificationToken': False, 'Role': 'student', 'hashedpass': hashedPassword[0]['PASSWORD'],
                'ID': studentID}

    elif (tutorID is not None and len(tutorID) > 0):
        hashedPassword = getTutorPassword(email)
        # if tutor return hashed password and set role to tutor
        return {'VerificationToken': False, 'Role': 'tutor', 'hashedpass': hashedPassword[0]['PASSWORD'],
                'ID': tutorID}

    # Neither staff nor student
    else:
        return {'VerificationToken': False, 'Role': '', 'hashedpass': ""}


def verifyPassword(passwordEntered, hashedPassword):
    """
    Check the password entered is the same as the password stored
    :param passwordEntered: String password that was enetered into the form
    :param hashedPassword: String password stored in the database
    :return: True if the same False otherwise
    """
    if (passwordEntered != ""):
        global PEPPER
        # Adds the pepper to the plaintext password
        checkingPassword = passwordEntered + (PEPPER)
        # checks the stored hased password agains the new hashed password
        if (check_password_hash(hashedPassword, checkingPassword)):
            return True
        else:
            return False


def verifyUser(passwordEntered, emailEntered):
    """
    Verify the email and password are correct
    :param String passwordEntered : the password entered into the login screen
    :param String emailEntered : the email entered into the login screen
    """
    token = verifyEmail(emailEntered)

    if (len(token['hashedpass']) > 0):
        if (verifyPassword(passwordEntered, token['hashedpass'])):
            # sets the tokens verification to true e.g. passwords are the same
            token['VerificationToken'] = True

    return token


def hashPassword(password):
    """
    Hashes the given password after appending pepper and salt using sha256
    :param String password : the password entered
    :return: Hashed password
    """
    global PEPPER
    password_text = password + PEPPER
    hashedPass = generate_password_hash(password_text, "sha256")
    return hashedPass
