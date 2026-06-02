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

    var lezarultak = document.querySelectorAll(".lezarult");
    if ( lezarultak ) {
        lezarultak[lezarultak.length -1].scrollIntoView({ behavior: 'smooth' });
    }
});

function inputChanged(ev) {
    var parent = ev.currentTarget.parentElement;
    var input1 = parent.getElementsByTagName("input")[0];
    var input2 = parent.getElementsByTagName("input")[1];

    if (input1.value === "" && 
        input2.value === "" && 
        input1.defaultValue === "") {
        input1.required = false;
        input2.required = false;
    }
    else {
        input1.required = true;
        input2.required = true;
    }
    document.getElementById('form-gombok').classList.add('visible');
}

async function handleFormSubmit(event) {
	event.preventDefault();
    
	const form = event.currentTarget;

    var postJson = {}
    Array.from(form.children).forEach( (meccsDiv) => {
        if ( meccsDiv.classList.contains("meccs")
            && !meccsDiv.classList.contains("lezarult") &&
            meccsDiv.getElementsByTagName('input')[0].required &&
            meccsDiv.getElementsByTagName('input')[1].required ) {

            var meccs_id = meccsDiv.dataset.mid;
            var bet_H = meccsDiv.getElementsByTagName('input')[0].value;
            var bet_A = meccsDiv.getElementsByTagName('input')[1].value;
            
            if ( isNaN(parseInt(meccs_id)) || 
                isNaN(parseInt(bet_H)) || 
                isNaN(parseInt(bet_A))) {
                    displayMsg("Hibás paraméterek valamelyik meccsnél!","error");
                    return;
            }
            postJson[String(meccs_id)] = {"bet_H": bet_H, "bet_A": bet_A}
        }
    });

	try {
        const fetchData = {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify(postJson),
        };
        
        const response = await fetch(form.action, fetchData);

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(errorMessage);
        }

        const responseData = await response.json();
        var responseMsg = responseData.response;
        if (responseMsg != "")
            displayMsg(responseMsg,"error");
        else {
            displayMsg("Tippek mentve!","message");
            Array.from(form.children).forEach( (meccsDiv) => {
                if ( meccsDiv.classList.contains("meccs")
                    && !meccsDiv.classList.contains("lezarult")) {
                    inputH = meccsDiv.querySelectorAll('input')[0];
                    inputH.defaultValue = inputH.value;
                    inputA = meccsDiv.querySelectorAll('input')[1];
                    inputA.defaultValue = inputA.value;
                }
            document.getElementById("form-gombok").classList.remove("visible");
            });

        }
	} catch (error) {
		console.error(error);
	}
}