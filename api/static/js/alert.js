const alertDiv = document.getElementById("alert-div");

/**
 * Show an alert right below the navbar
 * @param {"primary" | "secondary" | "success" | "danger" | "warning" | "info" | "light" | "dark"} alertType Style of the alert box
 * @param {String} alertText Displayed message
 */
function displayAlert(alertType, alertText) {
    alertDiv.innerHTML = `<div class="alert alert-warning alert-dismissible fade show" role="alert">
                <p>Invalid phone number. Use an international number with "+" symbol</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`;
}
