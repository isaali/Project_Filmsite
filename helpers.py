import urllib.request, requests, json, urllib, datetime
from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from urllib.request import urlopen
from API import *

db = SQL("sqlite:///nlfilms.db")

def accountverwijderenform():
    """ Delete account form """
    # requests input which have been filled in
    wachtwoord = request.form.get("wachtwoord")
    wachtwoord_herhaling = request.form.get("wachtwoord_herhaling")

    # if there is no input, return error for next 4 codelines
    if not wachtwoord:
        return apology("Geef jouw wachtwoord op.")

    if not wachtwoord_herhaling:
        return apology("Geef herhaling van jouw wachtwoord op.")

    # if the password does not equal the confirmation, return error
    if wachtwoord != wachtwoord_herhaling:
        return apology("De bevestiging komt niet overeen met het wachtwoord.")

def apology(message, code=400):
    """Renders message as an apology to user."""

    return render_template("apology.html",
        top = code,
        bottom = message,
        lengte = lengte_vv(),
        tipslengte = tipslength(),
        totaal = (tipslength() + lengte_vv()))

def apologynon(message, code=400):
    """Renders message as an apology to user."""

    return render_template("apologynon.html", top=code, bottom=message)

def lengte_vv():
    """ Notifications for friend requests """
    gebruikersnaam = gebruiker()
    verzoeken = verzoek()

    if verzoeken:
        lengte = len(verzoeken)
        return lengte

    else:
        lengte = 0
        return lengte

def loginform():
    """ Checks if inputbars from registerform are filled in"""
    # checks if the inputbars are filled in, else return errors
    if not request.form.get("gebruiker-inloggen"):
        return apologynon("Geef een gebruikersnaam op")

    if not request.form.get("wachtwoord-inloggen"):
        return apologynon("Geef een wachtwoord op")

def login_required(f):
    """ Decorate routes to require login. http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/ """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# reqeuest info from submit
def ophalen(name):
    opgehaald = request.form.get(name)
    return opgehaald

# returns friendname from post.method
def profielvriend():
    profiel = request.form.get("profiel")

    if profiel == None:
        profiel = request.form.get("profiel1")
        return profiel

    else:
        return profiel

def registerform():
    """ Check if inputbars are filled in from registerform """
    if not request.form.get("gebruikersnaam"):
        return apologynon("Geef een gebruikersnaam op.")

    # ensure password was submitted
    elif not request.form.get("wachtwoord"):
        return apologynon("Geef een wachtwoord op.")

    # ensure password-confirmation was submitted
    elif not request.form.get("wachtwoord-confirmatie"):
        return apologynon("Geef het wachtwoord nogmaals op.")

    # ensure password equals password confirmation
    if request.form.get("wachtwoord") != request.form.get("wachtwoord-confirmatie"):
        return apologynon("De bevestiging komt niet overeen met het wachtwoord.")

    # ensure the security question has been answered
    elif not request.form.get("veiligheidsvraag"):
        return apologynon("Beantwoord de veiligheidsvraag.")

def passwordformgeb():
    """ Check if inputbars are filled in from passwordform users"""
    # ensure if password was submitted
    if not request.form.get('wachtwoord'):
        return apology("Vul je huidige wachtwoord in")

    # ensure if new password was submitted
    if not request.form.get("nieuw_wachtwoord"):
        return apology("Vul een nieuw wachtwoord in")

    # ensure if password-confirmation was submitted
    if not request.form.get("wachtwoord_herhaling"):
        return apology("Herhaal je nieuwe wachtwoord")

def passwordformnon():
    """ Check if inputbars are filled in from passwordform non-users"""
    # ensure if username was submitted
    if not request.form.get('gebruikersnaam'):
            return apologynon("Vul je gebruikersnaam in")

    # ensure if new password was submitted
    if not request.form.get("nieuw_wachtwoord"):
        return apologynon("Vul een nieuw wachtwoord in")

    # ensure if new password-confirmation was submitted
    if not request.form.get("wachtwoord_herhaling"):
        return apologynon("Herhaal je nieuwe wachtwoord")

    # ensure if new password equals new password-confirmation
    if request.form.get("nieuw_wachtwoord") != request.form.get("wachtwoord_herhaling"):
        return apologynon("De wachtwoorden komen niet overeen")

    # ensure if security question has been answered
    if not request.form.get('veiligheidsvraag'):
        return apologynon("Beantwoord de veiligheidsvraag.")

####### SQL ######## everything underneath has SQL in it ################
# request all tips from friends to you
def aanbevelingenn():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar = gebruikersnaam)

# request all tips to friends
def aanbevelingenvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM aanbevelingen WHERE naar=:naar", naar=profiel)

