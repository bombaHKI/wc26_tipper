async function sendPostRequest(body) {
    try {
        const fetchData = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(body),
        };
        console.log(fetchData);
        const response = await fetch(document.URL, fetchData);

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(errorMessage);
        }

        const responseData = await response.json();
        displayMsg(responseData.response,responseData.type);
        if (responseData.error)
            console.log(responseData.error);
	} catch (error) {
		console.error(error);
	}
}

async function updateMatches() {
    sendPostRequest({action: "update-matches"});
}

function inputChanged(ev) {
    const parent = ev.currentTarget.parentElement;
    const inpArr = Array.from(parent.getElementsByTagName("input"));
    
    if (inpArr.some(inp => inp.value !== "")) {
        inpArr.forEach( inp => inp.required = true);
        document.getElementById('form-gombok').classList.add('visible');
    }
    else {
        inpArr.forEach( inp => inp.required = false);
        document.getElementById('form-gombok').classList.remove('visible');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('input').forEach( input => {
        input.addEventListener('input', inputChanged);
    });

    const exampleForm = document.getElementById("meccsek");
    exampleForm.addEventListener("submit", handleFormSubmit);
    exampleForm.addEventListener("reset", () => {
        Array.from(exampleForm.getElementsByTagName("input"))
            .forEach(input => {
                if ( input.defaultValue === "" )
                    input.required = false;
            });
        document.getElementById("form-gombok").classList.remove("visible");
    });

    Array.from(document.getElementsByTagName("time")).forEach(timeEl => {
        var date = new Date(timeEl.dateTime);
        timeEl.textContent = dateToString(date);
    });
});

async function handleFormSubmit(event) {
	event.preventDefault();
    
	const form = event.currentTarget;

    var postJson = { action: "update-odds", odds: {}};
    Array.from(form.children).forEach( (meccsDiv) => {
        const inpArr = Array.from(meccsDiv.getElementsByTagName("input"));
        if ( meccsDiv.classList.contains("meccs") &&
            inpArr.every( inp => inp.required )) {

            const meccs_id = meccsDiv.dataset.mid;
            const odds_H = inpArr[0].value;
            const odds_X = inpArr[1].value;
            const odds_A = inpArr[2].value;
            
            if ( isNaN(parseInt(meccs_id)) || isNaN(parseFloat(odds_H)) ||
                isNaN(parseFloat(odds_X)) || isNaN(parseFloat(odds_A))) {
                    displayMsg("Hibás paraméterek valamelyik meccsnél!","error");
                    return;
            }
            postJson.odds[String(meccs_id)] = {
                "odds_H": odds_H,
                "odds_X": odds_X,
                "odds_A": odds_A
            }
        }
    });
    document.getElementById('form-gombok').classList.remove('visible');
	sendPostRequest(postJson);
}