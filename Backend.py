from Jikan import Jikan
import Settings
from pathlib import Path
import json
import random

'''
The purpose of this module is to handle most of the calculations and data management
from the program, such as parsing JSON objects and creating the list of recommendations.
'''

# JikanObj is used to access members that call Jikan API 
JikanObj = Jikan()

'''
searchTitles takes the user's query to display titles closest to the query. The
user then picks a title from the list to return a tuple pair (titleName, titleID)
'''
def searchTitles(title: str, medium = "anime") -> tuple:
    # If user chose to quit, return empty pair
    if (title == 'q'):
        return ("", 0)

    # Replace spaces in query with URL space encoding
    title = title.replace(' ', '%20') 
    # Remove newlines
    title = title.replace('\n', '')

    print("Searching...")
    jsonResult = JikanObj.searchJikan(title, medium)

    results = []

    resultsLength = len(jsonResult['results'])

    for x in range(resultsLength):
        titleName = jsonResult['results'][x]['title']
        titleID = jsonResult['results'][x]['mal_id']
        searchTuple = (titleID, titleName)

        results.append(searchTuple)

    return results


'''
getSimilarUsers takes a titleID and returns a list of users who rated the
title favorably. The list of users is shuffled before returning so repeated
searches of a title can provide varied results.
'''
def getSimilarUsers(titleID: int, medium = "anime"):
    print("Gathering reviews...")
    jsonResult = JikanObj.findUserReviews(titleID, medium)

    userList = [] 
    for review in jsonResult['reviews']:
        if review['reviewer']['scores']['overall'] >= 8:
            userList.append(review['reviewer']['username'])

    random.shuffle(userList)
    return userList

'''
filterUserList takes a userSettings object and populates the anime/manga sets
by referencing a user on MyAnimeList. These sets will be used to filter out recommended 
titles the user has already seen.
'''
def filterUserList(settings: Settings.userSettings):
    settings.filteredAnime.clear()
    settings.filteredManga.clear()

    # Exit function if username is empty
    if settings.MALUsername == "":
        return

    print("Retrieving anime list...")
    pageNum = 1
    while True:
        # Each API call only returns 300 titles, so we may need to call again by incrementing the page number.
        jsonResult = JikanObj.retrieveUserList(settings.MALUsername, pageNum, "anime")

        for title in jsonResult['anime']:
            settings.filteredAnime.add(title['title'])
        
        print("Total anime:", len(settings.filteredAnime))

        # We can only retrieve 300 titles max per API call, so if the call doesn't 
        # return 300 titles, it means we're on the last page and don't need to loop anymore.
        if (len(jsonResult['anime']) != 300):
            break

        pageNum += 1

    

    print("\nRetrieving manga list...")
    pageNum = 1
    while True:
        # Each API call only returns 300 titles, so we may need to call again by incrementing the page number.
        jsonResult = JikanObj.retrieveUserList(settings.MALUsername, pageNum, "manga")

        for title in jsonResult['manga']:
            settings.filteredManga.add(title['title'])

        print("Total manga:", len(settings.filteredManga))
        
        # We can only retrieve 300 titles max per API call, so if the call doesn't 
        # return 300 titles, it means we're on the last page and don't need to loop anymore.
        if (len(jsonResult['manga']) != 300):
            break

        pageNum += 1

'''
getRecommendedList takes a list of users and compares their ratings to return a list of
titles that tend to be favored among those users. The list is sorted by titles with the
most overlap.
'''
def getRecommendedList(userList: list, settings, medium = "anime"):
    # In the titleOverlap dictionary, the key represents the title str and the
    # value represents the number of users that rated the title favorably.
    titleOverlap = dict()

    # The medium variable determines which set to check for filtering
    if medium == "anime":
        filteredList = settings.filteredAnime
    else:
        filteredList = settings.filteredManga

    # depth is the number of users that will be checked to find overlap.
    depth = min(5, len(userList))
    count = 0
    while count < depth:
        try:
            print("Checking user " + str(count+1)+"/"+str(depth)+"...")
            jsonResult = JikanObj.getTopScoringTitles(userList[count], medium)
            count += 1
        except:
            print("Can't access private list.")
            # Remove user from list and break if they were the last user in the list
            userList.pop(count)
            # Update depth after user is removed
            depth = min(5, len(userList))
            if count == len(userList):
                break
            else:
                continue

        for title in jsonResult[medium]:
            
            if title['score'] >= 8 and title['title'] not in filteredList:
                # If there is no date with the title, ignore it.
                if title['start_date'] == None:
                    continue
                # start_date begins with the year, so we grab a substring of the first 4 numbers.
                titleYear = int(title['start_date'][:4])
                if titleYear >= settings.minYear and titleYear <= settings.maxYear:
                    # If the tile is in the overlap dictionary, increment its value by 1. Otherwise
                    # add it to the dictionary and set its value to 1.
                    if title['title'] in titleOverlap:
                        titleOverlap[title['title']] += 1
                    else:
                        titleOverlap[title['title']] = 1

    resultList = []
    while len(titleOverlap) > 0:
        # Get the title with the highest value (overlap) and append it to resultList
        highestTitle = max(titleOverlap, key=titleOverlap.get)
        titleOverlap.pop(highestTitle)
        resultList.append(highestTitle)

    return resultList

'''
displayAndSave takes a list of titles and prints out the titles in chunks of 10 or less.
This function also gives the user the option to save the full list to a .txt file.
'''
def displayAndSave(recList: list, title: str, settings: Settings.userSettings):
    resultsLength = len(recList)
    displayCount = 0

    userInput = 'n'
    print("\nUsers that like " + str(title) + " tend to like these titles (from " + str(settings.minYear) + " to " + str(settings.maxYear) + "):")
    while userInput != 'q':
        # Show 10 or less results, depending on the number of search results
        for x in range(min(10, resultsLength - displayCount)): 
            print(str(displayCount + 1) + ': ' + recList[displayCount])
            displayCount += 1
        print("('n' to view the next 10 results, 'q' save and quit)")
        userInput = str(input())

    while userInput != 'y' and userInput != 'n':
        userInput = str(input("\nWould you like to save the results to a .txt file? (y/n) "))

        if userInput == 'y':
            dirInput = None
            # Exit if the path is Path('q') 
            while dirInput != Path('q'):
                print("\nInput a folder path where you want the file to be saved ('q' to quit):")
                dirInput = Path(input())
                if dirInput.is_dir():
                    filePath = dirInput.joinpath("MyRecommendations.txt")

                    # If the filename already exists, increment the filename so it doesn't overwrite anything.
                    count = 1
                    while filePath.exists():
                        filePath = dirInput.joinpath("MyRecommendations ("+str(count)+").txt")
                        count += 1

                    print("\nRecommendations saved to: ", filePath)
                    filePath.touch()

                    fileContent = "Users that like " + str(title) + " tend to like these titles (from " + str(settings.minYear) + " to " + str(settings.maxYear) + "):"
                    # Store the all the results in the string fileContent
                    for x in range(len(recList)):
                        fileContent += "\n" + str(x+1) +". " + str(recList[x])

                    filePath.write_text(fileContent, encoding='UTF-8')

                    dirInput = Path('q')
                
                elif dirInput != Path('q'):
                    print("Not a valid directory path.")


