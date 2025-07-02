var userId,
    alertDiv,
    namesDiv,
    fullNameEl,
    usernameEL,
    contactDiv,
    emailEL,
    phoneEl,
    roleNameEl,
    role,
    rolePageLink,
    companiesDiv,
    companyCardsDiv,
    vacanciesDiv,
    csrfToken;

document.addEventListener("DOMContentLoaded", async function () {
    userId = document.getElementById("user-id").innerText;
    alertDiv = document.getElementById("alert-div");
    namesDiv = document.getElementById("names");
    fullNameEl = document.getElementById("full-name");
    usernameEL = document.getElementById("username");
    contactDiv = document.getElementById("contact-details");
    emailEL = document.getElementById("email");
    phoneEl = document.getElementById("phone");
    roleNameEl = document.getElementById("role-name");
    rolePageLink = document.getElementById("role-page-link");
    vacanciesDiv = document.getElementById("vacancies-div");
    companiesDiv = document.getElementById("companies");
    companyCardsDiv = document.getElementById("company-cards");
    csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    await fetch(`/get/user/data/${userId}`, {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
            Accept: "application/json",
        },
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
            fullNameEl.innerText = data.firstName + " " + data.lastName;
            usernameEL.innerText = "@" + data.username;
            emailEL.innerHTML = `<b>Email: </b>${data.email}`;
            phoneEl.innerHTML = `<b>Phone: </b>${data.phone}`;
            roleNameEl.innerText =
                data.role.charAt(0).toUpperCase() + data.role.slice(1);
            role = data.role;
            rolePageLink.href = `/${data.role}/me/`;
            return;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });
    await fetch(`/get/profile/vacancies/${role}/${userId}/`, {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
        },
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
            if (role === "employee") {
                document.getElementById("vacancy-h").innerText =
                    "Applied vacancies";
                for (vac of data) {
                    vacanciesDiv.insertAdjacentHTML(
                        // add "Cancel application" button
                        "beforeend",
                        `<div class="card p-3 my-1">
                            <h4>${vac.title}</h4>
                            <p>${vac.location}</p>
                            <a class="badge rounded-pill text-bg-dark link-underline link-underline-opacity-0 stretched-link"
                                href="/company/${vac.companyId}">
                                ${vac.companyName}
                            </a>
                        </div>`
                    );
                }
            } else {
                document.getElementById("vacancy-h").innerText = "My vacancies";
                for (vac of data) {
                    vacanciesDiv.insertAdjacentHTML(
                        // add "Cancel application" button
                        "beforeend",
                        `<div class="card p-3 my-1">
                            <h4>${vac.companyName}</h4>
                            <p>Number of vacancies: ${vac.vacanciesNum}</p>
                            <p>Unanswered responses: ${vac.responseNum}</p>
                            <a class="link-underline link-underline-opacity-0 stretched-link"
                                href="/company/${vac.companyId}">
                                
                            </a>
                        </div>`
                    );
                    rolePageLink.style.display = "none";
                    companiesDiv.style.removeProperty("display");
                    companyCardsDiv.insertAdjacentHTML(
                        "beforeend",
                        `<div class="card p-3 m-1">
                            <h4>${vac.companyName}</h4>
                            <p>Location: ${vac.companyLocation}</p>
                            <a class="link-underline link-underline-opacity-0 stretched-link"
                                href="/company/${vac.companyId}">
                            </a>
                        </div>`
                    );
                }
            }
            return;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });
});

// TODO: optimize later
function editNames(button) {
    namesDiv.style.display = "none";
    button.insertAdjacentHTML(
        "beforebegin",
        `<form onsubmit="submitEditNames(this)">
                <label for="first_name">Fitst name</label>
                <input id="first_name" type="text" value="${fullNameEl.innerText.match(
                    /.+(?= )/
                )}" class="form-control" placeholder="First name">
                <label for="last_name">Last name</label>
                <input id="last_name" type="text" value="${
                    fullNameEl.innerText.match(/(?<= ).+/) || ""
                }" class="form-control" placeholder="Last name">
                <p class="p-2">${usernameEL.innerText}</p>
                <button type="submit" class="btn btn-warning">Submit</button>
            </form>`
    );
}

async function submitEditNames(form) {
    event.preventDefault();

    let firstName = form.children[1].value || "";
    if (!firstName.replaceAll(" ", "").length > 0) {
        firstName = fullNameEl.innerText.match(/.+(?= )/)[0];
    }
    let lastName = form.children[3].value || "";

    let body = { id: userId, first_name: firstName, last_name: lastName };
    await fetch(`/post/user/`, {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
        },
    })
        .then((response) => {
            if (response.status !== 202) {
                alertDiv.innerHTML = `<div class="alert alert-warning alert-dismissible fade show" role="alert">
                <p>Error while updating profile name</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`;
            } else {
                fullNameEl.innerText = firstName + " " + lastName;
            }
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });
    namesDiv.style.removeProperty("display");
    form.remove();
}

function editContact(button) {
    contactDiv.style.display = "none";
    button.insertAdjacentHTML(
        "beforebegin",
        `<form onsubmit="submitContact(this)">
                <label for="email-field">Email</label>
                <input id="email-field" type="text" value="${emailEL.innerText.match(
                    /(?<= ).+/
                )}" class="form-control" placeholder="your.email@example.com">
                <label for="phone">Phone</label>
                <input id="phone" type="text" value="${phoneEl.innerText.match(
                    /(?<= ).+/
                )}" class="form-control" placeholder="+123456789012">
                <button type="submit" class="btn btn-warning">Submit</button>
            </form>`
    );
}

async function submitContact(form) {
    event.preventDefault();

    let emailNew = form.children[1].value || "";
    if (!emailNew.replaceAll(" ", "").length > 0) {
        emailNew = emailEL.innerText.match(/(?<= ).+/)[0];
    }
    let phoneNew = form.children[3].value || "";
    if (!phoneNew.replaceAll(" ", "").length > 0) {
        phoneNew = phoneEl.innerText.match(/(?<= ).+/)[0];
    }

    let bodyObj = { id: userId, email: emailNew, phone: phoneNew };
    let body = JSON.stringify(bodyObj);
    await fetch(`/post/user/`, {
        method: "POST",
        body: body,
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
        },
    })
        .then((response) => {
            if (response.status !== 202) {
                alertDiv.innerHTML = `<div class="alert alert-warning alert-dismissible fade show" role="alert">
                <p>Error while updating contact data</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`;
            } else {
                emailEL.innerHTML = `<b>Email: </b>${emailNew}`;
                phoneEl.innerHTML = `<b>Phone: </b>${phoneNew}`;
            }
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });
    contactDiv.style.removeProperty("display");
    form.remove();
}
