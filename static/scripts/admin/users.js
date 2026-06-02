async function sendAction(actionType, userData) {
    try {
        const url = "/admin/users";
        const fetchData = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({
                action: actionType,
                userData: userData
            }),
        };

        const response = await fetch(url, fetchData);
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const responseJson = await response.json();
        displayMsg(responseJson.response, responseJson.type);
        if (responseJson.type === "message" && userData["id"]) {
            var id = userData["id"];
            var rowElement;
            if (actionType === "delete-candidate" || actionType === "accept-candidate")
                rowElement = document.getElementById("candidate-id-" + id);
            else if (actionType === "delete-user") {
                console.log("user-id-" + responseJson["user-id"]);
                rowElement = document.getElementById("user-id-" + id);
            }
            
            if (!rowElement)
                return;
            rowElement.classList.add("remove");
            rowElement.addEventListener("transitionend", (ev) => {
                ev.target.remove();
            });
        }
    } catch (error) {
        // Display an error message if something goes wrong
        displayMsg("Valami hiba történt!", "error");
        console.error('There was a problem with the fetch operation:', error);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById("letrehoz-form").addEventListener("submit", async event => {
        event.preventDefault();
        const form = event.currentTarget;
        sendAction("addUser", Object.fromEntries(new FormData(form)));
    });
});

function action(action, id) {
    if (confirm('Biztos?'))
        sendAction(action, {id: id});
}
