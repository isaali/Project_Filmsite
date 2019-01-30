from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import datetime, requests, json, xml.etree.ElementTree, urllib
from helpers import *
from API import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///nlfilms.db")

'''
On alphabetical order
Some functions are made in helpers.py and API.py to prevent repitition with many codelines
See helpers.py and API.py
'''

# redirect to homepage
@app.route("/")
def homepage():
    ''' Homepage with popular and new films '''
    # returns homepage with the popular and new films with the API of IMDB AND OMDB (see API.py)
    return render_template("homepage.html", popular=popular_films()["results"], new=new_films()["results"])

@app.route("/accountverwijderen", methods=["GET", "POST"])
@login_required
def accountverwijderen():
    ''' Delete account '''
    # if something has been submitted with the POST method
    if request.method == "POST":

        # checks if the inputbars with passwords are filled in and if the password-confirmation equals the password
        accountverwijderenform()

        # check for password of the user in the database
        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=gebruiker())

        # if the new password does not equal the current password of the user, return error
        if len(wachtwoordcheck) != 1 or not pwd_context.verify(request.form.get("wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Het opgegeven wachtwoord klopt niet")

        else:
            # user will be logged out
            session.clear()

            # delete user from database
            db.execute("DELETE FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam", gebruikersnaam=gebruiker())
            db.execute("DELETE FROM verzoeken WHERE naar=:naar OR van=:van", naar=gebruiker(), van=gebruiker())

            # returns message that account has been deleted (other paramaters are for notifications)
            return render_template("/message/verwijderd.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal= (lengte_vv()+ tipslength()))

    # if the request method is not post, render the accountverwijderen template (other paramaters are for notifications)
    return render_template("accountverwijderen.html", lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal= (lengte_vv()+ tipslength()))

@app.route("/addcheckins", methods=["POST"])
@login_required
def addcheckins():
    ''' Add films to your check-ins '''
    # if something has been submitted with the POST method
    if request.method == "POST":

        # requests filminformation for a specific TMDB film with tmdb_id (posted with button name favorieten)
        tmdb_response = rfi_TMDb(request.form.get("favorieten"))
        omdb_response = rfi_OMDb(tmdb_response)

        # adds film into check-ins table with the parameters mentioned below (some of them are from helpers.py)
        db.execute("INSERT INTO checkins (gebruiker, film_id, titel, afbeelding) VALUES \
                  (:gebruiker, :film_id, :titel, :afbeelding)",
                  gebruiker = gebruiker(), film_id =request.form.get("favorieten"), titel = tmdb_response["original_title"],
                  afbeelding = tmdb_response["poster_path"])

        # return message that the film has been added to your check-ins (other paramaters are for notifications)
        # checkinss() is a function from helpers.py and requests the check-ins for this user
        return render_template("/message/addcheckins.html", tmdb = tmdb_response, omdb=omdb_response, checkins=checkinss(),
                                lengte = lengte_vv(), tipslengte = tipslength(), totaal = tipslength() +lengte_vv())

@app.route("/addfavorite", methods=["POST"])
@login_required
def addfavorite():
    ''' Add films to your favorites '''
    # if something has been submitted with the POST method
    if request.method == "POST":

        # requests filminformation for a specific TMDB film with tmdb_id (posted with button name favorieten)
        tmdb_response = rfi_TMDb(request.form.get("favorieten"))
        omdb_response = rfi_OMDb(tmdb_response)

        # adds film into favorites table with the parameters mentioned below (some of them are from helpers.py)
        db.execute("INSERT INTO favorieten (gebruiker, film_id, titel, afbeelding) VALUES (:gebruiker, :film_id, :titel, :afbeelding)",
                    gebruiker = gebruiker(), film_id = request.form.get("favorieten"), titel = tmdb_response["original_title"],
                    afbeelding = tmdb_response["poster_path"])

        # return message that the film has been added to your favorites (other paramaters are for notifications)
        # favorietenn() is a function from helpers.py and requests the favorites for this user
        return render_template("/message/addfavorite.html", tmdb = tmdb_response, omdb=omdb_response, favorieten=favorietenn(),
                                lengte = lengte_vv(), tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()))


@app.route("/addtolist", methods=["POST"])
@login_required
def addtolist():
    ''' Add films to your favorites '''
    # if something has been submitted with the POST method
    if request.method == "POST":

        # requests the values with these parameters
        tmdb_id = request.form.get("buttonfilm")
        lijst = request.form.get("lijst")

        # requests filminformation for a specific TMDB film with tmdb_id
        tmdb_response = rfi_TMDb(tmdb_id)
        omdb_response = rfi_OMDb(tmdb_response)

        # splits the lijst in 2 strings, this one for the listname (if the )
        lijstnaam = lijst.split('|')[0]

        # if there is no friendname inside the requested lijst, add an individual list
        if len(lijst) == len(lijstnaam):
            # checks if the film is already in list with same requested list name
            lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND \
                                    afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND nieuwe_lijst IS NULL",
                                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                                    afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam)

            # if film is already in list, return error
            if lijstinfo:
                tekst = "Deze film staat al in je lijst: " + lijstnaam
                return apology(tekst)

            # else insert the film into the list with the parameters mentioned below
            db.execute("INSERT INTO lijsten (gebruiker, film_id, titel, afbeelding, lijstnaam) VALUES \
                        (:gebruiker, :film_id, :titel, :afbeelding, :lijstnaam)",
                        gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                        afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam)

            # return message that the film is added to the individual list
            return render_template("/message/addtolist.html", tmdb = tmdb_response, omdb=omdb_response, lengte = lengte_vv(),
                                    tipslengte = tipslength(), totaal = tipslength() +lengte_vv(), lijstnaam = lijstnaam)

        else:
            # splits the lijst in 2 strings, this one for the friendname
            vriend = lijst.split('|')[1]

            # checks if the film is already in list with same requested list name with friend
            lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND \
                                    afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND \
                                    nieuwe_lijst IS NULL AND gebruiker2=:gebruiker2",
                                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                                    afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam, gebruiker2=vriend)

            # if film is already in list with this friend, return error
            if lijstinfo:
                tekst = "Deze film staat al in je gezamenlijke lijst: " + lijstnaam + "met:" + vriend
                return apology(tekst)


            if not lijstinfo:
                # checks if the film is already in list with same requested list name with friend
                lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND film_id=:film_id AND titel=:titel AND \
                                        afbeelding=:afbeelding AND lijstnaam=:lijstnaam AND gez_lijst IS NULL AND \
                                        nieuwe_lijst IS NULL AND gebruiker2=:gebruiker2",
                                        gebruiker=vriend, film_id = tmdb_id, titel = tmdb_response["original_title"],
                                        afbeelding=tmdb_response["poster_path"], lijstnaam=lijstnaam, gebruiker2 = gebruiker())

                # if film is already in list with this friend, return error
                if lijstinfo:
                    tekst = "Deze film staat al in je gezamenlijke lijst: " + lijstnaam + "met:" + vriend
                    return apology(tekst)

                else:
                    # else insert the film into the list with the parameters mentioned below
                    db.execute("INSERT INTO lijsten (gebruiker, film_id, gebruiker2, titel, afbeelding, lijstnaam) VALUES (:gebruiker, :film_id, :gebruiker2, :titel, :afbeelding, :lijstnaam)",
                    gebruiker = gebruiker(), film_id = tmdb_id, titel = tmdb_response["original_title"],
                    afbeelding = tmdb_response["poster_path"], lijstnaam = lijstnaam, gebruiker2=vriend)

                    # returns message that film has been added to list with a friend
                    return render_template("/message/addtolist.html", tmdb = tmdb_response, omdb=omdb_response, lengte = lengte_vv(),
                    tipslengte = tipslength(), totaal = tipslength() +lengte_vv(), lijstnaam = lijstnaam, vriend=vriend)

