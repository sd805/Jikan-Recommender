'''
This module specifies class members for calling certain APIs from Jikan API.
API reference: https://jikan.docs.apiary.io/
'''

import urllib, json
from urllib import request,error

class Jikan:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        
    def callJikan(self, url):
        response = None
        jsonObject = None
        request = urllib.request.Request(url, None, self.headers)
        
        try:
            response = urllib.request.urlopen(request)
            jsonRaw = response.read()
            jsonObject = json.loads(jsonRaw)

        except urllib.error.HTTPError as e:
            raise Exception('\nFailed to download contents of URL\nStatus code: {}\n'.format(e.code))
        
        except json.decoder.JSONDecodeError:
            raise Exception("\nError: Invalid data format from API for JSON decoding\n")

        finally:
            if response != None:
                response.close()
        
        return jsonObject
    
    '''
    searchJikan takes a string query and returns a JSON object with titles closest to the query.
    '''
    def searchJikan(self, title: str, medium = "anime"):
        url = "https://api.jikan.moe/v3/search/"+medium+"?q=" + str(title)
        return self.callJikan(url)

    '''
    findUserReviews returns a JSON object of all user reviews from a selected title.
    '''
    def findUserReviews(self, titleID: int, medium = "anime"):
        url = "https://api.jikan.moe/v3/"+medium+"/"+str(titleID)+"/reviews"
        return self.callJikan(url)
        
    '''
    retrieveUserList returns a JSON object of the first 300 titles in the user's anime/manga list, with 
    the other titles being retrieved by incrementing the pageNum parameter.
    '''
    def retrieveUserList(self, username, pageNum, medium = "anime"):
        url = "https://api.jikan.moe/v3/user/"+username+"/"+medium+"list/completed/"+str(pageNum)
        return self.callJikan(url)

    '''
    getTopScoringTitles returns a JSON object of the user's anime/manga list sorted by highest score to lowest.
    '''
    def getTopScoringTitles(self, username, medium = "anime"):
        url = "https://api.jikan.moe/v3/user/"+username+"/"+medium+"list?q=&order_by=score&sort=desc"
        return self.callJikan(url)