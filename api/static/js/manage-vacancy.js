const vacancyTitle = document.getElementById("vacancyTitle"),
    vacancyLoc = document.getElementById("vacancyLoc"),
    vacancyText = document.getElementById("vacancyText"),
    vacancyTagsDiv = document.getElementById("vacancyTagsDiv"),
    respondentsCards = document.getElementById("respondentsCards"),
    csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value,
    vacancyId = JSON.parse(document.getElementById("vacancyId").textContent);

var employeeSkills;

document.addEventListener("DOMContentLoaded", async function () {
    await fetch(`/get/vacancy/${vacancyId}/`, {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
            Accept: "application/json",
        },
    })
        .then((Response) => Response.json())
        .then((data) => {
            vacancyTitle.innerText = data.title;
            vacancyLoc.innerText = data.city + ", " + data.country;
            vacancyText.innerText = data.text;

            for (tag of data.tags) {
                vacancyTagsDiv.insertAdjacentHTML(
                    "beforeend",
                    `<span class="badge rounded-pill text-bg-dark link-underline link-underline-opacity-0 me-1 mb-1 fs-5">${tag.name}</span>`
                );
            }
            for (resp of data.respondents) {
                respondentsCards.insertAdjacentHTML(
                    "beforeend",
                    `<div class="card m-1 text-bg-light" id="card${resp.id}">
                    <div class="card-header" id="employeeName">
                        <h3>${resp.name}</h3>
                    </div>
                    <div class="p-3 row card-body">
                        <div class="col col-10">
                            <p id="employeeLocation"><b>Location: </b>${resp.city}, ${resp.country}</p>
                            <p id="employeeEmail"><b>Email: </b>${resp.email}</p>
                            <p id="employeePhone"><b>Phone: </b>${resp.phone}</p>
                            <div id="employeeSkills${resp.id}">
                            </div>
                        </div>
                        <div class="col col-2 d-flex flex-fill">
                            <button role="button" class="btn btn-danger m-1 flex-fill"
                                style="text-align: center; font-size: larger;" id="${resp.id}" onclick="declineApplication(this)">
                                Decline
                            </button>
                        </div>
                    </div>
                    <div class="card-footer d-flex justify-content-center" style="position: relative;">
                        <a class="btn stretched-link" style="text-align: center;" href="/employee/${resp.id}/">Show
                            profile</a>
                    </div>
                </div>`
                );
                employeeSkills = document.getElementById(
                    `employeeSkills${resp.id}`
                );
                if (resp.hasOwnProperty("skills")) {
                    for (skill of resp.skills) {
                        employeeSkills.insertAdjacentHTML(
                            "beforeend",
                            `<span class="badge rounded-pill text-bg-dark">${skill.name}</span>`
                        );
                    }
                }
            }
        });
});

async function declineApplication(button) {
    await fetch(`/post/vacancy/${vacancyId}/decline-app/`, {
        method: "POST",
        body: JSON.stringify({ respondentId: button.id }),
        headers: {
            "X-CSRFToken": csrfToken,
            "Content-Type": "application/json",
        },
    }).then((response) => {
        if (!response.ok) {
            return response.json().then((err) => {
                throw err;
            });
        }
        if (response.status == 204) {
            let alertDiv = document.getElementById("alert");
            alertDiv.className += "alert-success";
            alertDiv.style.removeProperty("display");
            let alertMsg = document.getElementById("alertMsg");
            alertMsg.innerText = "You successefully declined the application.";

            let deletedCard = document.getElementById(`card${button.id}`);
            deletedCard.parentElement.removeChild(deletedCard);
        } else {
            let alertDiv = document.getElementById("alert");
            alertDiv.className += "alert-danger";
            alertDiv.style.removeProperty("display");
            let alertMsg = document.getElementById("alertMsg");
            alertMsg.innerText =
                "An error occurred while declining the application.";
        }
    });
}