@app.route("/checkins", methods=["GET", "POST"])
@login_required
def checkins():
    ''' Render checkins page with your check-ins '''
    return render_template("checkins.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                            checkins=checkinss())

@app.route("/disclaimer")
@login_required
def disclaimer():
    ''' Render disclaimer '''
    return render_template("disclaimer.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()))

@app.route("/disclaimernon")
def disclaimernon():
    ''' Render disclaimer '''
    return render_template("disclaimernon.html")

@app.route("/favorieten", methods=["GET", "POST"])
@login_required
def favorieten():
    ''' Render favorites page with your favorites '''
    return render_template("favorieten.html", favorieten=favorietenn(), lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal= (lengte_vv()+ tipslength()))

@app.route("/filminfo", methods=["GET", "POST"])
@login_required
def filminformatie():
    ''' Render filminformation page with chosen film '''
    if request.method == "POST":

        # requests filminformation for a specific TMDB film with tmdb_id (addtohistory is explained in helpers.py)
        tmdb_response = rfi_TMDb(request.form.get("tmdb_id"))
        addtohistory(request.form.get("tmdb_id"), tmdb_response)
        omdb_response = rfi_OMDb(tmdb_response)

        # requests favorieten and check-ins and checks if they already exist in the tables
        favorieten = favorietenn()
        alfavo = any([favoriet['film_id'] == request.form.get("tmdb_id") for favoriet in favorieten])
        checkins = checkinss()
        alcheckin = any([checkin['film_id'] == request.form.get("tmdb_id") for checkin in checkins])

        # render the filminformation page with parameters mentioned below (for the buttons and notifications)
        return render_template("filminformatie.html", tmdb = tmdb_response, omdb=omdb_response, alfavo=alfavo,
                                lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()),
                                vrienden=vrienden1(), vrienden1=vrienden2(), lijsten=lijsten1(), lijsten2=lijsten2(),
                                lijsten3=lijsten3(), alcheckin=alcheckin)

@app.route("/filminfo_non", methods=["GET", "POST"])
def filminformatie_non():
    ''' Render filminformation page for non-users (separated html because of the notifications in the layout) / does the same as above '''
    if request.method == "POST":
        # requests filminformation for a specific TMDB film with tmdb_id
        tmdb_response = rfi_TMDb(request.form.get("tmdb_id"))
        omdb_response = rfi_OMDb(tmdb_response)

        return render_template("filminformatie_non.html", tmdb = tmdb_response, omdb=omdb_response)

@app.route("/gezamenlijkelijstgemaakt", methods=["POST"])
@login_required
def gezamenlijkelijstgemaakt():
    ''' Returns message that a joint list has been made '''
    if request.method == "POST":

        # request information from buttons/post method
        lijstnaam = request.form.get("gez_lijstnaam")
        friend_request_FROM = request.form.get("vriendvan")
        friend_request_TO = request.form.get("vriendnaar")

        # makes list if there is not already a joint list with this friend (from in database)
        if friend_request_FROM:
            sql_gezamenlijke_lijst_gemaakt(gebruiker(), friend_request_FROM, lijstnaam)

        # # makes list if there is not already a joint list with this friend (to in database)
        if friend_request_TO:
            sql_gezamenlijke_lijst_gemaakt(gebruiker(), friend_request_TO, lijstnaam)

        # returns message that the joint list has been made
        return render_template("/message/gezamenlijkelijstgemaakt.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                lijstnaam = lijstnaam, totaal = tipslength() + lengte_vv())

@app.route("/gezlijst", methods=["POST"])
@login_required
def gezlijst():
    ''' Returns the joint list with requested friend '''
    if request.method == "POST":
        # requests friend from post method
        vriend = request.form.get("vriend")

        # checks for information of the list in both directions (user and user2 and opposite direction)
        lijsten1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 \
                               AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                               gebruiker = gebruiker(), gebruiker2 = vriend, lijstnaam = request.form.get("button"))

        lijsten2 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                                gebruiker2 = gebruiker(), gebruiker = vriend, lijstnaam = request.form.get("button"))

        # renders joint list page with parameters
        return render_template("gezlijst.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = tipslength() +lengte_vv(),
                                lijstnaam = request.form.get("button"),  vriend = vriend, lijsten1=lijsten1, lijsten2=lijsten2)

