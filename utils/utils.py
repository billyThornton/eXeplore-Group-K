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
@Last Edited: 26/02/2020
@edited by: Billy Thornton

This file contains some extra function and utilities
"""
EMAILEXTENSION = "@exeter.ac.uk"

#Checks if a string has numbers
def hasNumbers(inputString):
     return any(char.isdigit() for char in inputString)
 
#Checkes email is of the right email extension (@exeter.ac.uk)
def checkEmail(email):
    global EMAILEXTENSION
    if(email[-len(EMAILEXTENSION):]==EMAILEXTENSION):
        return True