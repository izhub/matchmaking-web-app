import os
import datetime
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
from dotenv import load_dotenv

# Configure application
load_dotenv()
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///matrimonial.db")

# Make sure API key is set 
api_key = os.getenv("API_KEY")
if not api_key:
    raise RuntimeError("API_KEY not set")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userID"]

        # Query database for profile
        profile = db.execute(
            "SELECT * FROM profile WHERE userID = ?", rows[0]["userID"]
        )

        # Query database for preference
        preference = db.execute(
            "SELECT * FROM preference WHERE userID = ?", rows[0]["userID"]
        )

        # Query database for contact
        contact = db.execute(
            "SELECT * FROM contact WHERE userID = ?", rows[0]["userID"]
        )

        # Check if profile has been completed
        if len(profile) != 1:
            return redirect("profile")

        # Check if preference has been completed
        elif len(preference) != 1:
            return redirect("preference")

        # Check if contact has been completed
        elif len(contact) != 1:
            return redirect("contact")

        # Redirect user to home page
        else:

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def passwordCheck(password):

    punctuation = False
    number = False
    length = False
    characters = False

    for x in password:
        if x == "!" or x == "?" or x == ".":
            punctuation = True
        if x.isnumeric() == True:
            number = True
        if isinstance(x, str) == True and x != "!" and x != "?" and x != ".":
            characters = True
        if len(password) >= 8:
            length = True

    if (
        length == False
        or number == False
        or punctuation == False
        or characters == False
    ):
        return False


def calcAge(date):

    bday = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    today = datetime.date.today()
    age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
    return age


def calcProfileAge(date):

    registered = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").date()
    today = datetime.date.today()
    age = (
        today.year
        - registered.year
        - ((today.month, today.day) < (registered.month, registered.day))
    )
    return round(age * 12)