@app.route("/historie", methods=["GET", "POST"])
@login_required
def historie():
    ''' Returns historie for user or delete the userhistorie '''
    if request.method == "POST":

        # if there are films in the historie, delete all films (from helpers.py)
        if len(geschiedenis()) > 0:
            db.execute("DELETE FROM historie WHERE gebruiker=:gebruiker", gebruiker = gebruiker())

            return render_template("/message/legehistorie.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal= (lengte_vv()+ tipslength()))

        else:
            # if there are no films in the historie
            return apology("Je hebt geen kijkgeschiedenis")

    return render_template("historie.html", historie=geschiedenis(), lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal= (lengte_vv()+ tipslength()))

@app.route("/index")
@login_required
def index():
    ''' Returns index page with popular and new films (parameters for notifications) '''
    return render_template("index.html", popular=popular_films()["results"], new=new_films()["results"], lengte = lengte_vv(),
    tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/layout")
@login_required
def layout():
    ''' Made for notifications (show them in the navbar) '''
    return render_template("layout.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/legehistorie", methods=["GET", "POST"])
@login_required
def legehistorie():
    ''' Returns message that historie has been deleted '''
    return render_template("/message/legehistorie.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()))

@app.route("/lijst", methods=["POST"])
@login_required
def lijst():
    ''' Returns list which has been clicked with the films inside the film '''
    if request.method == "POST":
        # request listinformation from table where user is user
        lijstinfo = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND nieuwe_lijst IS NULL",
                                gebruiker = gebruiker(), lijstnaam = request.form.get("button"))

        return render_template("lijst.html", lengte = lengte_vv(), tipslengte = tipslength(), lijst=request.form.get("button"),
                                lijstinfo=lijstinfo, totaal = tipslength() + lengte_vv())

@app.route("/lijstgemaakt", methods=["POST"])
@login_required
def lijstgemaakt():
    ''' Returns message that list has been made '''
    if request.method == "POST":

        # check if list already exists with same listname for this user
        check = db.execute("SELECT * FROM lijsten WHERE lijstnaam=:lijstnaam AND gebruiker=:gebruiker AND gebruiker2 IS NULL",
                            lijstnaam = request.form.get("lijstnaam"), gebruiker = gebruiker())

        # if the list exists, return error
        if check:
            tekst = "Je hebt al een lijst die " + request.form.get("lijstnaam") + " heet"
            return apology(tekst)

        else:
            # else, make a list with this listname and for this user
            db.execute("INSERT INTO lijsten (gebruiker, lijstnaam, nieuwe_lijst) VALUES (:gebruiker, :lijstnaam, :nieuwe_lijst)",
                    gebruiker = gebruiker(), lijstnaam = request.form.get("lijstnaam"), nieuwe_lijst="ja")

        return render_template("/message/lijstgemaakt.html", lengte = lengte_vv(), tipslengte =tipslength(),
                                lijstnaam = request.form.get("lijstnaam"), totaal=(lengte_vv() + tipslength()))

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in. """
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # checks inputbars from loginform (from helpers.py)
        loginform()

        # request table information if username exists
        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruiker-inloggen"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("wachtwoord-inloggen"), rows[0]["wachtwoord"]):
            return apologynon("Ongeldige gebruikersnaam en/of wachtwoord")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("inloggen.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/mijnlijsten", methods=["GET", "POST"])
@login_required
def mijnlijsten():
    """Return my lists with parameters of lists (check helpers.py for parameters)"""
    # see helpers.py for parameters
    return render_template("mijnlijsten.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                            vrienden=vrienden1(), vrienden1=vrienden2(), lijsten=lijsten1(), lijsten2=lijsten2(), lijsten3=lijsten3())

@app.route("/mijnprofiel")
@login_required
def mijnprofiel():
    """Edit own profile (check helpers.py for parameters)"""
    return render_template("mijnprofiel.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()),
    vrienden=vrienden1(), vrienden1=vrienden2(), favorieten=favorietenn(), historie=geschiedenis(),
    lijsten=lijsten1(), lijsten2=lijsten2(), lijsten3=lijsten3(), aanbevelingen=aanbevelingenn(), checkins=checkinss(),
    aanbevelingenvan=aanbevelingenvann())

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "POST":

        # checks if forms are filled in
        registerform()

        # hash the password
        wachtwoord = pwd_context.hash(request.form.get("wachtwoord"))

        # insert the user into the database
        result = db.execute("INSERT INTO gebruikers (gebruikersnaam, wachtwoord, email, veiligheidsvraag) VALUES \
                            (:gebruikersnaam, :wachtwoord, :email, :veiligheidsvraag)",
                            gebruikersnaam=request.form.get("gebruikersnaam"), wachtwoord=wachtwoord,
                            veiligheidsvraag=request.form.get("veiligheidsvraag"), email="niet meer nodig")

        if not result:
            return apologynon("username already exists")

        # query database for username
        rows = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                          gebruikersnaam=request.form.get("gebruikersnaam"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registreren.html")

@app.route("/removecheckins", methods=["POST"])
@login_required
def removecheckins():
    """Returns message that film has been deleted from checkins"""
    if request.method == "POST":

        # requests filminformation for a specific TMDB film with tmdb_id
        tmdb_response = rfi_TMDb(request.form.get("geencheckin"))
        omdb_response = rfi_OMDb(tmdb_response)

        # delete film from check-ins
        db.execute("DELETE FROM checkins WHERE gebruiker=:gebruiker AND film_id=:film_id",
                    gebruiker = gebruiker(), film_id = request.form.get("geencheckin"))

        return render_template("/message/removecheckins.html", tmdb = tmdb_response, omdb = rfi_OMDb(tmdb_response), lengte = lengte_vv(),
                                tipslengte = tipslength(), totaal = tipslength() +lengte_vv())

@app.route("/removefavorite", methods=["POST"])
@login_required
def removefavorite():
    """Returns message that film has been deleted from favorites"""
    if request.method == "POST":

        # requests filminformation for a specific TMDB film with tmdb_id
        tmdb_response = rfi_TMDb(tmdb_id = request.form.get("geenfavo"))
        omdb_response = rfi_OMDb(tmdb_response)

        # delete film from favorites
        db.execute("DELETE FROM favorieten WHERE gebruiker=:gebruiker AND film_id=:film_id",
                    gebruiker = gebruiker(), film_id = request.form.get("geenfavo"))

        return render_template("/message/removefavorite.html", tmdb = tmdb_response, omdb=omdb_response, lengte = lengte_vv(),
                                tipslengte = tipslength(), totaal= (lengte_vv()+ tipslength()))

@app.route("/removelist", methods=["POST"])
@login_required
def removelist():
    """Returns message that list has been deleted from lists"""
    if request.method == "POST":
        #request friendname
        vriend = request.form.get("vriend")

        # if there is no friend, delete individual list with parameters below
        if not vriend:
            db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gez_lijst IS NULL",
                        gebruiker = gebruiker(), lijstnaam = request.form.get("lijstnaam"))

            return render_template("/message/removelist.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal = tipslength()+lengte_vv(), lijstnaam = request.form.get("lijstnaam"))

        # if there is a friend, check and delete joint list with parameters below (both directions)
        else:
            check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gebruiker2=:gebruiker2",
                                gebruiker = gebruiker(), lijstnaam = request.form.get("lijstnaam"), gebruiker2=vriend)

            if check1:
                db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                            gebruiker = gebruiker(), gebruiker2=vriend, lijstnaam = request.form.get("lijstnaam"))

                return render_template("/message/removelist.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                        totaal = tipslength()+lengte_vv(), lijstnaam=request.form.get("lijstnaam"), vriend=vriend)

            # check and delete joint list with parameters below (both directions)
            if not check1:
                check1 = db.execute("SELECT * FROM lijsten WHERE gebruiker=:gebruiker AND lijstnaam=:lijstnaam AND gebruiker2=:gebruiker2",
                                    gebruiker2 = gebruiker(), lijstnaam=request.form.get("lijstnaam"), gebruiker=vriend)

                db.execute("DELETE FROM lijsten WHERE gebruiker=:gebruiker AND gebruiker2=:gebruiker2 AND lijstnaam=:lijstnaam",
                            gebruiker2=gebruiker(), gebruiker=vriend, lijstnaam = request.form.get("lijstnaam"))

                return render_template("/message/removelist.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                        totaal = tipslength()+lengte_vv(), lijstnaam = request.form.get("lijstnaam"), vriend=vriend)

@app.route("/tips", methods=["GET", "POST"])
@login_required
def tips():
    """Renders tips page (tips from other users for the logged in user) /parameters from helpers.py"""
    return render_template("tips.html", lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                            aanbevelingen=aanbevelingenn(), vrienden=vrienden1(), vrienden1=vrienden2())

@app.route("/tipvriend", methods=["POST"])
@login_required
def tipvriend():
    """Tip a friend with the selected film"""
    if request.method == "POST":

        tmdb_id = ophalen("buttonvriend")

        # request friends (both directions)
        check = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruiker(), naar=ophalen("tipvriend"), geaccepteerd="ja")
        check2 = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar = gebruiker(), van=ophalen("tipvriend"), geaccepteerd="ja")

        # if there are friends
        if check or check2:
            # check if the film has already been tipped, if so, return error
            tipcheck = db.execute("SELECT * FROM aanbevelingen WHERE van=:van AND naar=:naar AND film_id=:film_id",
                                   van=gebruiker(), naar=ophalen("tipvriend"), film_id = ophalen("buttonvriend"))

            if tipcheck:
                return apology("Je hebt deze gebruiker deze film al aanbevolen")

            # else, tip the friend and insert it into the database (parameters from helpers.py)
            tips = db.execute("INSERT INTO aanbevelingen (van, naar, film_id, titel, afbeelding) VALUES \
                             (:van, :naar, :film_id, :titel, :afbeelding)", van=gebruiker(), naar=ophalen("tipvriend"),
                             film_id = ophalen("buttonvriend"), titel = rfi_TMDb(tmdb_id)["original_title"],
                             afbeelding = rfi_TMDb(tmdb_id)["poster_path"])

            return render_template("index.html", popular=(popular_films())["results"], new=(new_films())["results"],
                                    tmdb = rfi_TMDb(tmdb_id), omdb=rfi_OMDb(rfi_TMDb(tmdb_id)), favorieten=favorieten,
                                    lengte = lengte_vv(), tipslengte =tipslength(), totaal=(lengte_vv()+ tipslength()),
                                    aanbevelingen=aanbevelingenn())

        else:
            return apology("Deze gebruiker is geen vriend van je")

@app.route("/toegevoegd", methods=["GET", "POST"])
@login_required
def toegevoegd():
    """Returns message that the friend has been added"""
    return render_template("/message/toegevoegd.html", lengte = lengte_vv(), tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/verzoeken", methods=["GET", "POST"])
@login_required
def verzoeken():
    """Render page with friend requests"""
    if request.method == "POST":
        gebruikersnaam = gebruiker()
        accepteren = request.form.get("accepteren")
        weigerenn = request.form.get("weigeren")

        # if the user wants to reject the friend request
        if not accepteren:
            # request friendname
            weigeren = weigerenn[1:]
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")

            # delete and insert that the friend request has been rejected
            db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar", naar = gebruikersnaam, van=weigeren)
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, uitgenodigd, afgewezen, datum) VALUES (:van, :naar, :geaccepteerd, :uitgenodigd, :afgewezen, :datum)",
                        van=weigeren, naar = gebruikersnaam, geaccepteerd="nee", uitgenodigd="ja", afgewezen="ja", datum=date)

            return render_template("/message/geweigerd.html", verzoeken=verzoek(), lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal = (lengte_vv()+ tipslength()), weigeren=weigeren)

        # if the user wants to accept the friend request
        elif accepteren:
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")

            # delete and insert that the friend request has been accepted
            db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar", naar = gebruikersnaam, van=accepteren)
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, datum) VALUES (:van, :naar, :geaccepteerd, :datum)",
                        van=accepteren, naar = gebruikersnaam, geaccepteerd="ja", datum=date)

            return render_template("/message/geaccepteerd.html", verzoeken=verzoek(), lengte = lengte_vv(), tipslengte = tipslength(),
                                    totaal = (lengte_vv()+ tipslength()), accepteren=accepteren)

    return render_template("verzoeken.html", verzoeken=verzoek(), lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal = (lengte_vv()+ tipslength()))

@app.route("/vriend", methods=["GET", "POST"])
@login_required
def vriend():
    """Render page to add friends or a message that the friend has been added"""
    if request.method == "POST":

        # check if friend exists in database
        vriend = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = :gebruikersnaam",
                            gebruikersnaam=ophalen("vriend"))
        if not vriend:
            return apology("Deze gebruikersnaam bestaat niet.")

        # check if you want to add yourself, if so, return error
        if ophalen("vriend") == gebruiker():
            return apology("Je kan jezelf niet toevoegen")

        # check if you are already friends with the requested friend (from the post method) in both ways
        alvrienden = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                van=ophalen("vriend"), naar=gebruiker(), geaccepteerd="ja")
        alvriendenn = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                naar=ophalen("vriend"), van=gebruiker(), geaccepteerd="ja")

        # if already friends, return error that you are already friends
        tekstt = "Je bent al vrienden met " + ophalen("vriend")
        if alvrienden or alvriendenn:
            return apology(tekstt)

        # check if you have already send a friend request to the requested friend and it's not accepted/rejected yet
        aluitgenodigdvriend = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd \
                                          AND geaccepteerd=:geaccepteerd AND afgewezen=:afgewezen",
                                          van=ophalen("vriend"), naar = gebruiker(), uitgenodigd="ja",
                                          geaccepteerd="nee", afgewezen="nee")
        aluitgenodigdjij = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND uitgenodigd=:uitgenodigd \
                                       AND geaccepteerd=:geaccepteerd AND afgewezen=:afgewezen",
                                       van=gebruiker(), naar=ophalen("vriend"), uitgenodigd="ja",
                                       geaccepteerd="nee", afgewezen="nee")

        # if you have already send a friend request to the requested friend and it's not accepted/rejected yet, return error
        if aluitgenodigdvriend or aluitgenodigdjij:
            return apology("Deze gebruiker heeft je al uitgenodigd of andersom")

        else:
            # if not, send a friend requrest to the user
            now = datetime.datetime.now()
            date = now.strftime("%d-%m-%Y")
            db.execute("INSERT INTO verzoeken (van, naar, geaccepteerd, uitgenodigd, afgewezen, datum) VALUES \
                        (:van, :naar, :geaccepteerd, :uitgenodigd, :afgewezen, :datum)",
                        van=gebruiker(), naar=ophalen("vriend"), geaccepteerd="nee",
                        uitgenodigd="ja", afgewezen="nee", datum=date)

            return render_template("/message/toegevoegd.html", toetevoegenvriend = ophalen("vriend"), lengte = lengte_vv(),
                                    tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

    return render_template("vriendtoevoegen.html", lengte = lengte_vv(), tipslengte = tipslength(),
                            totaal = (lengte_vv()+ tipslength()))

@app.route("/vriendenlijst")
@login_required
def vriendenlijst():
    """Render page with friends"""
    return render_template("vriendenlijst.html", vrienden=vrienden1(), vrienden1=vrienden2(), lengte = lengte_vv(),
                            tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/vriendinfo", methods=["POST"])
@login_required
def vriendinfo():
    """Render page with friendinformation"""
    if request.method == "POST":
        # profile friend (requested from post method) / helpers.py
        profiel = profielvriend()
        return render_template("vriendinfo.html", favorieten=favorietenvriend(), lengte = lengte_vv(), tipslengte =tipslength(),
                                totaal=(lengte_vv()+ tipslength()), profiel=profiel, checkins=checkinsvriend(),
                                historie=geschiedenisvriend(), vrienden=vriendenvriend1(), vrienden1=vriendenvriend2(),
                                aanbevelingen=aanbevelingenvriend(), aanbevelingenvan=aanbevelingenvanvriend())

@app.route("/verwijdervriend", methods=["POST"])
@login_required
def verwijdervriend():
    """Return a message that the friend has been deleted"""
    if request.method == "POST":

        # check if button is submitted
        if request.form.get("verwijder1"):
            # check friend in bot directions
            vriendcheck = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      naar = gebruiker(), van=request.form.get("verwijder1"), geaccepteerd="ja")

            vriendcheckk = db.execute("SELECT * FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                                      van=gebruiker(), naar=request.form.get("verwijder1"), geaccepteerd="ja")

            # delete friend in one of the two directions
            if vriendcheck:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            naar = gebruiker(), van=request.form.get("verwijder1"), geaccepteerd="ja")
            elif vriendcheckk:
                db.execute("DELETE FROM verzoeken WHERE van=:van AND naar=:naar AND geaccepteerd=:geaccepteerd",
                            van=gebruiker(), naar=request.form.get("verwijder1"), geaccepteerd="ja")

        return render_template("/message/verwijderdvriend.html", lengte = lengte_vv(), tipslengte =tipslength(),
                                totaal=(lengte_vv() + tipslength()))

@app.route("/verwijdervriendredirect", methods=["POST"])
@login_required
def verwijdervriendredirect():
    """Returns a message if you want to delete this friend"""
    if request.method == "POST":

        # check which button has been submitted
        vriend = request.form.get("verwijder")
        if not vriend:
            vriend = request.form.get("verwijder1")

    return render_template("/message/verwijdervriendredirect.html", vriend=vriend, lengte = lengte_vv(), tipslengte =tipslength(),
                            totaal=(lengte_vv()+ tipslength()))

@app.route("/wachtwoord")
def wachtwoord():
    """Return a page to change your password (not logged in)"""
    return render_template("wachtwoord.html")

@app.route("/wachtwoordgebruikers", methods=["GET", "POST"])
@login_required
def wachtwoordgebruikers():
    """Change password logged in"""

    if request.method == 'POST':

        # check if passwordforms are filled in
        passwordformgeb()

        # get id from database
        account = db.execute("SELECT * FROM gebruikers WHERE id = :id", id=session['user_id'])

        # check if the password equals the password in the database
        if len(account) != 1 or not pwd_context.verify(request.form.get('wachtwoord'), account[0]['wachtwoord']):
            return apology("Het wachtwoord klopt niet!")


        # check if password equals password confirmation
        if request.form.get("nieuw_wachtwoord") != request.form.get("wachtwoord_herhaling"):
            return apology("De wachtwoorden komen niet overeen")

        # check if the password is equal to your current password
        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        # if so, return error
        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apology("Niet mogelijk om je huidige wachtwoord te kiezen")

        # hash the password
        new_hash = pwd_context.hash(request.form.get("nieuw_wachtwoord"))

        # update the user
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE id=:id",
                                id=session["user_id"], wachtwoord=new_hash)

        return render_template("/message/wachtwoordveranderdgeb.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                totaal= (lengte_vv()+ tipslength()))

    else:
        return render_template("wachtwoordgebruikers.html", lengte = lengte_vv(), tipslengte = tipslength(),
                                totaal= (lengte_vv()+ tipslength()))

@app.route("/wachtwoordveranderen", methods=["GET", "POST"])
def wachtwoordveranderen():
    """Change password not logged in"""

    if request.method == 'POST':

        # get id from database
        account = db.execute("SELECT * FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                              gebruikersnaam=request.form.get('gebruikersnaam'))

        # check if inputbars are filled in
        passwordformnon()

        # check if security question has been filled in right
        if len(account) != 1 or request.form.get('veiligheidsvraag') != account[0]['veiligheidsvraag']:
            return apologynon("Het antwoord op de veiligheidsvraag klopt niet!")

        # check if new password is equal to old password
        wachtwoordcheck = db.execute("SELECT wachtwoord FROM gebruikers WHERE gebruikersnaam=:gebruikersnaam",
                                      gebruikersnaam=account[0]["gebruikersnaam"])

        # if so, return error
        if pwd_context.verify(request.form.get("nieuw_wachtwoord"), wachtwoordcheck[0]["wachtwoord"]):
            return apologynon("Niet mogelijk om je huidige wachtwoord te kiezen")

        # hash the password
        new_hash = pwd_context.hash(request.form.get("nieuw_wachtwoord"))

        # update the user
        resultaat = db.execute("UPDATE gebruikers SET wachtwoord=:wachtwoord WHERE gebruikersnaam=:gebruikersnaam",
                                gebruikersnaam=request.form.get('gebruikersnaam'), wachtwoord=new_hash)

        return render_template("/message/wachtwoordveranderd.html")

@app.route("/wachtwoordvergeten", methods=["GET", "POST"])
def wachtwoordvergeten():
    """Forget password"""
    if request.method == "POST":
        return render_template("wachtwoordveranderen.html")

@app.route("/zoeken", methods=["GET", "POST"])
@login_required
def zoekresultaat():
    """Renders search results (logged in)"""
    if request.method == "POST":
        # request submit information
        searchterm = request.form.get("zoekterm")

        # if there is no searchterm, return error. If there are no results, return results.
        if not searchterm:
            return apology("Geen zoekterm")
        elif results_per_page(searchterm, pagenr=1) == False:
            return apology("Geen resultaten")

        # else, return the results
        else:
            return render_template("zoekresultaten.html", zoekresultaten=total_results(searchterm), lengte = lengte_vv(),
                                    tipslengte = tipslength(), totaal = (lengte_vv()+ tipslength()))

@app.route("/zoekennon", methods=["GET", "POST"])
def zoekresultaat_non():
    """Renders search results (not logged in)"""
    if request.method == "POST":
        # request submit information
        searchterm = request.form.get("zoekterm")

        # if there is no searchterm, return error. If there are no results, return results.
        if not searchterm:
            return apology("Geen zoekterm")
        elif results_per_page(searchterm, pagenr=1) == False:
            return apology("Geen resultaten")

        # else, return the results
        else:
            return render_template("zoekresultaten.html", zoekresultaten=total_results(searchterm))
