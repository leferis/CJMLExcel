from datetime import datetime
import os
from dateutil import parser
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import cjml
import numpy as np
from tkinter import messagebox
from tkinter.messagebox import askyesno
from dragAndDrop import Drag_and_Drop_Listbox
#from icons import IconSelect
from meniu import Meniu


journeySheets = []
userMapping = {}
PhaseList = []
actorsList = []
endUser = []
loop = True
goFoward = True
skipGruping = False
tempActors = []
action = ""
hasActivatedGrouping = False
fileName = ""
Icons = []


def checkifCreatorProvided(dataframe: pd.DataFrame):
    return dataframe.head(1).iloc[0, 0] in ["Yes", "No", np.nan]


def dropCreatorProvided(dataframe: pd.DataFrame):
    return dataframe.drop(axis=0, index=[6])


def showSheetWindow(excelFile, sheet):
    global actorsList
    if goFoward:
        dataFrame = pd.read_excel(excelFile, sheet_name=sheet)
        touchPoints = dataFrame.drop(axis=0, index=[0, 1, 2, 3, 4, 5])
        if checkifCreatorProvided(touchPoints) is True:
            touchPoints = dropCreatorProvided(touchPoints)
            touchPoints.rename(columns=stripSeries(dataFrame.iloc[5]), inplace=True)
        else:
            touchPoints.rename(columns=stripSeries(dataFrame.iloc[6]), inplace=True)
        actorsList = getActorsList(touchPoints)


def showActorGroupingWindow(sheet):
    global journeySheets, actorsList, loop
    while loop and goFoward:
        organizeUsers(sheet)
        if loop is False:
            for actor in actorsList:
                userMapping[actor] = actor
        if len(actorsList) == 0:
            loop = False


def checkIncludeFlag(text):
    if pd.isna(text):
        return True
    elif (
        str.upper(text) == "NO"
        or str.upper(text) == "NEI"
        or str.upper(text) == "N"
        or str.upper(text) == "FALSE"
        or CheckIfNumber(text)
    ):
        return False
    else:
        return True


def CheckIfNumber(text):
    if text is None:
        return False
    try:
        result = float(text) == 0
        return result
    except ValueError:
        return False


def checkDevationFlag(text):
    if pd.isna(text) or text is float:
        return False
    elif (
        str.upper(text) == "NO"
        or str.upper(text) == "NEI"
        or str.upper(text) == "N"
        or str.upper(text) == "FALSE"
        or (CheckIfNumber(text))
    ):
        return False
    else:
        return True


def error(sheet):
    messagebox.showerror(
        "Excel fillment error",
        'Enduser provided in "'
        + sheet
        + '" sheet, field A3, label "End-user ID", does not exist in receiver (column I) or initiator (column J) fields',
    )


def stripSeries(dataFrame):
    return dataFrame.apply(lambda x: x.strip() if isinstance(x, str) else x)


def change(value):
    global action
    action = value


def readExcel(filePath):
    global journeySheets, endUser, loop, skipGruping, actorsList, userMapping, action, fileName, Icons
    id = 1
    excelFile = pd.ExcelFile(filePath)
    fileName = os.path.splitext(os.path.basename(filePath))[0]
    selectSheets(excelFile.sheet_names)
    if goFoward:
        XMlList = cjml.CJML()
        for sheet in journeySheets:
            dataFrame = pd.read_excel(excelFile, sheet_name=sheet)
            showSheetWindow(excelFile, sheet)
            Meniu(change)
            if action == "group":
                showActorGroupingWindow(sheet)
            else:
                for actor in actorsList:
                    userMapping[actor] = actor
            endUser.append(str.capitalize(str.lower(dataFrame["Unnamed: 3"][0])))
            if not str.capitalize(str.lower(dataFrame["Unnamed: 3"][0])) in actorsList:
                error(sheet)
                return
            touchPoints = dataFrame.drop(axis=0, index=[0, 1, 2, 3, 4, 5]).dropna(
                how="all"
            )
            # if action == "icons" or action == "sort":
            #     IconSelect(userMapping)
            if checkifCreatorProvided(touchPoints) is False:
                touchPoints = dropCreatorProvided(touchPoints)
                touchPoints.rename(columns=stripSeries(dataFrame.iloc[6]), inplace=True)
            else:
                touchPoints.rename(columns=stripSeries(dataFrame.iloc[5]), inplace=True)
            journey = extractJourneyInfo(dataFrame, id)
            initiator = touchPoints.columns.get_loc("Actor who initiated")
            receiver = touchPoints.columns.get_loc("Actor who received")
            tclist = np.array(
                [
                    str(elem).upper() if isinstance(elem, str) else elem
                    for elem in touchPoints.iloc[:, initiator].values
                ]
            )
            tclist2 = np.array(
                [
                    str(elem).upper() if isinstance(elem, str) else elem
                    for elem in touchPoints.iloc[:, receiver].values
                ]
            )
            for value, (key, value) in enumerate(userMapping.items()):
                if value not in journey.actors and (
                    str.upper(key) in tclist or str.upper(key) in tclist2
                ):
                    journey.actors.append(value)
            for index2, line in touchPoints.iterrows():
                if checkIncludeFlag(line["Include"]) and not pd.isnull(
                    line["Actor who initiated"]
                ):
                    touchPoint = parseTouchPoint(line, userMapping)
                    journey.addTouchPoints(touchPoint)
            journey.Phases = list(set(PhaseList))
            XMlList.ActualJourney.append(journey)
            XMlList.user = journey.creator
            id = id + 1
            loop = True
            if action == "sort" or action == "group" or action == "icons":
                journey = sortUser(journey)
        saveXML(XMlList)


