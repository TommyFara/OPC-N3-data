let list = [];  // Lista per memorizzare i dati ricevuti tramite WebSocket
let getUpdates = false;
const wsUri = "ws://172.16.1.16:8765";
const websocket = new WebSocket(wsUri);

function inizializzaPagina() {
    initializeWebSocket(); // Inizializza WebSocket all'avvio della pagina
}

function initializeWebSocket() {
    
    // Evento che si verifica quando la connessione WebSocket è aperta
    websocket.onopen = function(event) {
        console.log("Connessione WebSocket aperta");
        websocket.send("getData#"+"cur"); //ottiene i dati del giorno corrente
    };

    // Evento che si verifica quando viene ricevuto un messaggio dal server
    websocket.onmessage = function(event) {
        //console.log("Dati ricevuti tramite WebSocket: " + event.data);
        let command = event.data.split('#');
        if(command[0] == "fileName") {
            //il primo messaggio è il nome del file (per ogni update)
        } else {
            switch (command[0]) {
                case "noData": {
                    //nessun dato
                    let table = document.querySelector(".table-container");
                    table.innerHTML = "<div style='height: 30px;'></div><tr><td colspan='2'>Nessun dato disponibile</td>"
                    break;
                }
                case "deviceState": {
                    let corrVal = document.getElementById("corrVal");
                    let corrInt = document.getElementById("corrInt");
                    let corrMin = document.getElementById("corrMin");
                    let readTime = document.getElementById("readTime");
                    let sidebar = document.querySelector(".sidebar");

                    values = command[1].split(',');
                    corrVal.value = values[0]
                    corrInt.value = values[1]
                    corrMin.value = values[2]
                    readTime.value = values[3]
                    sidebar.classList.remove("disabled-block")
                    break;
                }
                case "completed": {
                    let btn = document.getElementById("applyParams")
                    let btn_dis = document.getElementById("applyParams_disabled")
                    let sidebar = document.querySelector(".sidebar");

                    btn.display = "block";
                    btn_dis.display = "none";
                    sidebar.classList.remove("disabled-block");

                    let notification = document.querySelector(".notification");
                    notification.classList.add("inAnim");

                    setTimeout(() => {
                        notification.classList.remove("inAnim");
                        notification.classList.add("outAnim");
                        setTimeout(() => {
                            notification.classList.remove("outAnim");
                        }, 500);
                    }, 2000);
                    break;
                }
                default: {
                    //il resto è il file
                    let x = event.data;
                    list = listFromCSV(event.data);
                    document.getElementById("lat").value = list[list.length-2].Latitudine;
                    document.getElementById("long").value = list[list.length-1].Longitudine;
                    createTable();
                }
            }

            if(!getUpdates) {
                console.log("get updates");
                websocket.send("getUpdates#");
                websocket.send("getState#");
                
                getUpdates = true;
            }
            
        }

        
    };

    // Evento che si verifica quando la connessione WebSocket è chiusa
    websocket.onclose = function(event) {
        console.log("Connessione WebSocket chiusa");
    };

    // Evento che si verifica in caso di errore
    websocket.onerror = function(event) {
        console.error("Errore WebSocket: ", event);
        let table = document.querySelector(".table-container");
        table.innerHTML = "<div style='height: 30px;'></div><tr><td colspan='2'>Si è verificato un errore!</td>"
    };
}

// Funzione per cambiare pagina
function goToDatiPage(){
    location.href = "dati.html";
}

function listFromCSV(csv) {
    console.log("inizio csv");
    let lines = csv.split("\n");
    let result = [];
    let headers = lines[0].split(";"); // Assumendo che la prima riga contenga gli header

    for (let i = 1; i < lines.length; i++) {   // scorro le righe
        if (lines[i] != "") {
            let obj = {};   // creo oggetto senza parametri
            let attributiOggetto = lines[i].split(";");

            // creo l'oggetto con i suo attributi
            for (let i = 0; i < headers.length; i++) {
                obj[headers[i]] = attributiOggetto[i];
            }

            result.push(obj);
        }
    }
    console.log("fine csv");
    return result;
}

function createTable(){
    let table = "";
    console.log("inizio table");
    if (list.length > 0){
        //let i = list.length -8;  // prendo l'indice dell'ultimo ottavo elemento

        // creo le colonne
        table += "<div class='row'>";
            for (const key in list[0]) {
                if (Object.hasOwnProperty.call(list[0], key)) {
                    table += "<div class='cell'>" + key + "</div>";
                }
            }
        table += "</div>";

        for (let i = list.length - 1; i >= list.length-8; i--) {
            const element = list[i];
            if(i == list.length - 1) {
                table += "<div class='row newElement'>";
            } else {
                table += "<div class='row'>";
            }
            
            for (const key in element) {
                table += "<div class='cell'>" + element[key] + "</div>";
            }
            table += "</div>";
        }
    }
    console.log("fine table");
    document.getElementsByClassName("table-container")[0].innerHTML = table;
}

function applyChanges() {
    let corrVal = document.getElementById("corrVal").value;
    let corrInt = document.getElementById("corrInt").value;
    let corrMin = document.getElementById("corrMin").value;
    let readTime = document.getElementById("readTime").value;
    
    if(corrVal != "" && corrInt != "" && corrMin != "" && readTime != "" && readTime > 0) {
        websocket.send("setState#"+corrVal+","+corrInt+","+corrMin+","+readTime);

        let btn = document.getElementById("applyParams")
        let btn_dis = document.getElementById("applyParams_disabled")
        let sidebar = document.querySelector(".sidebar");

        btn.display = "none";
        btn_dis.display = "block";
        sidebar.classList.add("disabled-block")
    }
}

function isFloat(n){
    return Number(n) === n && n % 1 !== 0;
}

function isInt(n){
    return Number(n) === n && n % 1 === 0;
}