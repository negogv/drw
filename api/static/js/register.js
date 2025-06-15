var TheUser = {
    username: "",
};
var par;
var formDiv;
var h2;
var insertedDataUl;

document.addEventListener("DOMContentLoaded", function () {
    par = document.getElementById("result");
    formDiv = document.getElementById("form_div");
    h2 = document.getElementsByTagName("h2")[0];
    insertedDataUl = document.getElementById("inserted_data_ul");
});

function submitUsername() {
    document
        .getElementById("inserted_data_div")
        .style.removeProperty("display");
    document.getElementById("is_reg_div").remove();

    let username = document.getElementById("username_field").value;
    const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;
    TheUser.csrfmiddlewaretoken = csrfToken;
    TheUser.username = username;
    formDiv.innerHTML = `<h2 class="align-center">Your first name</h2>
        <label>(necessary field)</label>
        <form onsubmit="submitFirstName()" id="firstname_form">
            <input class="form-control" style="margin-bottom: .5rem;" id="firstname_field" placeholder="First name" required>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("firstname_field").focus();
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<li class="list-group-item">Username: ${TheUser.username}</li>`
    );
}

function submitFirstName() {
    let firstname = document.getElementById("firstname_field").value;
    TheUser.first_name = firstname;
    formDiv.innerHTML = `<h2 class="align-center">Your last name</h2>
        <label>(unnecessary field)</label>
        <form onsubmit="submitLastName()" id="lastname_form">
            <input class="form-control" style="margin-bottom: .5rem;" id="lastname_field" placeholder="Last name">
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("lastname_field").focus();
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<li class="list-group-item">First name: ${TheUser.first_name}</li>`
    );
}

function submitLastName() {
    let lastname = document.getElementById("lastname_field").value || "";
    TheUser.last_name = lastname;
    formDiv.innerHTML = `<h2 class="align-center">Are you searching or offering jobs?</h2>
        <p class="align-center">(necessary info)</p>
        <div class="row">
            <button class="btn btn-secondary col" type="button" onclick="submitRole('company')">
                Offer jobs
            </button>
            <button class="btn btn-secondary col" type="button" onclick="submitRole('employee')">
                Search jobs
            </button>
        </div>`;
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<li class="list-group-item">Last name: ${TheUser.last_name}</li>`
    );
    return false;
}

function submitRole(role) {
    TheUser.role = role;
    formDiv.innerHTML = `<h2 class="align-center">Your email adress</h2>
        <label>(necessary field)</label>
        <form onsubmit="submitEmail()" id="email_form">
            <input class="form-control" style="margin-bottom: .5rem;" id="email_field" placeholder="your.email@example.com" required>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("email_field").focus();
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<li class="list-group-item">Role: ${
            TheUser.role.charAt(0).toUpperCase() + TheUser.role.slice(1)
        }</li>`
    );
}

function submitEmail() {
    let email = document.getElementById("email_field").value;
    TheUser.email = email;
    formDiv.innerHTML = `<h2 class="align-center">Your phone number</h2>
        <label>(necessary field)\nUse international format</label>
        <form onsubmit="submitPhone()" id="phone_form">
            <input class="form-control" style="margin-bottom: .5rem;" id="phone_field" placeholder="+123456789012" required>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("phone_field").focus();
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<li class="list-group-item">Email: ${TheUser.email}</li>`
    );
}

function submitPhone() {
    // TODO: specify input type="tel" and add a pattern (in RegEx format)
    if (!TheUser.phone) {
        // so when there is invalid number it's value won't safe. But I definetely should change if-requirement..
        let phone = document.getElementById("phone_field").value;
        TheUser.phone = phone;
        insertedDataUl.insertAdjacentHTML(
            "beforeend",
            `<li class="list-group-item">Phone number: ${TheUser.phone}</li>`
        );
    }
    formDiv.innerHTML = `<h2 class="align-center">Create a password</h2>
        <label>(necessary field)</label>
        <form onsubmit="return submitPassword()" id="password_form">
            <input type="password" class="form-control" style="margin-bottom: .5rem;" id="password_field" placeholder="Password" required>
            <input type="password" class="form-control" style="margin-bottom: .5rem;" id="password_repeat_field" placeholder="Repeat the password" required>
            <div id="password_error" style="color: red; display: none;">Passwords don't match!</div>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("password_field").focus();
}

function submitPassword() {
    event.preventDefault();

    var passwordField = document.getElementById("password_field");
    var repeatField = document.getElementById("password_repeat_field");

    let password = passwordField.value;
    let passwordRepeat = repeatField.value;

    if (password !== passwordRepeat) {
        passwordField.style.borderColor = "red";
        repeatField.style.borderColor = "red";
        document.getElementById("password_error").style.display = "block";
        return false;
    } else {
        TheUser.password1 = password;
        TheUser.password2 = passwordRepeat;

        let body = Object.keys(TheUser)
            .map(
                (key) =>
                    `${encodeURIComponent(key)}=${encodeURIComponent(
                        TheUser[key]
                    )}`
            )
            .join("&");

        fetch("/api/register/", {
            method: "POST",
            body: body,
            headers: {
                "X-CSRFToken": TheUser.csrfmiddlewaretoken,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            credentials: "include",
            keepalive: true,
        })
            .then((response) => {
                if (!response.ok) {
                    return response.json().then((err) => {
                        throw err;
                    });
                }
                return response.json();
            })
            .then((data) => {
                if (data.redirectTo) {
                    window.location.href = data.redirectTo;
                }
            })
            .catch((error) => {
                console.error("Fetch completely failed:", error);
            });
    }
}
