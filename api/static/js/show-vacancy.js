var title,
    // csrfToken,
    editBtn,
    manageBtn,
    delBtn,
    locationP,
    owner,
    ownerEmail,
    ownerPhone,
    salary,
    text,
    tags,
    ownerId,
    applyBtn;

const vacancyId = window.location.href.match(/(?<=vacancy\/)\d+/)[0];
var companyId;

document.addEventListener("DOMContentLoaded", async function () {
    title = document.querySelector("h1");
    editBtn = document.getElementById("editBtn");
    manageBtn = document.getElementById("manageBtn");
    delBtn = document.getElementById("delBtn");
    locationP = document.getElementById("location");
    owner = document.getElementById("owner");
    ownerEmail = document.getElementById("owner-email");
    ownerPhone = document.getElementById("owner-phone");
    salary = document.getElementById("salary");
    text = document.getElementById("text");
    tags = document.getElementById("tags");
    applyBtn = document.querySelector(".btn-success");
    const mediaDiv = document.getElementById("media");

    let vacancy = await fetch(`/get/vacancy/${vacancyId}/`, {
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
            return data;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });

    let company = await fetch(`/get/company/${vacancy.owner}/`, {
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
            return data;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });

    for (let resp of vacancy.respondents) {
        if (applyBtn && resp.user_id == applyBtn.id) {
            applyBtn.style.display = "none";
        }
    }

    title.innerText = vacancy.title;
    if (editBtn) {
        editBtn.href = `/vacancy/edit/${vacancyId}/`;
        manageBtn.href = `/vacancy/${vacancyId}/manage/`;
        delBtn.addEventListener("click", deleteVacancy);
        companyId = company.id;
    }
    locationP.innerText = vacancy.city + ", " + vacancy.country;
    owner.innerText = company.name;
    owner.href = `/company/${company.id}`;
    ownerEmail.innerText = company.email;
    ownerPhone.innerText = company.phone;
    salary.innerText =
        vacancy.salary + " " + vacancy.currency + " for " + vacancy.salary_type;
    text.innerText = vacancy.text;
    for (let tag of vacancy.tags || []) {
        slugName = tag.name.replace(/^\s+|\s+$/g, "");
        slugName = slugName.toLowerCase();
        tags.insertAdjacentHTML(
            "beforeend",
            `
            <a class="btn btn-info" href="/vacancy/search/?tag=${slugName}"> ${tag.name} </a>
            `
        );
    }
    for (let mediaInst of vacancy.media) {
        let imageUrl = await getMediaUrl(mediaInst.id);
        mediaDiv.insertAdjacentHTML(
            "beforeend",
            `<img src="${imageUrl}" class="rounded-3 p-3 border border-2 m-1" alt="error"
            style="height: 200px; width: 300px;">`
        );
    }
    if (mediaDiv.innerHTML.length > 0) {
        document.getElementById("mediaHeader").innerText = "Additional media:";
    }
});

async function applyForVac(button) {
    let applied = await fetch(
        `/post/vacancy/apply/${vacancyId}/${button.id}/`,
        {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json",
            },
        }
    )
        .then((response) => {
            if (!response.ok) {
                return response.json().then((err) => {
                    throw err;
                });
            }
            button.innerText = "You have applied for this vacancy!";
            button.className = "btn btn-outline-secondary flex-fill";
            button.disabled = true;
            return response.status;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });
}

async function deleteVacancy() {
    await fetch(`/delete/vacancy/${vacancyId}/`, {
        method: "DELETE",
        headers: {
            "X-CSRFToken": csrfToken,
        },
    })
        .then((response) => {
            console.log(response.status);

            if (response.status == 204) {
                window.location.assign(`/company/${companyId}/`);
            } else {
                return response.json().then((errorData) => {
                    throw errorData;
                });
            }
        })
        .catch((error) => {
            console.error(error);
            return;
        });
}
