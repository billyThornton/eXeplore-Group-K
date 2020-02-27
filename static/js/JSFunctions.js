/**
 * Created on 19/02/2020 
 * @author: Ben Trotter
 * @Last Edited: 26/02/2020
 * @edited by: Billy Thornton
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

/**
 * @brief Dynamically loads HTML into the div that has an id called 'content'. This 
 * function is used with HTML5's onclick method.
 *
 * @param {file} - A string containing the url for the html that is to be loaded.
 */
function loadDoc(file)
{
  $(document).ready(function()
  {
    $('#content').load(file);
  });
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
 * @brief Alerts a message to the browser informing the user that a certain feature
 * hasn't been added yet. This function is used with HTML5's onclick method. 
 *
 */
function appConstruction() {
	alert("Application currently under construction.\nFeature not added yet.")
}

/**
 * @brief Function takes the user back to the last page that they were on. Used
 * when go back buttons are clicked.
 *
 */
function goBack() {
  window.history.back();
}