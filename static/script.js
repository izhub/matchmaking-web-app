function calcAge() {

    var date = new Date(document.getElementById("bday").value);
    var today = new Date();
    var timeDiff = Math.abs(today.getTime() - date.getTime());
    var age1 = Math.ceil(timeDiff / (1000 * 3600 * 24)) / 365.2425;

    return age1;
}

function ageCheck() {
    var minAge = 18;
    var age = calcAge();
    if (age < minAge) {
        swal("Warning!", "You must be 18 years of age to Register!", "warning");
    }
}

function reminder(myMsg, userMsg ) {
    if (myMsg === "off") {
        swal("Reminder!", "You have disabled messaging. To turn it back on, visit Preferences", "info");
        event.preventDefault()
    }
    else if (userMsg === "off") {
        swal("Sorry", "This user has disabled their messaging", "error");
        event.preventDefault()
    }
}


