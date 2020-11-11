HOW TO GET THE BOT TO WORK : 


1) Get yourself a bot token :

This tutorial will explain way better than me how to get yourself a bot token. A bot token is the unique identifier for your bot.
https://www.writebots.com/discord-bot-token/

This file also explains how to invite your bot to your server

Put this token inside of the "token" parameter in the config.txt file.

2) Get yourself a Google Spreadsheet API Key.

The Google Spreadsheet API Key takes the form of a "client_secret.json" file. Here is how to get this file : 

-Go to the Google developers console : https://console.developers.google.com/
-Create a new project
-Give the project a name
-Go to the project dashboard and click on "+ ENABLE APIS AND SERVICES"
-Search Google Spreadsheet API (warning : don't search for google drive API) and click it
-Enable the Google Spreadsheet API 
-Click on Create Credentials.
-Select the "application data" and "No, i'm not using them" parameters and click on What credentials do I need?.
-Enter a Service Account Name and select the "project->editor" Role.
-A JSON file will be downloaded. We will need this JSON file in our script. So rename that file as client_secret.json.

you can find a complete version of this tutorial (with images) on this page : 
https://medium.com/craftsmenltd/from-csv-to-google-sheet-using-python-ef097cb014f9

3) Share your document with the bot

Now that you have this file in your project folder, you will need to give access to the bot to your google spreadsheet. Create a google spreadsheet document and and write in the first four columns of the first line : 
Activity Name | StartTime | EndTime | Time Added | ID

The names can change but it's important to have those columns (from A to E) filled on the first line.

Share the document with the mail address you can find in the "client_email" property of the client_secret.json file, line 6. Don't forget to give him the edit permission.

In the config.txt file, in the property "sheetName", enter the name of the sheet you want the bot to modifiy.

4) Fix the google drive error and launch the bot

At this point, if you launch the bot.py script, an error may occur, telling you that you need to activate the Google Drive API. If so, follow the link the console will give you and make sure that the google drive API is enabled. Wait a few minutes and try again.

5) Enjoy !

Let me know if you experience any issue with this program, or if you want me to add/modify anything. Type the !help (! is the default prefix but can be changed with the config file) command to get started !


