# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 11:42:10 2020

@author: Billy Thornton
"""
class User():
    def __init__(self,dbID,name,email,password,role):
        self.dbID = dbID
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        
    