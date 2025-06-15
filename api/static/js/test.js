// function testFunc() {
//     const request = new XMLHttpRequest();
//     try {
//         request.open("POST", "/api/test2/");

//         request.responseType = "json";

//         request.addEventListener("load", () => console.log(request.response));
//         request.addEventListener("error", () => console.error("XHR error"));

//         request.send();
//     } catch (error) {
//         console.error(`XHR error ${request.status}`);
//     }
//     console.log("Func is ended");
// }
function testFunc() {
    const csrftoken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    ).value;
    const data = { givethelink: "please" };
    const fetchPromise = fetch("/api/test2/", {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",
        },
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
            } else {
                console.log(data);
            }
        });
}
