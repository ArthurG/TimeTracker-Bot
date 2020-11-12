#timetracker V2
import datetime # time parser
import uuid # to generate unique ids
import csv # default python library to navigate csv files
import calendar #to manage timezones
import json

import gspread # to edit google sheets files
from oauth2client.service_account import ServiceAccountCredentials # secured connection to the google drive API


with open('config.txt') as json_file:
    data = json.load(json_file)



    sheetName = data['sheetName'] # name of the document to process. Create it
                              # with your google account and share it with this
                              # gmail user : timetracker@discord-timetracker.iam.gserviceaccount.com
                              # don't forget to give the editing permissions.
                              # please note that the program will only process the first
                              # sheet of the document.
    filename = data['filename'] # name of the csv file to process. It will be created if it does not exists.
    delimiter = data['delimiter'] # not the default comma as a comma is more likely to be in an activity label.
                    # you may virtually choose any delimiter but a more common one will make displaying
                    # the file easier for most spreadsheet viewers.
    timezoneoffset = int(data['timezoneoffset']) # time offset (difference in second to greenwich time/GMT)



# google drive authentification
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)


sheet = client.open(sheetName).sheet1 # processing the first workbook

class Activity:
    "Represents an activity"

    def __init__(self, startDate, endDate, label):
        self.startDate = startDate
        self.endDate = endDate
        self.dateCreated = str(int(datetime.datetime.utcnow().timestamp()))
        self.label = label
        self.id = str(uuid.uuid4()) #uuid4 is an unpredictable unique number. Creating 1 billion uuid4 keys per second for the next 100 years will result on a 50% chance of having a duplicate. Storing all those keys would take 256 000 petabytes of storage.


def saveToCsv():
    "saves the spreadsheet to csv format"
    # creating csv file from the google spreadsheet
    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter = delimiter)
        writer.writerows(sheet.get_all_values())

    log("saved spreadsheet to csv")

def getLastEndTime():
    lastRow = len(sheet.get_all_values())
    lastEndTime = sheet.acell('C'+str(lastRow)).value
    return int(lastEndTime)

def addActivity(activity):
    "adds an activity object in the sheet."
    lastRow = len(sheet.get_all_values()) # line numbers starts at 1.
    sliceStr = "A"+str(lastRow+1)+":E"+str(lastRow+1)

    sheet.update(sliceStr,[[activity.label, activity.startDate,activity.endDate,activity.dateCreated, activity.id]])
    log("added Activity to the spreadsheet")
    saveToCsv()

def delActivity(id):
    "deletes an activity based on a given id."
    try :
        cell = sheet.find(id)
        sheet.delete_rows(cell.row)
        log(f"successfully deleted the row of id {id}")
        saveToCsv()
    except gspread.exceptions.CellNotFound:
        log("Could not delete : the given Id does not exists in the sheet.")


def log(content): # modified print() function that adds the hour to the print. More convenient for logging purposes.
    print(str(datetime.datetime.utcnow())[11:19] + " : " + content)



