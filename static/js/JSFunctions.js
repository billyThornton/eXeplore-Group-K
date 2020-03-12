/**
 * Created on 19/02/2020
 * @author: Ben Trotter
 * @Last Edited: 11/03/2020
 * @edited by: Ben Trotter
 *
 * Copyright (c) “2020, by Group K
 * Contributors: Jamie Butler, Rahul Pankhania, Teo Reed, Billy Thornton, Ben Trotter,
 * Kristian Woolhouse
 * URL: https://github.com/billyThornton/eXeplore-Group-K ”
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of
 * conditions and the following disclaimer. Redistributions in binary form must reproduce
 * the above copyright notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 * SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
 * OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 * TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * This file contains javascript functions to alter the eXeplore App. Contains functions
 * to navigate through the application and dynamically load content to certain areas in
 * the application.
 */

// Global for reloading screens after form submission
 var currentScreen = "default";

/**
 * @brief Dynamically loads HTML into the div that has an id called 'content'. This
 * function is used with HTML5's onclick method.
 *
 * @param {file} - A string containing the url for the html that is to be loaded.
 */
function loadDoc(file)
{
  localStorage.currentScreen = file;
  currentScreen = file;

  $(document).ready(function()
  {
    $('#content').load(file);
  });
}

/**
 * @brief Reverts the page back to the dashboard page and sets the global variable
 * to default.
 *
 */
function clearRedirect()
{
  localStorage.currentScreen = "default";
  location.href="/dashboard";
}

/**
 * @brief Opens the side bar and changes the style for it once the icon is clicked.
 *
 */
function openNav() {
  document.getElementById("mySidebar").style.width = "250px";
  document.getElementById("main").style.marginLeft = "250px";
}

/**
 * @brief Closes the side bar and changes the style for it once the icon is clicked.
 * The style width and marginLeft is reverted back to 0.
 *
 */
function closeNav() {
  document.getElementById("mySidebar").style.width = "0";
  document.getElementById("main").style.marginLeft= "0";
}

/**
 * @brief Function takes the user back to the last page that they were on. Used
 * when go back buttons are clicked.
 *
 */
function goBack() {
  window.history.back();
}

