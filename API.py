'''
API requests from the following sources:
• https://www.themoviedb.org/documentation/api
• http://www.omdbapi.com
'''
import urllib.request, requests, json, urllib, datetime
from flask import redirect, render_template, request, session
from functools import wraps
from urllib.request import urlopen

'''
Parameters & keys
'''
tmdb_no_adult = "&include_adult=false"
tmdb_nl = "&language=nl"
tmdb_key = "9c226374f10b2dcd656cf7c348ee760a"
omdb_key = "be77e5d"

'''
Requests/functions:
'''

def results_per_page(searchterm, pagenr):
    '''
    Return all results for an individual searchresults page.
    '''
    url = "https://api.themoviedb.org/3/search/movie?api_key=" + tmdb_key + tmdb_nl + "&query=" + searchterm + tmdb_no_adult + "&page=" + str(pagenr)
    return(json.loads(str((requests.get(url).content).decode('UTF-8'))))

def total_results(searchterm):
    '''
    Collect results for the first 30 (or less) searchresults pages.
    '''
    total_pages = results_per_page(searchterm, pagenr=1)["total_pages"]
    searchresults = []
    pagenr = 1

    # Keep adding results till limit has been reached (30).
    while pagenr < 30 and pagenr <= total_pages:
        searchresults += results_per_page(searchterm, pagenr)["results"]
        pagenr += 1
    return([i for i in searchresults if i["original_language"] == "nl"])

def rfi_TMDb(tmdb_id):
    '''
    Request film information for a specific TMDb film ID.
    '''
    from urllib.request import urlopen
    tmdb_url = str( "https://api.themoviedb.org/3/movie/" + tmdb_id + "?api_key=" + tmdb_key + "&language=nl")
    return(json.loads(str((requests.get(tmdb_url).content).decode('UTF-8'))))

def rfi_OMDb(tmdb_response):
    '''
    Request film information for a specific IMDb film ID.
    '''
    # no IMDb ID
    if tmdb_response["imdb_id"] == None or "tt" not in tmdb_response["imdb_id"]:
        return(None)
    # valid IMDb ID
    else:
        omdb_url = str("http://www.omdbapi.com/?i=" + tmdb_response["imdb_id"] + "&apikey=" + omdb_key)
        return(json.loads(str((requests.get(omdb_url).content).decode('UTF-8'))))

# shows popular films
def popular_films():
    return(json.loads(str((requests.get("https://goo.gl/1wCPmP").content).decode('UTF-8'))))

# shows new films with parameters and keys
def new_films():
    return(json.loads(str((requests.get("https://api.themoviedb.org/3/discover/movie?api_key="
        + tmdb_key + tmdb_nl + "&year=" + str(datetime.date.today().year) + tmdb_no_adult
        + "&sort_by=popularity.desc&page=1&with_original_language=nl").content).decode('UTF-8'))))
