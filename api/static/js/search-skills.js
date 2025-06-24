var skillInput = document.getElementById("skill-input"),
    skillsList = document.getElementById("skills-list"),
    csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value,
    tagsInput =
        document.getElementById("id_tags") ||
        document.getElementById("id_skills");
selectedSkills = document.getElementById("selected-skills");

var manyToManyFields = JSON.parse(document.getElementById("manyToManyFields"));
if (manyToManyFields) {
    manyToManyFields = manyToManyFields.textContent;
}
console.log(manyToManyFields);

skillInput.addEventListener("focus", () => {
    skillsList.style.removeProperty("display");
});

skillInput.addEventListener("blur", () => {
    setTimeout(() => {
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

document.querySelector("form").onsubmit = function () {
    tagsInput.value = tagsInput.value.slice(0, -1);
    return true;
};

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
    console.log(tagsInput.value);
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
