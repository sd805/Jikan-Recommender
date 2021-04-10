'''
This module defines the class used for keeping track of the user's settings.
'''

class userSettings():
    def __init__(self):
        self.minYear = 1990
        self.maxYear = 2005
        self.MALUsername = ""
        self.filteredAnime = set()
        self.filteredManga = set()