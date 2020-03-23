#!/usr/bin/env python3

__author__ = "Jake Miller (@LaconicWolf)"
__date__ = "20200320"
__version__ = "0.01"
__description__ = '''A script to help build a node web app project.'''


import sys

if not sys.version.startswith('3'):
    print('\n[-] This script will only work with Python3. Sorry!\n')
    exit()

import subprocess
import shutil
import os


def check_for_tools(name):
    """Checks to see whether the tool name is in current directory or in the PATH"""
    if is_in_dir(name) or is_in_path(name):
        return True
    else:
        return False


def is_in_path(name):
    """Check whether name is on PATH and marked as executable.
    https://stackoverflow.com/questions/11210104/check-if-a-program-exists-from-a-python-script/34177358
    """
    return shutil.which(name) is not None


def is_in_dir(name, directory='.'):
    """Checks whether a file exists in a specified directory."""
    files = (os.listdir(directory))
    for file in files:
        if file.lower() == name.lower():
            if os.path.isfile(file):
                return True


def tools_check():
    """Checks for npm and node"""
    required_tools = ("node", "npm")
    missing_tools = []
    for tool in required_tools:
        if not check_for_tools(tool):
            missing_tools.append(tool)
    if missing_tools:
        for tool in missing_tools:
            print(f"[-] {tool} could not be found in the current directory or in your PATH. Please ensure either of these conditions are met.")
            exit()


def create_empty_file(filepath):
    with open(filepath, 'w') as fh:
        pass


def create_project_structure():
    """Creates the files and folders necessary to start a 
    project.
    """
    os.mkdir(project_name)
    create_empty_file(os.sep.join([project_name, 'app.js']))
    os.mkdir(os.sep.join([project_name, "public"]))
    os.mkdir(os.sep.join([project_name, "public", "css"]))
    create_empty_file(os.sep.join([project_name, "public", "css", "styles.css"]))
    os.mkdir(os.sep.join([project_name, "views"]))
    create_empty_file(os.sep.join([project_name, "views", "index.ejs"]))


def install_node_modules():
    """Uses subprocess to do npm init and install node modules"""
    #return
    os.chdir(project_name)

    # npm init is interactive, so I'm using 10 newline commands
    # to enter default values
    newline = os.linesep
    commands = newline * 10
    FNULL = open(os.devnull, 'w')

    p = subprocess.Popen(['npm', 'init'],
                          stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                          stdout=FNULL, universal_newlines=True, shell=True)
    p.communicate(commands)

    # Does not check for install errors...
    install_output = subprocess.getoutput("npm install express body-parser ejs")


def write_app_js():
    '''Writes a default app.js file'''
    with open('app.js', 'a') as fh:
        fh.write('''\
const express = require("express");
const bodyParser = require("body-parser");
const app = express();

let items = ['Example item 1', 'Example item 2', 'Example item 3'];

app.set("view engine", "ejs");
app.use(bodyParser.urlencoded({extended: true}));
app.use(express.static("public"));

app.get("/", function(req, res) {
    
    let today = new Date();
    
    let options = {
        weekday: "long",
        day: "numeric",
        month: "long"
    };

    let day = today.toLocaleDateString("en-US", options);

    res.render("index", {kindOfDay: day, newListItems: items});
    //res.render("name of template file minus the .ejs", {template marker <%= %> name: Var name in this file});
})

app.post("/", function(req, res) {
    //let item = req.body.<name of html name attribute>;
    let item = req.body.newItem;
    items.push(item);
    res.redirect("/");
})

const portNum = 3000;
app.listen(portNum, function(){
    console.log("Server started on port " + portNum)
})\
''')


def write_index_ejs():
    with open('index.ejs', 'a') as fh:
        fh.write('''\
<!DOCTYPE html>
<html lang="en" dir="ltr">
    <head>
        <meta charset="utf-8">
        <title>To Do List</title>
        <link rel="stylesheet" href="css/styles.css">
    </head>
    <body>
    
    <h1><%= kindOfDay %></h1>

    <ul>
    <%  for (var i=0; i<newListItems.length; i++) {  %>
        <li><%= newListItems[i] %></li>
<%  }  %>
    </ul>

    <form class="" action="/" method="post">
        <input type="text" name="newItem">
        <button type="submit" name="button">Add</button>
    </form>

    <!--<% if (kindOfDay === "Saturday" || kindOfDay === "Sunday") { %>
        <h1 style="color:purple">It's a <%= kindOfDay %>!</h1>
    <%} else { %>
        <h1 style="color:green">It's a <%= kindOfDay %>!</h1>
    <% } %>-->
        
    
    </body>
</html>            \
''')


def main():
    # Check for required tools
    print("[*] Checking for tools")
    tools_check()

    print("[*] Creating project structure")
    create_project_structure()

    print("[*] Installing node modules")
    install_node_modules()

    print("[*] Writing default file content")
    write_app_js()
    os.chdir('views')
    write_index_ejs()

    print(f"[+] Project {project_name} created successfully. Change directories to {project_name}, and use the command 'node app.js' to start the server.")

    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project name>")
        exit()
    project_name = sys.argv[1]
    main()