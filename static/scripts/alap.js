function displayMsg(msg, type) {
    var div = document.getElementById(type).cloneNode(true);
    document.body.appendChild(div);
    div.innerText = msg;
    div.classList.add("visible");

    setTimeout(() => {
        div.classList.remove("visible");
        setTimeout( () => {
            div.remove();
        },500);
    },2000);
}

function dateToString(date) {
    const monthNuerals = ["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII"];
    var today = new Date();
    today.setHours(0,0,0,0);
    const daysUntil = (date-today)/1000/60/60/24;
    var dateString;
    if ( -1 <= daysUntil && daysUntil < 0)
        dateString = "Tegnap";
    else if (0 <= daysUntil && daysUntil < 1)
        dateString = "Ma";
    else if (1 <= daysUntil && daysUntil < 2)
        dateString = "Holnap";
    else
        dateString = monthNuerals[date.getMonth()] + ". " 
        + date.getDate() + ". " +
        date.toLocaleString(window.navigator.language, {weekday: 'short'}) + ".";
        
    return dateString + " " + 
        date.getHours() + ":" +
        String(date.getMinutes()).padStart(2,'0') + ".";
}

window.displayMsg = displayMsg;
window.dateToString = dateToString;

//inputok
document.addEventListener('DOMContentLoaded', () => {
    function labelClicked(event) {
        const label = event.target;
        label.parentElement.children[0].focus();
    }
    Array.from(document.getElementsByTagName("label")).forEach(label => {
        label.addEventListener("click", labelClicked);
    });

    // input üres -> label felemel
    Array.from(document.querySelectorAll(".input-container input")).forEach(input => {
        input.classList.toggle("non-empty",
            input.value !== ""
        );
        input.addEventListener("input", (ev) => {
            const inp = ev.target;
            inp.classList.toggle("non-empty",
                inp.value !== ""
            );
        });
    });
}); 
//inputok