def analyzeUserEntry(entry):
    #try : #gigantic try as errors can happen everywhere if the input is random for example. The program won't block in all cases but the try will ensure that the fact that an error happened will be displayed.
    monthList = ["jan","feb","mar", "apr","may","jun","jul","aug","sep","oct","nov","dec"]
    messageList = entry.split(" ")



    timeIndicators = []
    dateIndicators = []
    label = ""

    for i in messageList : # parsing the message to retrieve hours and dates
        if "am" in i.lower() or "pm" in i.lower() :
            timeIndicators.append(i)
        else :
            for j in monthList :
                if j in i.lower() :
                    dateIndicators.append(i)

    formattedHours = [] # formatting the hours
    # /!\ Still have to implement special cases with noon and midnight
    for i in range(len(timeIndicators)) :
        if "am" in timeIndicators[i].lower() :
            withoutAm = timeIndicators[i].lower().split("am")[0]
            hour = []
            for i in withoutAm.split(":"):
                hour.append(int(i))
            if hour[0] == 12:
                hour[0] = 0
            formattedHours.append(hour)

        else :
            withoutPm = timeIndicators[i].lower().split("pm")[0]
            hour = []
            for i in withoutPm.split(":"):
                hour.append(int(i))
            if hour[0] != 12:
                hour[0] += 12
            formattedHours.append(hour)

    formattedDate = [] #formatting the date

    for i in range(len(dateIndicators)):
        month = dateIndicators[i][:3]
        monthNumber = monthList.index(month.lower())+1
        day = dateIndicators[i][3:]
        formattedDate.append([monthNumber,int(day)])


    # Starting the three methods :

    if len(formattedHours) == 2 and len(formattedDate) == 0 : # method 1
        yersteday = False # defines if the day is today or yersteday
        if formattedHours[0][0] > formattedHours [1][0] : # if the start hour is smaller than the end hour
            yersteday = True
        elif formattedHours [0][0] == formattedHours[1][0] : # if it is the same
            if formattedHours [0][1] > formattedHours[1][1]: # if the start minutes is smaller than the end minutes
                yersteday = True

        offset = 0
        if yersteday == True :
            offset = 86400

        datestart = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, datetime.datetime.utcnow().day, formattedHours[0][0], formattedHours[0][1])
        timestampstart = calendar.timegm(datestart.utctimetuple()) - timezoneoffset  - offset
        dateend = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, datetime.datetime.utcnow().day, formattedHours[1][0], formattedHours[1][1])
        timestampend = calendar.timegm(dateend.utctimetuple()) - timezoneoffset
        #done

        #getting the label :
        labelLst = messageList[:messageList.index(timeIndicators[0])]

        for i in labelLst :
            label+=i
            label+=" "
        label = label[:-1] # to delete the last space



    elif len(formattedHours) == 2 and len(formattedDate) == 2 : # method 2
        datestart = datetime.datetime(datetime.datetime.utcnow().year, formattedDate[0][0], formattedDate[0][1], formattedHours[0][0], formattedHours[0][1])
        timestampstart = calendar.timegm(datestart.utctimetuple()) - timezoneoffset

        dateend = datetime.datetime(datetime.datetime.utcnow().year, formattedDate[1][0], formattedDate[1][1], formattedHours[1][0], formattedHours[1][1])
        timestampend = calendar.timegm(dateend.utctimetuple()) - timezoneoffset

        #done

        #getting the label :
        labelLst = messageList[:messageList.index(dateIndicators[0])]

        for i in labelLst :
            label+=i
            label+=" "
        label = label[:-1] # to delete the last space

    elif len(formattedHours) == 1 and len(formattedDate) == 0 : # method 3

        timestampstart = getLastEndTime()

        dateend = datetime.datetime(datetime.datetime.utcnow().year, datetime.datetime.utcnow().month, datetime.datetime.utcnow().day, formattedHours[0][0], formattedHours[0][1])
        timestampend = calendar.timegm(dateend.utctimetuple()) - timezoneoffset

        #done

        #getting the label :
        labelLst = messageList[:messageList.index(timeIndicators[0])]

        for i in labelLst :
            label+=i
            label+=" "
        label = label[:-1] # to delete the last space


    else : # return an error message
        timestampstart = "error : unespected amount of arguments"
        timestampend = "error : unespected amount of arguments"






    return [timestampstart, timestampend, label]
    #except :
        #return ["an error happened", "an error happened", "an error happened"]




#print(analyzeUserEntry("Do the dishes 06:00AM 6:00PM"))

#activity1 = Activity("tomorrow", "in twelve years", "be very cool")
#printActivity(activity1)
#addActivity(activity1)
#delActivity("344e0abd-f1a4-44f2-9a42-d8556ee7a837")

#message = input("enter your message : ")
#analyzeUserEntry(message)
#saveToCsv()
