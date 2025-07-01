var config = {
    cUrl: "https://api.countrystatecity.in/v1/countries",
    ckey: "NHhvOEcyWk50N2Vna3VFTE00bFp3MjFKR0ZEOUhkZlg4RTk1MlJlaA==",
};

var stateInput = document.getElementById("state-input"),
    cityInput = document.getElementById("city-input"),
    countryInput = document.getElementById("country-input"),
    countryList = undefined,
    stateList = undefined,
    cityList = undefined;

var selectedCountryCode = "";

const locEvent = new CustomEvent("locChange", {
    bubbles: true,
    composed: true,
});

[countryInput, stateInput, cityInput].forEach((element) => {
    const ul = document.createElement("ul");
    ul.className = "list-group border border-secondary border-2";
    ul.id = `${element.name}-list`;
    ul.style =
        "position: absolute; max-height: 500%; overflow-y: auto; display: none; width: 100%; z-index: 10;";
    element.parentElement.appendChild(ul);

    const listElement = element.parentElement.children[2];
    var ilName = `.${element.name}`;
    element.addEventListener("focus", () => {
        listElement.parentElement.style.position = "relative";
        listElement.style.removeProperty("display");
    });

    element.addEventListener("blur", () => {
        setTimeout(() => {
            listElement.parentElement.style.removeProperty("position");
            listElement.style.display = "none";
        }, 300);
    });
    element.addEventListener("keyup", function () {
        let els = document.querySelectorAll(ilName);
        let regex = new RegExp(element.value, "i");
        Array.prototype.forEach.call(els, function (el) {
            if (regex.test(el.textContent)) el.style.display = "block";
            else el.style.display = "none";
        });
    });
});

countryList = document.getElementById("country-list");
stateList = document.getElementById("state-list");
cityList = document.getElementById("city-list");

function loadCountryList() {
    let apiEndPoint = config.cUrl;

    fetch(apiEndPoint, { headers: { "X-CSCAPI-KEY": config.ckey } })
        .then((Response) => Response.json())
        .then((data) => {
            // console.log(data);

            data.forEach((country) => {
                const option = document.createElement("li");
                option.className = "list-group-item country";
                option.role = "button";
                option.addEventListener("click", () => selectCountry(option));
                option.id = country.iso2;
                option.textContent = country.name;
                countryList.appendChild(option);
            });
        })
        .catch((error) => console.error("Error loading countries:", error));

    if (stateInput.value.length == 0) {
        stateInput.disabled = true;
        stateInput.style.pointerEvents = "none";
    }
    if (cityInput.value.length == 0) {
        cityInput.disabled = true;
        cityInput.style.pointerEvents = "none";
    }
}

function selectCountry(element) {
    stateInput.disabled = false;
    cityInput.disabled = true;
    stateInput.style.pointerEvents = "auto";
    cityInput.style.pointerEvents = "none";

    selectedCountryCode = element.id;
    countryInput.value = element.innerText;
    countryInput.dispatchEvent(locEvent);

    stateInput.value = "";
    stateList.innerHTML = "";
    cityInput.value = "";
    cityList.innerHTML = "";

    fetch(`${config.cUrl}/${selectedCountryCode}/states`, {
        headers: { "X-CSCAPI-KEY": config.ckey },
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.length == 0) {
                stateInput.value = "No states provided";
                cityInput.value = "No cities provided";
                stateInput.readOnly = true;
                cityInput.readOnly = true;

                cityInput.disabled = false;
                cityInput.style.pointerEvents = "auto";
                return;
            }

            data.forEach((state) => {
                const option = document.createElement("li");
                option.className = "list-group-item state";
                option.role = "button";
                option.addEventListener("click", () => selectState(option));
                option.id = state.iso2;
                option.textContent = state.name;
                stateList.appendChild(option);
            });
        })
        .catch((error) => console.error("Error loading countries:", error));
}

function selectState(element) {
    cityInput.disabled = false;
    cityInput.style.pointerEvents = "auto";

    stateInput.value = element.innerText;
    const selectedStateCode = element.id;
    stateInput.dispatchEvent(locEvent);

    cityInput.value = "";
    cityList.innerHTML = "";

    fetch(
        `${config.cUrl}/${selectedCountryCode}/states/${selectedStateCode}/cities`,
        { headers: { "X-CSCAPI-KEY": config.ckey } }
    )
        .then((response) => response.json())
        .then((data) => {
            if (data.length == 0) {
                cityInput.value = stateInput.value;
                return;
            }

            data.forEach((city) => {
                const option = document.createElement("li");
                option.className = "list-group-item city";
                option.role = "button";
                option.addEventListener("click", () => selectCity(option));
                option.id = city.iso2;
                option.textContent = city.name;
                cityList.appendChild(option);
            });
        });
}

function selectCity(element) {
    cityInput.value = element.innerText;
    cityInput.dispatchEvent(locEvent);
}

// window.onload = loadCountryList;
loadCountryList();
