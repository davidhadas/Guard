
var timeOptionsText = ["(don't set)", "1 Minuete", "2 Minuetes", "5 Minuetes", "10 Minuetes", "20 Minuetes", "30 Minuetes",
    "1 Hour", "2 Hours", "2 Hours", "6 Hours", "24 Hours", "2 Days", "4 Days", "1 Week", "1 Month"];
var timeOptions = [0, 1, 2, 5, 10, 20 , 30, 60, 2*60, 6*60, 24*60, 2*24*60, 4*24*60, 7*24*60, 31*24*60];
guardians = []

guardian = ""
document.getElementById('learning').style.display = "none";

fetch("/data/").then(response => {
        response.json().then(guardians => {
            console.log("fetch guardians", guardians)
            setOptions("guardian", guardians, guardians, guardianSelectChange)
        }).catch(error => {
            alert("HTTP-Error: " + response.status)
        })
}).catch(error => {
        alert("HTTP-Error: " + error)
});


function setOptions(selectid, options, optionsText, onchange) {
    var select = document.createElement("select");
    select.name = selectid+"Select";
    select.id = selectid+"Select";
    select.onchange = onchange

    var option = document.createElement("option");
    option.value = ""
    option.text = "";

    select.appendChild(option);

    for (var i=0; i<options.length; i++)
    {
        option = document.createElement("option");
        option.value = options[i];
        option.text = optionsText[i];
        select.appendChild(option);
    }

    var label = document.createElement("label");
    label.innerHTML = "Choose: "
    label.htmlFor = selectid+"Select";
    div = document.getElementById(selectid+"Div")
    div.innerHTML = '';
    //div.appendChild(label).appendChild(select);
    div.appendChild(select);
}


function guardianSelectChange() {
    document.getElementById('learning').style.display = "none";
    guardian = document.getElementById("guardianSelect").value;
    console.log("guardianSelectChange", guardian )
    if (guardian == "")  return

    setOptions("learnUntil", timeOptions, timeOptionsText)
    setOptions("unlearnUntil", timeOptions, timeOptionsText)
    setOptions("unblockUntil", timeOptions, timeOptionsText)
    document.getElementById('SubmitLearning').onclick  = timeSelectChange;
    document.getElementById('learning').style.display = "block";
}





function timeSelectChange() {
    console.log("timeSelectChange")
    var learnTime = document.getElementById("learnUntilSelect").value;
    var unlearnTime = document.getElementById("unlearnUntilSelect").value;
    var unblockTime = document.getElementById("unblockUntilSelect").value;
    if (guardian == "") {
        return
    }
    if (learnTime == "") learnTime = 0
    if (unlearnTime == "") unlearnTime = 0
    if (unblockTime == "") unblockTime = 0

    data = {
        "learnUntil": learnTime,
        "unlearnUntil": unlearnTime,
        "unblockUntil": unblockTime
    }

    fetch("/data/"+guardian, {
        method: 'post',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(function(response) {
        console.log('Set:', data, response);
        if (response.ok)  {
            alert("Success!")
        }
    }).catch(error => {
        alert("HTTP-Error: " + error)
    });
}