def sortUser(journey):
    global tempActors
    root = tk.Tk()
    userMapping = {}
    listbox = Drag_and_Drop_Listbox(root)
    sortUsersWindow(journey, root, listbox)
    for value in journey.actors:
        for actor in tempActors:
            if len(value) == 2 and actor == value[0]:
                userMapping[actor] = value
                break
            elif actor == value:
                userMapping[actor] = value
                break
    journey.actors = userMapping
    return journey


def sortUsersWindow(journey, root, listbox):
    tk.Label(
        root,
        text="Please sort the actors in the order they appear in the journey using drag-and-drop.",
        font=("Arial", 10),
    ).pack(pady=10)
    for i, name in enumerate(journey.actors):
        if len(name) == 2:
            listbox.insert(tk.END, name[0])
        else:
            listbox.insert(tk.END, name)
        if i % 2 == 0:
            listbox.selection_set(i)
    bSkip = tk.Button(
        root,
        text="Finish ordering",
        width=25,
        command=lambda: on_closings(root, listbox),
    )
    listbox.pack(fill=tk.BOTH, expand=True)
    bSkip.pack(fill=tk.BOTH, expand=True)
    listbox.bind("<<ListboxSelect>>", change_Colors(listbox))
    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)
    root.mainloop()


def change_Colors(listbox):
    for i in range(listbox.size()):
        if i % 2 == 0:  # Even indices
            listbox.itemconfig(i, bg="lightblue")
        else:  # Odd indices
            listbox.itemconfig(i, bg="lightyellow")


def saveXML(cjml: cjml.CJML):
    global endUser, fileName
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%Y_%m_%d")
    with open(f"{formatted_date}_{fileName}.xml", "w", encoding="utf-8") as file:
        file.write(cjml.toXML(endUser))
    tk.messagebox.showinfo("Success", "The XML file has been created successfully!")


def organizeUsers(sheet):
    window = tk.Tk(screenName="Select users")

    window.title("Create user mapping " + sheet)
    label = tk.Label(
        window, text="Please provide user name when grouping", font=("Arial", 14)
    )
    label.grid(row=0, columnspan=3, column=0)

    labelName = tk.Label(window, text="User generic name:")
    labelName.grid(row=1, columnspan=3, sticky="nsew")
    frame = tk.Frame(window)
    text = tk.Text(window, height=1)
    text.grid(row=2, columnspan=3, sticky="nsew", padx=50, pady=10)

    options, options2 = createBoxes(window, frame, 3)

    for index, sheet in enumerate(actorsList):
        if str.capitalize(str.lower(str(sheet))) not in options.get(0, options.size()):
            options.insert(index, sheet)

    frame.grid(row=3, column=1, padx=(20, 20), sticky="nsew", columnspan=1)

    b = tk.Button(
        window,
        text="Continue",
        width=25,
        command=lambda: saveActors(options, options2, text, window),
    )
    b.grid(row=4, columnspan=6, sticky="nsew", column=0, padx=50, pady=10)

    if hasActivatedGrouping == False:
        bSkip = tk.Button(
            window,
            text="Skip all grouping",
            width=25,
            command=lambda: breakGrouping(window),
        )
        bSkip.grid(row=5, columnspan=6, sticky="nsew", column=0, padx=50, pady=10)
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window))
    window.attributes('-topmost', True)
    window.update()
    window.attributes('-topmost', False)
    window.mainloop()