@app.route("/terms")
def terms():

    return render_template("termsConditions.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        gender = request.form.get("gender")
        country = request.form.get("country")
        registration = request.form.get("registration")
        source = request.form.get("source")
        dob = request.form.get("dob")
        securityQ = request.form.get("question")
        securityA = request.form.get("answer")

        if not name or not password or not confirmation or not email:
            return apology("fields cannot be blank", 400)

        username = db.execute("SELECT username FROM users WHERE username = ?", name)
        if len(username) == 1:
            return apology("username already exists", 400)

        mail = db.execute(
            "SELECT email FROM users WHERE email = ?", request.form.get("email")
        )
        if len(mail) > 0:
            return apology("Email is already used.")

        if password and confirmation:
            if password != confirmation:
                return apology("password did not match", 400)

        if passwordCheck(password) == False:
            return apology(
                "Password must include punctuation, characters, numbers, and be at leats 8 characters long"
            )

        if calcAge(dob) < 18:
            return apology("The minimum age to register is 18!")

        # Add user to db
        db.execute(
            """INSERT INTO users(username,email,hash,dob,gender,country,reason,source, securityQuestion, securityAnswer)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
            name,
            email,
            generate_password_hash(password),
            dob,
            gender,
            country,
            registration,
            source,
            securityQ,
            securityA,
        )

        # login the user after register
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        session["user_id"] = rows[0]["userID"]

        return redirect("profile")

    else:
        return render_template("register.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        aboutMe = request.form.get("aboutMe")
        lookingFor = request.form.get("lookingFor")
        citizenship = request.form.get("citizenship")
        origin = request.form.get("country")
        relocation = request.form.get("relocation")
        income = request.form.get("income")
        timeFrame = request.form.get("timeframe")
        marriageStatus = request.form.get("marriageStatus")
        haveChildren = request.form.get("haveChildren")
        wantChildren = request.form.get("wantChildren")
        livingArrangements = request.form.get("livingArrangements")
        height = request.form.get("height")
        build = request.form.get("build")
        smoke = request.form.get("smoke")
        disability = request.form.get("disability")
        education = request.form.get("education")
        profession = request.form.get("profession")
        jobTitle = request.form.get("jobTitle")

        if not jobTitle or not aboutMe or not lookingFor:
            return apology("Fields cannot be blank", 400)

        # Query database for profile & preference
        profile = db.execute(
            "SELECT * FROM profile WHERE userID = ?", session["user_id"]
        )
        preference = db.execute(
            "SELECT * FROM preference WHERE userID = ?", session["user_id"]
        )

        if len(profile) != 1:
            db.execute(
                """INSERT INTO profile(userID,aboutMe,lookingFor,citizenship,origin,relocation,income,
                        timeframe,marriageStatus,haveChildren,wantChildren,livingArrangements,height,build,smoke,
                        disabilities,education,profession,jobTitle) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                session["user_id"],
                aboutMe,
                lookingFor,
                citizenship,
                origin,
                relocation,
                income,
                timeFrame,
                marriageStatus,
                haveChildren,
                wantChildren,
                livingArrangements,
                height,
                build,
                smoke,
                disability,
                education,
                profession,
                jobTitle,
            )
        else:

            if aboutMe != profile[0]["aboutMe"]:
                db.execute(
                    "UPDATE profile SET aboutMe = ? WHERE userID = ?",
                    aboutMe,
                    session["user_id"],
                )

            if lookingFor != profile[0]["lookingFor"]:
                db.execute(
                    "UPDATE profile SET lookingFor = ? WHERE userID = ?",
                    lookingFor,
                    session["user_id"],
                )

            if citizenship != profile[0]["citizenship"]:
                db.execute(
                    "UPDATE profile SET citizenship = ? WHERE userID = ?",
                    citizenship,
                    session["user_id"],
                )

            if origin != profile[0]["origin"] and origin != "":
                db.execute(
                    "UPDATE profile SET origin = ? WHERE userID = ?",
                    origin,
                    session["user_id"],
                )

            if relocation != profile[0]["relocation"]:
                db.execute(
                    "UPDATE profile SET relocation = ? WHERE userID = ?",
                    relocation,
                    session["user_id"],
                )

            if income != profile[0]["income"]:
                db.execute(
                    "UPDATE profile SET income = ? WHERE userID = ?",
                    income,
                    session["user_id"],
                )

            if timeFrame != profile[0]["timeframe"]:
                db.execute(
                    "UPDATE profile SET timeframe = ? WHERE userID = ?",
                    timeFrame,
                    session["user_id"],
                )

            if marriageStatus != profile[0]["marriageStatus"]:
                db.execute(
                    "UPDATE profile SET marriageStatus = ? WHERE userID = ?",
                    marriageStatus,
                    session["user_id"],
                )

            if haveChildren != profile[0]["haveChildren"]:
                db.execute(
                    "UPDATE profile SET haveChildren = ? WHERE userID = ?",
                    haveChildren,
                    session["user_id"],
                )

            if wantChildren != profile[0]["wantChildren"]:
                db.execute(
                    "UPDATE profile SET wantChildren = ? WHERE userID = ?",
                    wantChildren,
                    session["user_id"],
                )

            if livingArrangements != profile[0]["livingArrangements"]:
                db.execute(
                    "UPDATE profile SET livingArrangements = ? WHERE userID = ?",
                    livingArrangements,
                    session["user_id"],
                )

            if int(height) != profile[0]["height"]:
                db.execute(
                    "UPDATE profile SET height = ? WHERE userID = ?",
                    height,
                    session["user_id"],
                )

            if build != profile[0]["build"]:
                db.execute(
                    "UPDATE profile SET build = ? WHERE userID = ?",
                    build,
                    session["user_id"],
                )

            if smoke != profile[0]["smoke"]:
                db.execute(
                    "UPDATE profile SET smoke = ? WHERE userID = ?",
                    smoke,
                    session["user_id"],
                )

            if disability != profile[0]["disabilities"]:
                db.execute(
                    "UPDATE profile SET disabilities = ? WHERE userID = ?",
                    disability,
                    session["user_id"],
                )

            if education != profile[0]["education"]:
                db.execute(
                    "UPDATE profile SET education = ? WHERE userID = ?",
                    education,
                    session["user_id"],
                )

            if profession != profile[0]["profession"]:
                db.execute(
                    "UPDATE profile SET profession = ? WHERE userID = ?",
                    profession,
                    session["user_id"],
                )

            if jobTitle != profile[0]["jobTitle"]:
                db.execute(
                    "UPDATE profile SET jobTitle = ? WHERE userID = ?",
                    jobTitle,
                    session["user_id"],
                )

            return redirect("userPreference")

        if len(preference) != 1:
            return redirect("preference")
        else:
            return redirect("/")

    else:
        profile = db.execute(
            "SELECT * FROM profile WHERE userID = ?", session["user_id"]
        )
        if len(profile) == 1:
            return redirect("/")
        else:
            return render_template("profile.html")


@app.route("/preference", methods=["GET", "POST"])
@login_required
def preference():

    if request.method == "POST":

        ageFrom = request.form.get("ageFrom")
        ageTo = request.form.get("ageTo")
        heightFrom = request.form.get("heightFrom")
        heightTo = request.form.get("heightTo")
        country = request.form.get("country")
        education = request.form.get("education")
        marriageStatus = request.form.get("marriage")
        income = request.form.get("income")

        if not education or not marriageStatus or not income or not country:
            return apology("All fields are required", 400)

        # Query database for preference & contact
        preference = db.execute(
            "SELECT * FROM preference WHERE userID = ?", session["user_id"]
        )
        contact = db.execute(
            "SELECT * FROM contact WHERE userID = ?", session["user_id"]
        )

        # Check if preference has been completed
        if len(preference) != 1:
            db.execute(
                "INSERT INTO preference(userID,age,height,country,education,maritalStatus,income) VALUES(?,?,?,?,?,?,?)",
                session["user_id"],
                ageFrom + " - " + ageTo,
                heightFrom + " - " + heightTo,
                country,
                education,
                marriageStatus,
                income,
            )

        else:
            ageSet = preference[0]["age"].split(" - ")
            htSet = preference[0]["height"].split(" - ")

            if ageFrom != ageSet[0] or ageTo != ageSet[1]:
                db.execute(
                    "UPDATE preference SET age = ? WHERE userID = ?",
                    ageFrom + " - " + ageTo,
                    session["user_id"],
                )

            if heightFrom != htSet[0] or heightTo != htSet[1]:
                db.execute(
                    "UPDATE preference SET height = ? WHERE userID = ?",
                    heightFrom + " - " + heightTo,
                    session["user_id"],
                )

            if education != preference[0]["education"]:
                db.execute(
                    "UPDATE preference SET education = ? WHERE userID = ?",
                    education,
                    session["user_id"],
                )

            if marriageStatus != preference[0]["maritalStatus"]:
                db.execute(
                    "UPDATE preference SET maritalStatus = ? WHERE userID = ?",
                    marriageStatus,
                    session["user_id"],
                )

            if income != preference[0]["income"]:
                db.execute(
                    "UPDATE preference SET income = ? WHERE userID = ?",
                    income,
                    session["user_id"],
                )

            if country != preference[0]["country"] and country != "":
                db.execute(
                    "UPDATE preference SET country = ? WHERE userID = ?",
                    country,
                    session["user_id"],
                )

            return redirect("userPreference")

        if len(contact) != 1:
            return redirect("contact")
        else:
            return redirect("/")

    else:
        preference = db.execute(
            "SELECT * FROM preference WHERE userID = ?", session["user_id"]
        )
        if len(preference) == 1:
            return redirect("/")
        else:
            return render_template("preference.html")


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():

    # Query database for contact
    contact = db.execute("SELECT * FROM contact WHERE userID = ?", session["user_id"])

    if request.method == "POST":

        firstName = request.form.get("firstname")
        lastName = request.form.get("lastname")
        address = request.form.get("address")
        country = request.form.get("country")
        state = request.form.get("state")
        city = request.form.get("city")
        zipcode = request.form.get("zip")
        dob = request.form.get("dob")

        if not firstName or not lastName or not address or not zipcode or not dob:
            return apology("All fields are required", 400)

        if len(contact) != 1:
            db.execute(
                """INSERT INTO contact(userID,firstName,lastName,address,country,state,city,zipcode,dob)
                        VALUES(?,?,?,?,?,?,?,?,?)""",
                session["user_id"],
                firstName,
                lastName,
                address,
                country,
                state,
                city,
                zipcode,
                dob,
            )
        else:
            if firstName != contact[0]["firstName"]:
                db.execute(
                    "UPDATE contact SET firstName = ? WHERE userID = ?",
                    firstName,
                    session["user_id"],
                )

            if lastName != contact[0]["lastName"]:
                db.execute(
                    "UPDATE contact SET lastName = ? WHERE userID = ?",
                    lastName,
                    session["user_id"],
                )

            if address != contact[0]["address"]:
                db.execute(
                    "UPDATE contact SET address = ? WHERE userID = ?",
                    address,
                    session["user_id"],
                )

            if country != contact[0]["country"] and country != "":
                db.execute(
                    "UPDATE contact SET country = ? WHERE userID = ?",
                    country,
                    session["user_id"],
                )

            if state != contact[0]["state"] and state != "":
                db.execute(
                    "UPDATE contact SET state = ? WHERE userID = ?",
                    state,
                    session["user_id"],
                )

            if city != contact[0]["firstName"] and city != "":
                db.execute(
                    "UPDATE contact SET city = ? WHERE userID = ?",
                    city,
                    session["user_id"],
                )

            if zipcode != contact[0]["zipcode"]:
                db.execute(
                    "UPDATE contact SET zipcode = ? WHERE userID = ?",
                    zipcode,
                    session["user_id"],
                )

            if dob != contact[0]["dob"]:
                db.execute(
                    "UPDATE contact SET dob = ? WHERE userID = ?",
                    dob,
                    session["user_id"],
                )

            return redirect("userPreference")

        return redirect("/")

    else:
        if len(contact) == 1:
            return redirect("/")
        else:
            return render_template("contact.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show profiles"""

    if request.method == "POST":
        return redirect("/")

    else:
        me = db.execute(
            """SELECT users.gender,users.username, users.profileStatus, contact.city, contact.state, contact.country FROM users
                        JOIN contact ON contact.userID = users.userID
                        WHERE users.userID = ?""",
            session["user_id"],
        )
        users = db.execute(
            """SELECT users.userID, users.username, users.dob, users.gender, users.registered,
                            users.profilePhotos,users.profileMsg, profile.profession, contact.city, contact.state,
                            contact.country FROM users
                            JOIN profile ON profile.userID = users.userID
                            JOIN contact ON contact.userID = users.userID
                            WHERE users.profileStatus = 'active' AND users.userID NOT IN
                            (SELECT blocked FROM profileBlocks WHERE blocker = ?)""",
            session["user_id"],
        )
        for user in users:
            user["age"] = calcAge(user["dob"])
            user["profage"] = calcProfileAge(user["registered"])

        return render_template("index.html", users=users, me=me)


@app.route("/search/")
@login_required
def searchprofiles():
    """search user"""

    # get current user's gender
    current_user = db.execute(
        "SELECT gender FROM users WHERE userID = ?", session["user_id"]
    )[0]["gender"]

    # set opposite gender
    opposite_gender = "F" if current_user == "M" else "M"

    print("Current user gender:", current_user, flush=True)
    print("Opposite gender:", opposite_gender, flush=True)

    # get users of opposite gender who are active and not blocked by current user
    users = db.execute(
        """
                       SELECT users.userID, users.username, users.dob, users.gender, profile.height, profile.origin,
                            profile.citizenship,profile.income, profile.education, profile.profession, contact.state,
                            contact.country 
                       FROM users
                       JOIN profile ON profile.userID = users.userID
                       JOIN contact ON contact.userID = users.userID
                       WHERE users.userID <> ? 
                       AND users.profileStatus = 'active' 
                       AND users.gender = ?
                       AND users.userID NOT IN
                            (SELECT blocked FROM profileBlocks WHERE blocker = ?)""",
        session["user_id"],
        opposite_gender,
        session["user_id"],
    )
    for user in users:
        user["age"] = calcAge(user["dob"])

    return render_template("search.html", users=users)


@app.route("/user/<username>")
@login_required
def userProfile(username):
    """Show user"""

    user = db.execute(
        "SELECT userID,username, dob, gender, country,membership, reason, registered, profileStatus, profilePhotos, profileMsg  FROM users WHERE username = ?",
        username,
    )
    profile = db.execute(
        "SELECT * FROM profile WHERE profile.userID = ?", user[0]["userID"]
    )
    location = db.execute(
        "SELECT country, state, city FROM contact WHERE contact.userID = ?",
        user[0]["userID"],
    )
    prefs = db.execute(
        "SELECT * FROM preference WHERE preference.userID = ?", user[0]["userID"]
    )
    age = calcAge(user[0]["dob"])
    user.extend(profile)
    user.extend(location)
    user.extend(prefs)

    pLikes = db.execute(
        "SELECT * FROM profileLikes WHERE liker = ? AND liked = ?",
        session["user_id"],
        user[0]["userID"],
    )
    pblocks = db.execute(
        "SELECT * FROM profileBlocks WHERE blocker = ? AND blocked = ?",
        session["user_id"],
        user[0]["userID"],
    )
    blength = len(pblocks)
    blocked = False if len(pblocks) == 0 else True
    liked = False if len(pLikes) == 0 else True
    sessionUser = db.execute(
        "SELECT userID,membership, profileMsg FROM users WHERE userID = ?",
        session["user_id"],
    )

    return render_template(
        "user.html",
        user=user,
        age=age,
        sessionUser=sessionUser,
        liked=liked,
        blocked=blocked,
        blength=blength,
    )


@app.route("/userProfileAction/<userID>/<action>")
@login_required
def userProfileAction(userID, action):

    if action == "like":
        db.execute(
            "INSERT INTO profileLikes(liker, liked) VALUES(?,?)",
            session["user_id"],
            userID,
        )
    elif action == "unlike":
        db.execute(
            "DELETE FROM profileLikes WHERE liker = ? AND liked = ?",
            session["user_id"],
            userID,
        )

    if action == "block":
        db.execute(
            "INSERT INTO profileBlocks(blocker, blocked) VALUES(?,?)",
            session["user_id"],
            userID,
        )
    elif action == "unblock":
        db.execute(
            "DELETE FROM profileBlocks WHERE blocker = ? AND blocked = ?",
            session["user_id"],
            userID,
        )

    return redirect(request.referrer)


@app.route("/myLikes")
@login_required
def myLikes():

    iLiked = db.execute(
        """SELECT users.userID, users.username, users.dob, users.gender, contact.state, contact.country FROM users
                            JOIN profile ON profile.userID = users.userID
                            JOIN contact ON contact.userID = users.userID
                            WHERE users.userID IN (SELECT liked FROM profileLikes WHERE liker = ?)
                            AND users.profileStatus = 'active' AND users.username NOT IN
                            (SELECT blocked FROM profileBlocks WHERE blocker = ? )""",
        session["user_id"],
        session["user_id"],
    )

    uLiked = db.execute(
        """SELECT users.userID, users.username, users.dob, users.gender, contact.state, contact.country FROM users
                            JOIN profile ON profile.userID = users.userID
                            JOIN contact ON contact.userID = users.userID
                            WHERE users.userID IN (SELECT liker FROM profileLikes WHERE liked = ?)
                            AND users.profileStatus = 'active' AND users.username NOT IN
                            (SELECT blocked FROM profileBlocks WHERE blocker = ? )""",
        session["user_id"],
        session["user_id"],
    )
    for user in iLiked:
        user["age"] = calcAge(user["dob"])

    for user in uLiked:
        user["age"] = calcAge(user["dob"])

    return render_template("myLikes.html", iLiked=iLiked, uLiked=uLiked)


@app.route("/messageSend/<userID>/<membership>", methods=["GET", "POST"])
@login_required
def messageSend(userID, membership):
    if request.method == "POST":
        return apology("Coming soon...")

    else:
        if membership == "basic":
            return render_template("msgUpgrade.html")

        else:
            return apology("Coming soon...")


@app.route("/messages/", methods=["GET", "POST"])
@login_required
def messages():

    if request.method == "POST":
        return apology("Coming soon...")

    else:
        return apology("Coming soon...")


@app.route("/report/<username>", methods=["GET", "POST"])
@login_required
def report(username):
    if request.method == "POST":
        info = db.execute("SELECT * FROM users WHERE userID = ?", session["user_id"])
        name = info[0]["username"]
        explanation = request.form.get("explanation")
        r = [
            "Violence",
            "Harassment",
            "Soliciting",
            "False Information",
            "Use of inappropriate photos",
            "Other",
        ]
        selected = []
        combo = ""
        for x in r:
            print(x)
            reason = request.form.get(x)
            if reason:
                selected.append(x)

        if len(selected) == 0:
            return apology("You must select a reason for reporting")

        for y in range(len(selected)):
            if y == len(selected) - 1:
                combo += selected[y]
            else:
                combo += selected[y] + " and "

        db.execute(
            "INSERT INTO report(whoReported, whoGotReported, reasonOfReport, explanation) VALUES(?,?,?,?)",
            name,
            username,
            combo,
            explanation,
        )
        return redirect("/")

    else:
        reasons = [
            "Use of inappropriate language",
            "Use of inappropriate photos",
            "Other",
        ]
        return render_template("report.html", username=username, reasons=reasons)


@app.route("/forgotPassword", methods=["GET", "POST"])
def forgotPassword():

    if request.method == "GET":
        return render_template("forgotPasswordEmail.html")
    else:
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", request.form.get("email")
        )
        if not user:
            return apology("Email Not Found")

        return render_template("forgotPassword.html", user=user)


@app.route("/resetPassword", methods=["POST"])
def resetPassword():

    if request.method == "POST":

        userID = request.form.get("userID")
        answer = request.form.get("answer")
        password = request.form.get("password")
        confirm = request.form.get("confirmPassword")
        info = db.execute("SELECT * FROM users WHERE userID = ?", userID)

        if password != confirm:
            return apology("The passwords did not match")

        if answer != info[0]["securityAnswer"]:
            return apology("Incorrect answer to your question", 400)

        if passwordCheck(password) == False:
            return apology(
                "Password has to have and can only have punctuation, characters, numbers, and has to be at leats 8 characters long"
            )

        db.execute(
            "UPDATE users SET hash = ? WHERE userID = ?",
            generate_password_hash(password),
            userID,
        )
        return redirect("/login")


@app.route("/userPreference", methods=["GET", "POST"])
@login_required
def userPreference():
    """user preference"""

    profileStatus = request.form.get("profileStatus")
    profilePhotos = request.form.get("profilePhotos")
    profileMsg = request.form.get("profileMsg")
    prefs = db.execute(
        "SELECT profileStatus,profilePhotos,profileMsg FROM users WHERE userID = ?",
        session["user_id"],
    )

    if profileStatus and profileStatus != prefs[0]["profileStatus"]:
        db.execute(
            "UPDATE users SET profileStatus = ? WHERE userID = ?",
            profileStatus,
            session["user_id"],
        )

    if profilePhotos and profileStatus != prefs[0]["profilePhotos"]:
        db.execute(
            "UPDATE users SET profilePhotos = ? WHERE userID = ?",
            profilePhotos,
            session["user_id"],
        )

    if profileMsg and profileMsg != prefs[0]["profileMsg"]:
        db.execute(
            "UPDATE users SET profileMsg = ? WHERE userID = ?",
            profileMsg,
            session["user_id"],
        )

    return render_template("edits/viewPref.html")


@app.route("/editProfile", methods=["GET"])
@login_required
def editProfile():
    """Edit profile"""

    profile = db.execute(
        "SELECT * FROM profile WHERE profile.userID = ?", session["user_id"]
    )
    return render_template("edits/editProfile.html", profile=profile)


@app.route("/editPartnerPreference", methods=["GET"])
@login_required
def editPartnerPreference():
    """Edit preference"""

    prefs = db.execute(
        "SELECT * FROM preference WHERE preference.userID = ?", session["user_id"]
    )
    return render_template("edits/editPrefs.html", prefs=prefs)


@app.route("/editContact", methods=["GET"])
@login_required
def editContact():
    """Edit Contact"""

    contact = db.execute(
        "SELECT * FROM contact WHERE contact.userID = ?", session["user_id"]
    )
    return render_template("edits/editContact.html", contact=contact)


@app.route("/myPhotos", methods=["GET", "POST"])
@login_required
def myPhotos():
    """Edit Photos"""

    return render_template("edits/editPhotos.html")


@app.route("/photoAccess", methods=["GET", "POST"])
@login_required
def photoAccess():
    """Photo Access"""

    return render_template("edits/photoAccess.html")


@app.route("/changeUsername", methods=["GET", "POST"])
@login_required
def changeUsername():
    """Change Username"""

    if request.method == "POST":

        username = request.form.get("username")
        confirm = request.form.get("ConfirmUsername")
        password = request.form.get("password")
        user = db.execute("SELECT username FROM users WHERE username = ?", username)

        if not username or not confirm or not password:
            return apology("Fields cannot be empty.")

        if len(user) == 1:
            return apology("username already taken", 400)
        else:
            db.execute(
                "UPDATE users SET username = ? WHERE userID = ?",
                username,
                session["user_id"],
            )

        return redirect(request.referrer)
    else:
        user = db.execute(
            "SELECT username FROM users WHERE userID = ?", session["user_id"]
        )
        return render_template("edits/changeUsername.html", user=user)


@app.route("/changeEmail", methods=["GET", "POST"])
@login_required
def changeEmail():
    """Change Email"""

    if request.method == "POST":

        newEmail = request.form.get("email")
        confirm = request.form.get("confirmEmail")
        password = request.form.get("password")
        user = db.execute("SELECT email FROM users WHERE email = ?", newEmail)

        if not newEmail or not confirm or not password:
            return apology("Fields cannot be empty.")

        if len(user) == 1:
            return apology("email already exists", 400)
        else:
            db.execute(
                "UPDATE users SET email = ? WHERE userID = ?",
                newEmail,
                session["user_id"],
            )

        return redirect(request.referrer)

    else:
        users = db.execute("SELECT * FROM users WHERE userID = ?", session["user_id"])
        return render_template("edits/changeEmail.html", users=users)


@app.route("/changePassword", methods=["GET", "POST"])
@login_required
def changePassword():

    if request.method == "POST":

        old = request.form.get("currentPassword")
        new = request.form.get("newPassword")
        confirm = request.form.get("confirmPassword")

        if not old or not new or not confirm:
            return apology("All fields are required")

        if new != confirm:
            return apology("Passwords do not match")

        result = db.execute(
            "SELECT hash FROM users WHERE userID = ?", session["user_id"]
        )

        if not result:
            return apology("User not found")

        stored_hash = result[0]["hash"]

        if not check_password_hash(stored_hash, old):
            return apology("Current password is incorrect")

        if not passwordCheck(new):
            return apology(
                "Password must be at least 8 characters and contain valid characters"
            )

        db.execute(
            "UPDATE users SET hash = ? WHERE userID = ?",
            generate_password_hash(new),
            session["user_id"],
        )

        return redirect("/")

    return render_template("edits/changePassword.html")


@app.route("/membershipHistory", methods=["GET", "POST"])
@login_required
def membershipHistory():
    """Membership History"""

    return render_template("edits/membership.html")


@app.route("/blockedUsers", methods=["GET"])
@login_required
def blockedUsers():
    """Blocked Users"""

    blocked = db.execute(
        "SELECT userID, username, gender FROM users WHERE profileStatus='active' AND userID IN (SELECT blocked FROM profileBlocks WHERE blocker = ?)",
        session["user_id"],
    )
    return render_template("edits/blockedUsers.html", blocked=blocked)


@app.route("/userUnblock/<userID>/")
@login_required
def userUnblock(userID):

    db.execute(
        "DELETE FROM profileBlocks WHERE blocker = ? AND blocked = ?",
        session["user_id"],
        userID,
    )
    return redirect(request.referrer)


@app.route("/deleteProfile", methods=["GET", "POST"])
@login_required
def deleteProfile():
    """Delete Profile"""

    reasons = [
        "I found success",
        "I was just trying out the service",
        "I am going to re-register as another user",
        "I am concerened about my privacy",
        "Other",
    ]

    if request.method == "POST":

        info = db.execute("SELECT * FROM users WHERE userID = ?", session["user_id"])
        password = request.form.get("password")
        comments = request.form.get("comments")
        reasonList = request.form.getlist("reason")
        selected = ""

        if not check_password_hash(info[0]["hash"], password):
            return apology("Incorrect Password")

        if reasonList:
            for reason in reasonList:
                selected += reason + ". "

        if reasonList or comments:
            db.execute(
                "INSERT INTO profileDeletes(reason, feedback) VALUES(?,?)",
                selected,
                comments,
            )

        db.execute("DELETE FROM users WHERE userID = ?", session["user_id"])
        db.execute(
            "DELETE FROM profileLikes WHERE liker = ? OR liked = ? ",
            session["user_id"],
            session["user_id"],
        )
        db.execute(
            "DELETE FROM profileBlocks WHERE blocker = ? OR blocked = ? ",
            session["user_id"],
            session["user_id"],
        )
        return redirect("/login")
    else:
        return render_template("edits/deleteProfile.html", reasons=reasons)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
