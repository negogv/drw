var skillInput = document.getElementById("skill-input"),
    skillsList = document.getElementById("skills-list"),
    selectedSkills = document.getElementById("selected-skills"),
    tagsInput =
        document.getElementById("id_tags") ||
        document.getElementById("id_skills");

var manyToManyFields = document.getElementById("manyToManyFields"); // load values from db
if (manyToManyFields) {
    data = JSON.parse(manyToManyFields.textContent);
    tagsInput.value = ""; // clear the tags input to avoid errors
    let tags = data.tags || data.skills;
    console.log(tags);

    if (tags.length !== 0) {
        selectedSkills.innerHTML = "";
        for (tag of tags) {
            selectedSkills.insertAdjacentHTML(
                "beforeend",
                `<button class="btn btn-outline-secondary rounded-pill" id="${tag.id}" onclick="delSkill(this)">${tag.name}</button>`
            );
            tagsInput.value += tag.id + "-";
        }
    }
}

skillInput.addEventListener("focus", () => {
    skillsList.parentElement.style.position = "relative";
    skillsList.style.removeProperty("display");
});

skillInput.addEventListener("blur", () => {
    setTimeout(() => {
        skillsList.parentElement.style.removeProperty("position");
        skillsList.style.display = "none";
    }, 300);
});
skillInput.addEventListener("keyup", function () {
    let els = document.querySelectorAll(".skill");
    let regex = new RegExp(skillInput.value, "i");
    Array.prototype.forEach.call(els, function (el) {
        if (regex.test(el.textContent)) el.style.display = "block";
        else el.style.display = "none";
    });
});

document
    .querySelector("form")
    .addEventListener("submit", async function (event) {
        event.preventDefault();
        tagsInput.value = await tagsInput.value.slice(0, -1);
        form = document.querySelector("form");
        form.submit();
        return true;
    });

window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        tagsInput.value = "";
        selectedSkills.innerHTML = `<span class="text-muted">Nothing is selected</span>`;
    }
});

async function loadSkillsList() {
    await fetch("/api/get/skills/all/", {
        method: "GET",
        headers: {
            "X-CSRFToken": csrfToken,
            Accept: "application/json",
        },
    })
        .then((Response) => Response.json())
        .then((data) => {
            data.forEach((skill) => {
                const option = document.createElement("li");
                option.className = "list-group-item skill";
                option.role = "button";
                option.addEventListener("click", () => addSkill(option));
                option.id = skill.id;
                option.textContent = skill.name;
                skillsList.appendChild(option);
            });
        })
        .catch((error) => console.error("Error loading skills:", error));
}

function addSkill(button) {
    let span = document.querySelector("span");
    if (selectedSkills.contains(span)) {
        selectedSkills.removeChild(span);
    }

    tagsInput.value += button.id + "-";
    selectedSkills.insertAdjacentHTML(
        "beforeend",
        `<button class="btn btn-outline-secondary rounded-pill" id="${button.id}" onclick="delSkill(this)">${button.innerText}</button>`
    );
    button.parentElement.removeChild(button);
}

function delSkill(button) {
    event.preventDefault();

    tagsInput.value.replace(button.id, "");

    const option = document.createElement("li");
    option.className = "list-group-item skill";
    option.role = "button";
    option.addEventListener("click", () => addSkill(option));
    option.id = button.id;
    option.textContent = button.innerText;
    skillsList.appendChild(option);

    selectedSkills.removeChild(button);
    if (selectedSkills.children.length == 0) {
        selectedSkills.innerHTML =
            '<span class="text-muted">Nothing is selected</span>';
    }
}

window.onload = loadSkillsList;
