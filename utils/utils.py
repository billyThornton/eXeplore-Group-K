"""
Copyright  2020, by Group K
Contributors: Jamie Butler, Rahul Pankhania, Teo Reed, Billy Thornton, Ben Trotter, Kristian Woolhouse
URL: https://github.com/billyThornton/eXeplore-Group-K 
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
 
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials
provided with the distribution. 

Created on 26/02/2020

@author: Billy Thornton
@Last Edited: 12/03/2020
@edited by: Billy Thornton
updated doc comments

This file contains some extra function and utilities
"""
EMAILEXTENSION = "@exeter.ac.uk"


def hasNumbers(inputString):
     """
     :param inputString : the input to check for numbers
     :return: True if the email contains a number
     """
     return any(char.isdigit() for char in inputString)
 

def checkEmail(email):
    """
    :var EMAILEXTENSION the chosen email extension
    :param email : the email to check for an extension
    :return: True if the email has the right extension
    """
    global EMAILEXTENSION
    if(email[-len(EMAILEXTENSION):]==EMAILEXTENSION):
        return True