/**
* Ensures that the name field is valid. If it isn't suitable
* an error class is added to the form input so the client knows which field has
* raised a mistake and an error message is produced saying what the error is.
*
* @return {boolean} true if a the entered field is valid otherwise false.
*/
function validateName()
{
  var name = document.forms["newAccountForm"]["name"].value;
  nameField = document.getElementById("name_input");
  // Removing the initial message
  initialMessage = document.getElementById("initial_message");
  initialMessage.innerHTML = "";

  if(!/^[a-zA-Z ]+$/.test(name))
  {
    text = "Name should only contain letters";
    nameField.classList.add("input-error");
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else
  {
    nameField.classList.remove("input-error");
    document.getElementById("invalid").innerHTML = "Please enter your details below:";
    document.getElementById("invalid").style.color="white";
    return true;
  }
}

/**
* Ensures that the email field is valid. If it isn't suitable
* an error class is added to the form input so the client knows which field has
* raised a mistake and an error message is produced saying what the error is.
*
* @return {boolean} true if a the entered field is valid otherwise false.
*/
function validateEmail()
{
  var email = document.forms["newAccountForm"]["email"].value;
  emailField = document.getElementById("email_input");
  // Removing the initial message
  initialMessage = document.getElementById("initial_message");
  initialMessage.innerHTML = "";

  if(!email.includes("@exeter.ac.uk"))
  {
    text = "Please enter an Exeter University email";
    emailField.classList.add("input-error");
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else
  {
    emailField.classList.remove("input-error");
    document.getElementById("invalid").innerHTML = "Please enter your details below:";
    document.getElementById("invalid").style.color="white";
    return true;
  }
}

/**
* Ensures that the password field is valid. If it isn't suitable
* an error class is added to the form input so the client knows which field has
* raised a mistake and an error message is produced saying what the error is.
*
* @return {boolean} true if a the entered field is valid otherwise false.
*/
function validatePassword()
{
  // Variables that the client enters into the field in the form.
  var pass = document.forms["newAccountForm"]["password"].value;
  passField = document.getElementById("pass_input");
  // Removing the initial message
  initialMessage = document.getElementById("initial_message");
  initialMessage.innerHTML = "";

  if (pass.length < 8)
  {
    text = "Password should be 8 characters or more";
    passField.classList.add("input-error");
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else if (noMixedCase(pass))
  {
    text = "Password should contain an upper and lower case character";
    passField.classList.add("input-error");
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else if (noNumber(pass))
  {
    text = "Password should contain a number";
    passField.classList.add("input-error");
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else
  {
    passField.classList.remove("input-error");
    document.getElementById("invalid").innerHTML = "Please enter your details below:";
    document.getElementById("invalid").style.color="white";
    return true;
  }
}

/**
* Ensures that the password confirmation field is valid. If it isn't suitable
* an error class is added to the form input so the client knows which field has
* raised a mistake and an error message is produced saying what the error is.
*
* @return {boolean} true if a the entered field is valid otherwise false.
*/
function validateConfirmation()
{
  var pass = document.forms["newAccountForm"]["password"].value;
  var confirm = document.forms["newAccountForm"]["passwordConfirmation"].value;
  confirmField = document.getElementById("confirm_input");
  // Removing the initial message
  initialMessage = document.getElementById("initial_message");
  initialMessage.innerHTML = "";

  if (confirm != pass)
  {
    text = "Passwords do not match, please try again";
    confirmField.classList.add("input-error");
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else
  {
    confirmField.classList.remove("input-error");
    document.getElementById("invalid").innerHTML = "Please enter your details below:";
    document.getElementById("invalid").style.color="white";
    return true;
  }
}

/**
 * Ensures that the entire form is valid before it is submitted to the backend.
 * The submission of the form is prevented if false is returned.
 *
 * @return {boolean} true if a the all entered fields are valid otherwise false.
 */
function validateCreate()
{
  initialMessage = document.getElementById("initial_message");
  initialMessage.innerHTML = "";

  if(validateName() == false)
  {
    text = "Please enter a valid name";
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else if (validateEmail() == false)
  {
    text = "Please enter an Exeter University email";
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else if(validatePassword() == false)
  {
    text = "Please enter a stronger password";
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else if (validateConfirmation() == false)
  {
    text = "Passwords do not match, please try again";
    document.getElementById("invalid").innerHTML = text;
    document.getElementById("invalid").style.color="red";
    return false;
  }
  else
  {
    return true;
  }
}

/**
 * Checks to see if there isn't an uppercase or lowercase letter in a string.
 *
 * @param {string} Str String to be checked.
 *
 * @return {boolean} true if there is no upper or lower case letter in the string.
 */
function noMixedCase(str)
{
  return !(/[a-z]/.test(str)) || !(/[A-Z]/.test(str));
}

/**
 * Checks to see if there isn't a number in a string.
 *
 * @param {string} Str String to be checked.
 *
 * @return {boolean} true if there is no number in the string.
 */
function noNumber(str)
{
  return !(/[0-9]/.test(str));
}

/**
 * Filters list of locations live for search bar
 * 
 * @param {int} inputID the search box tag id.
 * @param {int} ulID the id of the unsorted list.
 */
function searchList(inputID, ulID) {
    var input, filter, ul, li, i, txtValue;
    input = document.getElementById(inputID);
    filter = input.value.toUpperCase();
    ul = document.getElementById(ulID);
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        txtValue = li[i].textContent || li[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function getDropDown(locationName, dropDownID) {
    console.log("ENTERED THE GET DROP DOWN");
    if (locationName == "n/a") {
        return false;
    }
    $(document).ready(function() {
        $.ajax({
            url : '/Display_Questions',
            data : {
                locationName : locationName
            },
            type : 'POST'
        })
        .done(function(data) {
            console.log(data);
            var questions = data;
            for (var i = 0; i < questions.length; i++) {
                // The question content
                var question = questions[i];
                // Creating an option tag
                var opt = document.createElement('option');

                // Add text and value attribute
                opt.textContent = question;
                opt.value = question;
                questionDropDown = document.getElementById(dropDownID);
                console.log(questionDropDown);
                questionDropDown.appendChild(opt);
            }
        });
    });
}


function googleTranslateElementInit() {
  new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
}


$(document).ready(function(){
    $('input[type="file"]').change(function(e){
        var fileName = e.target.files[0].name;
        $('p[id="filename"]').text('The file ' + fileName +  ' has been selected.');
    });
});

