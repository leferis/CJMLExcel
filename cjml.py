import pandas as pd
from datetime import datetime


class CJML:
    def __init__(self):
        self.plannedJourney = []
        self.ActualJourney = []
        self.user = ""

    def toXML(self, endUser):

        text = "<!-- Produced by: ExcelToCJML " + "Date:" + str(datetime.now())
        if not (self.user != ""):
            text += " produced by: " + self.user
        text += " -->\n"
        text += "<CJML version=\"2.0\">\n"
        for planed in self.plannedJourney:
            text += planed.toXML()
        for actual in self.ActualJourney:
            text += actual.toXML(endUser)
        text += "</CJML>"
        return text


class Journey:
    def __init__(self):
        self.journeyID = ""
        self.journeyTitle = ""
        self.journeyShortSummary = ""
        self.journeyLongSummary = ""
        self.journeyPhase = JourneyPhase()
        self.journeyOperators = ""
        self.journeyEndUserType = ""
        self.creator = ""

class JourneyPhase:
    def __init__(self):
        self.phaseName = ""
        self.phaseDescription = ""
        self.phaseId = ""
        self.phaseIDRef = ""


class EndUserExperience:
    def __init__(self):
        self.experienceDescription = ""
        self.expienceRating = ""

    def toXML(self):
        experienceText = ""
        experienceText += "<touchpointExperience>"
        experienceText += "<experienceDescription>{0}</experienceDescription>".format(self.experienceDescription)
        experienceText += "<experienceRating>{0}</experienceRating>".format(self.expienceRating)
        experienceText += "</touchpointExperience>"
        return experienceText

class AnalyzerResults:
    def __init__(self):
        self.Data = ""


class PlannedJourney(Journey):
    def __init__(self):
        super().__init__()
        self.actors = []
        self.touchpoints = []
        self.comment = ""
        self.JourneyAnalysis = AnalyzerResults()

    def toXML(self):
        super().toXML()

    def addTouchPoints(self, touchpoint):
        self.touchpoints.append(touchpoint)

    def addActor(self, actor):
        self.actors.append(actor)

class Actor:
    def __init__(self):
        self.actorName = ""
        self.IconName = ""

class ActualJourney(Journey):
    def __init__(self):
        super().__init__()
        self.journeyStatus = ""
        self.plannedReference = ""
        self.complianceContent = ""
        self.complianceSequence = ""
        self.complianceTiming = ""
        self.journeyExperience = EndUserExperience()
        self.actors = []
        self.touchpoints = []
        self.comment = ""
        self.JourneyAnalysis = AnalyzerResults()
        self.Phases = []

    def addTouchPoints(self, touchpoint):
        self.touchpoints.append(touchpoint)

    def addActor(self, actor):
        self.actors = self.actors + actor

    def sortActors(self, endUser):
        endUsers = []
        otherActors = []
        if (isinstance(self.actors, dict)):
            for a in self.actors.values():
                self.assignActors(a, endUser, endUsers, otherActors)
        else:
            for a in self.actors:
                self.assignActors(a, endUser, endUsers, otherActors)
        self.actors = endUsers + otherActors

    def assignActors(self, a, endUser,  endUsers, otherActors):
        if a in endUser:
            endUsers.append(a)
        else:
            otherActors.append(a)

    def toXML(self, endUser):
        self.sortActors(endUser)
        test = "<actualJourney>\n"
        test += "<journeyID>AJ{0}</journeyID>\n".format(self.journeyID)
        test += "<journeyTitle>{0}</journeyTitle>\n".format(self.journeyTitle) if self.journeyTitle != "" else ""
        test += "<plannedReference>PJ1</plannedReference>" # delete later
        if len(self.Phases) > 0:
            test += "<journeyPhases>\n"
            for phase in self.Phases:
                test += "<journeyPhase phaseID =\" "+phase+"\">\n"
                test += "<phaseName> {0}</phaseName>\n".format(phase)
                test += "<phaseDescription></phaseDescription>\n"
                test += "</journeyPhase>\n"
            test += "</journeyPhases>\n"
        test += "<journeyShortSummary>{0}</journeyShortSummary>\n".format(self.journeyShortSummary) if self.journeyShortSummary != "" else ""
        test += "<journeyLongSummary>{0}</journeyLongSummary>\n".format(self.journeyLongSummary) if self.journeyLongSummary != "" else ""
        test += "<journeyStatus>{0}</journeyStatus>\n".format(self.journeyStatus) if self.journeyStatus != "" else ""
        test += "<actors>\n"
        userList = ""
        for actor in self.actors:
            if actor in endUser:
                if len(actor) == 2:
                    userList = "<!-- {0} -->\n".format(actor[1]) + userList
                userList = "<endUser actorID =\"{0}\"/>\n".format(actor[0] if len(actor) == 2 else actor) + userList
            else:
                if len(actor) == 2:
                    userList = userList + "<!-- {0} -->\n".format(actor[1])
                userList = userList + "<serviceProvider actorID =\"{0}\"/>\n".format(actor[0] if len(actor) == 2 else actor)

        test += userList
        test += "</actors>\n"
        test += "<touchpoints>\n"
        for index, touchPoint in enumerate(self.touchpoints):
            test += touchPoint.toXML(index)
        test += "</touchpoints>\n"
        test += "</actualJourney>\n"
        return test


class TouchPoint:
    def __init__(self):
        self.TouchPointID =""
        self.uncertinty = ""
        self.category = ""


