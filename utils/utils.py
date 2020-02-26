EMAILEXTENSION = "@exeter.ac.uk"
def hasNumbers(inputString):
     return any(char.isdigit() for char in inputString)
 
def checkEmail(email):
    global EMAILEXTENSION
    if(email[-len(EMAILEXTENSION):]==EMAILEXTENSION):
        return True