def breakGrouping(window):
    global skipGruping, loop
    answer = askyesno(
        title="confirmation", message="Are you sure that you want to skip the grouping?"
    )
    if answer:
        skipGruping = True
        loop = False
        window.destroy()


def on_closing(window):
    global goFoward
    answer = askyesno(
        title="confirmation", message="Are you sure that you want to close the window?"
    )
    if answer:
        goFoward = False
    window.destroy()


def on_closings(window, lists):
    global tempActors
    answer = askyesno(
        title="confirmation", message="Are you sure that you want to close the window?"
    )
    if answer:
        tempActors = lists.get(0, "end")
    window.destroy()


def selectSheets(sheets):
    global journeySheets
    journeySheets = [
        e
        for e in sheets
        if e
        not in (
            "Log",
            "User Guide",
            "Channels",
            "Actors",
            "Phases",
            "Simplifications",
            "About",
            "Screenshots",
            "Configure",
            'Input through "web form"',
        )
    ]


def createBoxes(window, frame, rowLocation):
    options = tk.Listbox(window)

    options2 = tk.Listbox(window)
    moveToRight = tk.Button(
        frame,
        text="→",
        width=10,
        command=lambda: moveElementFormOneBoxToOther(options, options2),
    )
    moveToLeft = tk.Button(
        frame,
        text="←",
        width=10,
        command=lambda: moveElementFormOneBoxToOther(options2, options),
    )

    moveToRight.pack(side="top", expand=True)
    moveToLeft.pack(side="top", expand=True)

    options.bind(
        "<Double-1>", lambda x: moveElementFormOneBoxToOther(options, options2)
    )
    options2.bind(
        "<Double-1>", lambda x: moveElementFormOneBoxToOther(options2, options)
    )

    options.grid(row=rowLocation, column=0, sticky="nsew", padx=10, pady=10)
    options2.grid(row=rowLocation, column=2, sticky="nsew", padx=10, pady=10)
    return options, options2


def saveActors(options: tk.Listbox, options2: tk.Listbox, input: tk.Text, window):
    global userMapping, actorsList, loop, hasActivatedGrouping
    fieldIsEmpty = ""
    hasActivatedGrouping = True
    inputExists = input.get("1.0", "end-1c") != ""
    userSelected = options2.size() > 0

    if not inputExists and userSelected:
        fieldIsEmpty = "No name for user was given. Please assign the name for the user"

    if inputExists and not userSelected:
        fieldIsEmpty = "No users were assigned to group. Please assign the users"

    if fieldIsEmpty == "" and userSelected:
        for i in options2.get(0, options2.size() - 1):
            userMapping[i] = input.get("1.0", "end-1c")
        actorsList = []
        for i in options.get(0, options.size() - 1):
            actorsList.append(i)
        window.destroy()
    elif fieldIsEmpty:
        messagebox.showerror("Error", fieldIsEmpty)

    if not inputExists and not userSelected:
        answer = askyesno(
            title="confirmation",
            message="Are you sure that you finished grouping users?",
        )
        if answer:
            loop = False
            window.destroy()


def moveElementFormOneBoxToOther(fromBox: tk.Listbox, toBox: tk.Listbox):
    for i in fromBox.curselection():
        toBox.insert(i, fromBox.get(i))
        fromBox.delete(i)


def interactionMapper(interaction):
    match interaction.lower():
        case "sms":
            return "sms"

        case "face2face":
            return "faceToFace"

        case "web/app":
            return "internetViaPC"

        case "e-mail":
            return "email"

        case "phone call":
            return "phone"

        case "chat":
            return "chat"

        case "letter (paper)":
            return "letter"

        case "self-service machine":
            return "selfServiceMachine"

        case "telephone":
            return "Telephone"

        case "social media message":
            return "Social Media Message"

        case "message":
            return "message"

        case "web/smartphone":
            return "Internet Via Smartphone"

        case "web/tablet":
            return "Internet Via Tablet"

        case "app/pc":
            return "appOnPc"

        case "app/smartphone":
            return "appOnSmartphone"

        case "app/tablet":
            return "appOnTablet"

        case "internet":
            return "Internet Globe"

        case "package delivery":
            return "Parcel"

        case "Fax":
            return "Fax"

        case "shop counter":
            return "ShopCounter"

        case "service desk":
            return "ServiceDesk"

        case "payment":
            return "Payment Channel"

        case "unknown":
            return "Unknown"

        case _:
            return interaction