class ActualTouchPoint(TouchPoint):
    def __init__(self):
        super().__init__()
        self.compliance = ""


class PlannedAction(TouchPoint):
    def __init__(self):
        super().__init__()
        self.initiator = Initiator()
        self.deltaTime = ""
        self.touchPointDuration = ""
        self.comment = ""
        self.levelAnalysis = AnalyzerResults()


class ActualAction(ActualTouchPoint):
    def __init__(self):
        super().__init__()
        self.initiator = Initiator()
        self.timeStarted = ""
        self.timeCompleted = ""
        self.touchpointExperience = EndUserExperience()
        self.comment = ""
        self.analysis = AnalyzerResults()
        self.Devation = False
        self.phase = ""
        self.TouchPointID= ""

    def toXML(self, index):
        action = "<actualAction>\n"
        action += "<touchpointID>{0}</touchpointID>\n".format( self.TouchPointID if not pd.isna(self.TouchPointID) else index )
        action += "<belongsTo phaseIDref =\"" + self.phase + "\"></belongsTo>"
        action += self.initiator.toXML()
        action += "<comment>{0}</comment>\n".format(self.comment)
        print(hasattr(self, 'touchPointExperience'))
        if hasattr(self, 'touchPointExperience'):
            action += self.touchpointExperience.toXML()
        if hasattr(self, 'category'):
            action += "<category>{0}</category>\n".format(self.category)
        action += "</actualAction>\n"
        return action


class PlannedCommunicationPoint(TouchPoint):
    def __init__(self):
        super().__init__()
        self.initiator = Initiator()
        self.receiver = Receiver()
        self.channel = "" 
        self.message = ""
        self.touchPointDuration = ""
        self.comment =""
        self.touchPointAnalysis = AnalyzerResults()


class ActualCommunicationPoint(ActualTouchPoint):
    def __init__(self):
        super().__init__()
        self.initiator = Initiator()
        self.receiver = Receiver()
        self.chanell = ""
        self.message = ""
        self.timestamps = timeStamps()
        self.touchPointExperience = EndUserExperience()
        self.comment = ""
        self.touchLevelAnalysis = AnalyzerResults()
        self.Devation = False
        self.phase = ""

    def toXML(self, index):
        self.resolveTouchpointId(index)
        communicationPoint = "<actualCommunicationPoint>\n"
        communicationPoint += "<touchpointID>{0}</touchpointID>\n".format(self.TouchPointID if not pd.isna(self.TouchPointID) else index)
        communicationPoint += "<belongsTo phaseIDref =\""+ self.phase+"\"></belongsTo>"
        communicationPoint += self.receiver.toXML()
        communicationPoint += self.initiator.toXML()
        communicationPoint += "<channel>\n<channelName>{0}</channelName>\n</channel>\n".format(self.chanell)
        communicationPoint += "<comment>{0}</comment>\n".format(self.comment)
        communicationPoint += self.timestamps.toXML()
        if hasattr(self, 'touchPointExperience'):
            communicationPoint += self.touchPointExperience.toXML()
        if hasattr(self, 'category'):
            communicationPoint += "<category>{0}</category>\n".format(self.category)
        communicationPoint += "</actualCommunicationPoint>\n"
        return communicationPoint

    def resolveTouchpointId(self, index):
        if pd.isna(self.TouchPointID):
            self.TouchPointID = index
        if self.Devation == True:
            self.TouchPointID = "D" + str(index)


class Initiator:
    def __init__(self):
        self.refersTo = ""
        self.initatorLabel = ""

    def toXML(self):
        text = "<initiator>\n"
        text += "<refersTo actorIDref=\"{0}\"/>\n".format(self.refersTo[0] if len(self.refersTo) == 2 else self.refersTo)
        text += "<initiatorLabel>{0}</initiatorLabel>\n".format(self.initatorLabel if not pd.isnull(self.initatorLabel) else 'Sending') 
        text += "</initiator>\n"
        return text


class Receiver:
    def __init__(self):
        self.refersTo = ""
        self.receiversLabel = ""

    def toXML(self):
        nl = "\n"
        text = "<receiver>\n"
        text += f'''<refersTo actorIDref="{self.refersTo[0] if len(self.refersTo) == 2 else self.refersTo}"/>{nl}'''
        text += "<receiverLabel>{0}</receiverLabel>\n".format(self.receiversLabel if not pd.isnull(self.receiversLabel) else 'Receiving') 
        text += "</receiver>\n"
        return text



class timeStamps:
    def __init__(self):
        self.timeOriginated = ""
        self.timeReceived = ""
        self.timeConsumed = ""
        self.timeStarted = ""
        self.timeCompleted = ""

    def toXML(self):
        text = ""
        text += "<timestamps>\n"
        text += "<timeOriginated>{0}</timeOriginated>\n".format(self.timeOriginated) if self.timeOriginated != "" else ""
        text += "<timeReceived>{0}</timeReceived>\n".format(self.timeReceived) if self.timeReceived != "" else ""
        text += "<timeConsumed>{0}</timeConsumed>\n".format(self.timeConsumed) if self.timeConsumed != "" else ""
        text += "<timeStarted>{0}</timeStarted>\n".format(self.timeStarted) if self.timeStarted != "" else ""
        text += "<timeCompleted>{0}</timeCompleted>\n".format(self.timeCompleted) if self.timeCompleted != "" else ""
        text += "</timestamps>\n"
        return text
