var title,
    // csrfToken,
    editBtn,
    manageBtn,
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

document.addEventListener("DOMContentLoaded", async function () {
    title = document.querySelector("h1");
    editBtn = document.getElementById("editBtn");
    manageBtn = document.getElementById("manageBtn");
    locationP = document.getElementById("location");
    owner = document.getElementById("owner");
    ownerEmail = document.getElementById("owner-email");
    ownerPhone = document.getElementById("owner-phone");
    salary = document.getElementById("salary");
    text = document.getElementById("text");
    tags = document.getElementById("tags");
    applyBtn = document.querySelector(".btn-success");
    const mediaDiv = document.getElementById("media");
    // csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let vacancy = await fetch(`/api/get/vacancy/${vacancyId}/`, {
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
            console.log(data);

            return data;
        })
        .catch((error) => {
            console.error("Fetch completely failed:", error);
        });

    let company = await fetch(`/api/get/company/${vacancy.owner}/`, {
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
        editBtn.href = `/api/vacancy/edit/${vacancyId}`;
    }
    if (manageBtn) {
        manageBtn.href = `/api/vacancy/${vacancyId}/manage/`;
    }
    locationP.innerText = vacancy.city + ", " + vacancy.country;
    owner.innerText = company.name;
    owner.href = `/api/company/${company.id}`;
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
            <a class="btn btn-info" href="/api/vacancy/search/?tag=${slugName}"> ${tag.name} </a>
            `
        );
    }
    for (let mediaInst of vacancy.media) {
        let imageUrl = await getMediaUrl(mediaInst.id);
        mediaDiv.insertAdjacentHTML(
            "beforeend",
            `<img src="${imageUrl}" class="rounded-3 p-3 border border-2 m-1" alt="error"
            style="height: 200px; width: 300px; display: flex;">`
        );
    }
});

async function applyForVac(button) {
    let applied = await fetch(
        `/api/post/vacancy/apply/${vacancyId}/${button.id}/`,
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
    console.log(applied);
}