def getActorsList(touchPoints):
    print(touchPoints.columns)
    initiator = touchPoints.columns.get_loc("Actor who initiated")
    receiver = touchPoints.columns.get_loc("Actor who received")
    actorsList = touchPoints.iloc[:, initiator].drop_duplicates().tolist()
    del actorsList[0]
    actorsList2 = touchPoints.iloc[:, receiver].drop_duplicates().tolist()
    del actorsList2[0]
    actorsList = actorsList + actorsList2
    options = []
    for element in actorsList:
        if not pd.isna(element):
            if str.capitalize(str.lower(element)) not in options and not (
                str.isspace(element)
            ):
                options.append(str.capitalize(str.lower(element)))
    return options


def parseTouchPoint(line, mapping):
    global endUser
    if pd.isnull((line["Actor who received"])):
        touchPoint = cjml.ActualAction()
    else:
        touchPoint = cjml.ActualCommunicationPoint()
        receiver = cjml.Receiver()
        receiver.refersTo = mapping[
            str.capitalize(str.lower(line["Actor who received"]))
        ]
        receiver.receiversLabel = line["Receiver's label"]
        touchPoint.receiver = receiver

    touchPoint.TouchPointID = line["TP ID"]
    if not (pd.isnull(line["Channel"])):
        touchPoint.chanell = interactionMapper(line["Channel"])
    if not (pd.isnull(line["Comment"])):
        touchPoint.comment = line["Comment"]

    initiator = cjml.Initiator()
    initiator.refersTo = mapping[str.capitalize(str.lower(line["Actor who initiated"]))]
    initiator.initatorLabel = line["Initiator's label"]

    touchPoint.initiator = initiator

    if not pd.isnull((line["Phase"])):
        phase = line["Phase"]
        PhaseList.append(phase)
        touchPoint.phase = phase
    if not pd.isnull((line["UX description"])) or not pd.isnull((line["UX rating"])):
        touchPoint.touchPointExperience = cjml.EndUserExperience()
    if not pd.isnull((line["UX description"])):
        touchPoint.touchPointExperience.experienceDescription = line[12]
    if not pd.isnull(line["UX rating"]):
        touchPoint.touchPointExperience.expienceRating = convertExperienceToGrade(
            line["UX rating"]
        )

    touchPoint.Devation = checkDevationFlag(line["Deviation"])
    if not (pd.isnull(line["Date"])):
        time = cjml.timeStamps()
        handledDate = handleDate(line["Date"])
        if pd.isnull(line["Time"]):
            time.timeCompleted = handledDate
        else:
            time.timeCompleted = handledDate.combine(
                handledDate, line["Time"]
            )  # issues

        touchPoint.timestamps = time

    return touchPoint


def convertExperienceToGrade(text):
    match text.lower():
        case "very satisfied":
            return 5
        case "satisfied":
            return 4
        case "neutral":
            return 3
        case "dissatisfied":
            return 2
        case "very dissatisfied":
            return 1


def handleDate(field):
    date = field
    if type(field) is str:
        date = parser.parse(field)
    return date


def extractJourneyInfo(dataframe, index):
    head = dataframe.head(5)

    actualJourney = cjml.ActualJourney()
    actualJourney.journeyID = index
    actualJourney.journeyShortSummary = head.iloc[3, 3]
    actualJourney.journeyStatus = head.iloc[2, 3]
    actualJourney.creator = head.iloc[4, 3]
    return actualJourney


def getFileLocation():
    try:
        file = filedialog.askopenfile(
            mode="r", filetypes=[("Excel", "*.xlsm  *.xlsx")]
        )  # handle the exception
        if file:
            filepath = os.path.abspath(file.name)
    except Exception:
        messagebox.showerror(
            "Python Error",
            "The application could not read the file. If it is opened using Excel, please close it and retry again",
        )
        filepath = getFileLocation()
    return filepath


def main():
    filePath = getFileLocation()
    readExcel(filePath)


if __name__ == "__main__":
    main()
