import json
from participant_data_handling.participant import Participant
from heapq import nlargest

'''************************************************************
    CLASS: ParticipantData:
    Handle Particpant information during & after competition. 
************************************************************'''
class ParticipantData:

    # Static Member: participants - holds participant stats
    participants_stats: dict
    participants_stats = {} # Participants

    # Singleton requirement: Static Instance representing the class
    __instance = None

    # Implemented singleton design pattern to prevent multiple instantiations of UserData class.
    def __init__(self):
        if ParticipantData.__instance == None:
            ParticipantData.__instance = self
        else:
            raise Exception("[ERROR]: Cannot create another instance of class: Points. Singlton implemented.")

    @staticmethod
    def get_instance():
        if ParticipantData.__instance == None:
            ParticipantData.__instance = ParticipantData()    
        return ParticipantData.__instance

    def init_points(self):
        # create file if doesnt exist
        with open('participant_data_handling/participantStats.json', 'a+') as f:
            pass

        with open('participant_data_handling/participantStats.json', 'r') as f:
            fileContent: str = f.read()
            
        if fileContent == "":
            self.participants_stats= {}
            
        else:
            self.participants_stats = json.loads(fileContent)

    '''
    """NOT FOR PUBLIC USE: internal method only. """
    def __add_points(self, userID: int , points=1):
        userID = str(userID)
        if self.pointMap.get(userID) == None:
            self.pointMap[userID] = 0
        self.pointMap[userID] += points
        self.update()

        #updates personal stats for participant
        #self.updatePoints(userID, points, True)
    '''

    def add_participant(self, userID: int): #add participant upon getting role / leave stats if role removed?
        userID = str(userID)
        if self.participants_stats.get(userID) == None:
            self.participants_stats[userID] = Participant()

    def get_participant_printed_stats(self, userID: int):
        userID = str(userID)
        return self.participants_stats[userID].to_string()

    # get top scores
    def get_top(self, amount=20) -> list[int]:
        return nlargest(amount, self.participants_stats, key=lambda x: self.participants_stats[x].points)

    # get points of an individual user
    def get_points(self, userID: int ):
        userID = str(userID)
        if self.participants_stats.get(userID) == None:
            self.add_participant(userID)
        return self.participants_stats[userID].get_points()
    
    def update_win_stats(self, userID: int):
        self.participants_stats[userID].update_win()

    def update_stats(self, userID: int, difficulty: str, points_recieved: int, was_first: bool):
        userID = str(userID)
        if self.participants_stats.get(userID) == None:
            self.add_participant(userID)
        self.participants_stats[userID].update_stats(difficulty, points_recieved, was_first)
        self.update_files()

    #TODO: Add functionality for participant data
    # updates file (idk im just calling it everytime there's a change just in case the bot crashes)
    def update_files(self):
        with open('participant_data_handling/participantStats.json', 'w') as f:
            (json.dump(self.participants_stats, indent=2))

    # clears current scores
    def clear(self):
        self.participants_stats = {k.clear_points() for k, v in self.participants_stats.items()}
        self.update_files()

    '''  Don't think we need this handled here. Moved.
    def update_points(self, userID: int, difficulty: int, first: bool):
        baseValue, multiplier, firstBonus= 0,1,0
        userID = str(userID)
        user = self.particpants[userID]

        if first:
            user.first += 1
            firstBonus = 1
        user.problemsSolved += 1
        user.totalPoints += baseValue + difficulty*multiplier + firstBonus
        if difficulty == "1":
            user.easy += 1
        elif difficulty == "2":
            user.medium += 1
        elif difficulty == "3":
            user.hard += 1
    '''