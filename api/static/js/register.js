var TheUser = {
    username: "",
};
var par, formDiv, h2, insertedDataUl, csrfToken;

document.addEventListener("DOMContentLoaded", function () {
    par = document.getElementById("result");
    formDiv = document.getElementById("form_div");
    h2 = document.getElementsByTagName("h2")[0];
    insertedDataUl = document.getElementById("inserted_data_ul");
    alertDiv = document.getElementById("alert-div");
    csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
});

function editSubmittedField(button) {
    let otherEditButtons = document.querySelectorAll("#edit-button");
    otherEditButtons.forEach((button) => {
        button.disabled = true;
        button.style.pointerEvents = "none";
    });
    let parentDiv = button.parentElement;
    let spanText = parentDiv.children[0].innerText;
    let match = spanText.match(/\D+(?=:)/);
    let fieldName = match[0].replace(" ", "_").toLowerCase();
    let requiredAttr = "required";
    if (fieldName === "last_name") {
        requiredAttr = "";
    }
    let fieldValue = spanText.match(/(?<=: ).+/) || "";
    parentDiv.removeChild(parentDiv.children[0]);
    let inputType = "text";

    if (fieldName === "email") {
        inputType = "email";
    } else if (fieldName === "role") {
        button.insertAdjacentHTML(
            "beforebegin",
            `<form onsubmit="applyEditing(this)" id="role">
            <select class="form-select" autofocus required>
                <option value="">Company/Employee</option>
                <option value="company">Company</option>
                <option value="employee">Employee</option>
            </select>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`
        );
    } else {
        button.insertAdjacentHTML(
            "beforebegin",
            `<form onsubmit="applyEditing(this)" id="${fieldName}">
                        <input type="${inputType}" class="form-control" value="${fieldValue}" autofocus ${requiredAttr}>
                    </form>`
        );
    }
}

function applyEditing(formElement) {
    event.preventDefault();

    let parentDiv = formElement.parentElement;

    console.log(formElement);

    let inputField = formElement.children[0];
    let inputFieldValue = inputField.value;

    if (formElement.id === "phone") {
        let cleaningRegEx = /[^\+\d]/g;
        phone = inputFieldValue.replace(cleaningRegEx, "");
        let provingRegEx = /^\+\d{9,15}$/;
        if (!provingRegEx.test(phone)) {
            alertDiv.innerHTML = `<div class="alert alert-warning alert-dismissible fade show" role="alert">
                <p>Invalid phone number. Use an international number with "+" symbol</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`;
            return;
        }
    }

    TheUser[formElement.id] = inputFieldValue;

    parentDiv.removeChild(formElement);
    parentDiv.children[0].insertAdjacentHTML(
        "beforebegin",
        `<span class="p-2">${formElement.id
            .charAt(0)
            .toUpperCase()}${formElement.id.slice(1).replace("_", " ")}: ${
            TheUser[formElement.id]
        }</span>`
    );

    let otherEditButtons = document.querySelectorAll("#edit-button");
    otherEditButtons.forEach((button) => {
        button.disabled = false;
        button.style.pointerEvents = "auto";
    });
    console.log(TheUser);
}

async function submitUsername() {
    event.preventDefault();

    TheUser.csrfmiddlewaretoken = csrfToken;

    let username = document.getElementById("username_field").value;
    let existingUsernames = [];
    await fetch("/api/get/usernames/", {
        method: "GET",
        headers: {
            "X-CSRFToken": TheUser.csrfmiddlewaretoken,
            Accept: "application/json",
        },
    })
        .then((response) => {
            if (!response.ok) {
                return response.json().then((err) => {
                    throw err;
                });
            }
            return response.json(); // This returns a promise
        })
        .then((data) => {
            existingUsernames = data.usernames;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });

    if (existingUsernames.includes(username)) {
        alertDiv.innerHTML = `<div class="alert alert-warning alert-dismissible fade show" role="alert">
            <p>Username alreade exists, please choose another one</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;
        return;
    }

    document
        .getElementById("inserted_data_div")
        .style.removeProperty("display");
    document.getElementById("is_reg_div").remove();

    TheUser.username = username; // TODO: test with regex or slugify the value
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
        `<div class="list-group-item d-flex justify-content-between" id="li-username">
                <span class="p-2">Username: ${TheUser.username}</span>
                <button class="btn btn-secondary" onclick="editSubmittedField(this)" id="edit-button">Edit</button>
            </div>`
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
        `<div class="list-group-item d-flex justify-content-between" id="li-username">
                <span class="p-2">First name: ${TheUser.first_name}</span>
                <button class="btn btn-secondary" onclick="editSubmittedField(this)" id="edit-button">Edit</button>
            </div>`
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
        `<div class="list-group-item d-flex justify-content-between" id="li-username">
                <span class="p-2">Last name: ${TheUser.last_name}</span>
                <button class="btn btn-secondary" onclick="editSubmittedField(this)" id="edit-button">Edit</button>
            </div>`
    );
    return false;
}

function submitRole(role) {
    TheUser.role = role;
    formDiv.innerHTML = `<h2 class="align-center">Your email adress</h2>
        <label>(necessary field)</label>
        <form onsubmit="submitEmail()" id="email_form">
            <input type="email" class="form-control" style="margin-bottom: .5rem;" id="email_field" placeholder="your.email@example.com" required>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("email_field").focus();
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<div class="list-group-item d-flex justify-content-between" id="li-username">
                <span class="p-2">Role: ${TheUser.role}</span>
                <button class="btn btn-secondary" onclick="editSubmittedField(this)" id="edit-button">Edit</button>
            </div>`
    );
    // insertedDataUl.insertAdjacentHTML(
    //     "beforeend",
    //     `<li class="list-group-item">Role: ${
    //         TheUser.role.charAt(0).toUpperCase() + TheUser.role.slice(1)
    //     }</li>`
    // );
}

function submitEmail() {
    let email = document.getElementById("email_field").value;
    TheUser.email = email;
    formDiv.innerHTML = `<h2 class="align-center">Your phone number</h2>
        <label>(necessary field)\nUse international format</label>
        <form onsubmit="submitPhone()" id="phone_form">
            <input type="tel" class="form-control" style="margin-bottom: .5rem;" id="phone_field" placeholder="+123456789012" required>
            <button class="btn btn-primary" type="submit">
                Save
            </button>
        </form>`;
    document.getElementById("phone_field").focus();
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<div class="list-group-item d-flex justify-content-between" id="li-username">
                <span class="p-2">Email: ${TheUser.email}</span>
                <button class="btn btn-secondary" onclick="editSubmittedField(this)" id="edit-button">Edit</button>
            </div>`
    );
}

function submitPhone() {
    // TODO: validate phone number by country code (if the code is real)
    event.preventDefault();
    let phone = document.getElementById("phone_field").value;
    let cleaningRegEx = /[^\+\d]/g;
    phone = phone.replace(cleaningRegEx, "");
    let provingRegEx = /^\+\d{9,15}$/;
    if (!provingRegEx.test(phone)) {
        alertDiv.innerHTML = `<div class="alert alert-warning alert-dismissible fade show" role="alert">
            <p>Invalid phone number. Use an international number with "+" symbol</p>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;
        return;
    }
    TheUser.phone = phone;
    insertedDataUl.insertAdjacentHTML(
        "beforeend",
        `<div class="list-group-item d-flex justify-content-between" id="li-username">
                <span class="p-2">Phone: ${TheUser.phone}</span>
                <button class="btn btn-secondary" onclick="editSubmittedField(this)" id="edit-button">Edit</button>
            </div>`
    );
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