# request all tips from you
def aanbevelingenvann():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=gebruikersnaam)

# request all tips from friends
def aanbevelingenvanvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM aanbevelingen WHERE van=:van", van=profiel)

def addtohistory(tmdb_id, tmdb_response):
    """ Add to history """
    # returns film_ids for this user from the favorites table
    historie = db.execute("SELECT film_id FROM historie WHERE gebruiker=:gebruiker", gebruiker = gebruiker())

    # insert into historie if film_id is not already in this table for this user
    if len(historie) == 0:
        db.execute("INSERT INTO historie (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                    afbeelding = tmdb_response["poster_path"])

    alinhistorie = db.execute("SELECT * FROM historie WHERE film_id=:film_id AND gebruiker=:gebruiker", gebruiker=gebruiker(), film_id=tmdb_id)
    if not alinhistorie:
        db.execute("INSERT INTO historie (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                    afbeelding = tmdb_response["poster_path"])

# request all your checkins
def checkinss():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

# request all checkins from friends
def checkinsvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM checkins WHERE gebruiker=:gebruiker", gebruiker=profiel)

# request all your favorites
def favorietenn():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

# request all favorites from friend
def favorietenvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM favorieten WHERE gebruiker=:gebruiker", gebruiker=profiel)

# request username which is logged in
def gebruiker():
    a = db.execute("SELECT gebruikersnaam FROM gebruikers WHERE id=:id", id=session["user_id"])
    return(a[0]["gebruikersnaam"])

# request historie info for the user
def geschiedenis():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker = gebruikersnaam)

# request historie info for the user
def geschiedenisvriend():
    profiel = profielvriend()
    return db.execute("SELECT * FROM historie WHERE gebruiker=:gebruiker", gebruiker=profiel)

# request listinformation
def lijsten1():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gez_lijst IS NULL AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker = gebruikersnaam, nieuwe_lijst="ja")

# request joint listinformation (in one direction)
def lijsten2():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker=:gebruiker AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker = gebruikersnaam, nieuwe_lijst="ja")

# request joint listinformation (in other direction)
def lijsten3():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM lijsten WHERE gez_lijst IS NOT NULL AND gebruiker2=:gebruiker2 AND nieuwe_lijst=:nieuwe_lijst",
                        gebruiker2 = gebruikersnaam, nieuwe_lijst="ja")

def sql_gezamenlijke_lijst_gemaakt(gebruikersnaam, direction, lijstnaam):
    ''' Make a joint list if there is no list with the user which has been requested '''
    #checks if you have a list with this friend in both directions
    check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
        gebruiker=gebruikersnaam, gebruiker2=direction, lijstnaam=lijstnaam)
    check2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
        gebruiker2=gebruikersnaam, gebruiker = direction, lijstnaam=lijstnaam)

    # if so, return error that you have a list with this friend
    if check1 or check2:
        tekst = "Je hebt al een lijst die " + lijstnaam + " heet met deze vriend"
        return apology(tekst)

    # else make a joint list
    else:
        db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, gebruiker2, gez_lijst, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :gebruiker2, :gez_lijst, :nieuwe_lijst)",
            gebruiker=gebruikersnaam, lijstnaam=lijstnaam, gebruiker2 = direction, gez_lijst="ja", nieuwe_lijst="ja")


def tipslength():
    ''' Notifications of tips in navbar(layout) USED MULTIPLE TIMES'''
    gebruikersnaam = gebruiker()

    tips = db.execute("SELECT van FROM aanbevelingen WHERE naar=:naar", naar = gebruikersnaam)

    if tips:
        tipslengte = len(tips)
    else:
        tipslengte = 0
    return tipslengte

def verzoek():
    ''' Check if you have some requests '''
    return(db.execute("SELECT van FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd AND uitgenodigd=:uitgenodigd AND afgewezen=:afgewezen",
                            naar = gebruiker(), geaccepteerd="nee", uitgenodigd="ja", afgewezen="nee"))

# friends of you in one direction
def vrienden1():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                        naar = gebruikersnaam, geaccepteerd="ja")

# friends of friend in one direction
def vriendenvriend1():
    profiel = profielvriend()
    return db.execute("SELECT * FROM verzoeken WHERE naar=:naar AND geaccepteerd=:geaccepteerd",
                        naar=profiel, geaccepteerd="ja")

# friends of you in other direction
def vrienden2():
    gebruikersnaam = gebruiker()
    return db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                        van=gebruikersnaam, geaccepteerd="ja")

# friends of you in other direction
def vriendenvriend2():
    profiel = profielvriend()
    return db.execute("SELECT * FROM verzoeken WHERE van=:van AND geaccepteerd=:geaccepteerd",
                       van=profiel, geaccepteerd="ja")