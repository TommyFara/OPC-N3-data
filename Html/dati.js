let smallList = [];
let list = [];
let fileName = "";
let csvString = "";


function inizializzaPagina() {
    var datepicker = document.getElementById('datepicker');
    var today = new Date().toISOString().split('T')[0];
    datepicker.value = today;
    //run();
    createSocket("cur")

    document.getElementById('datepicker').addEventListener('change', function() {
        var dataSelezionata = new Date(this.value);
        var anno = dataSelezionata.getFullYear();
        var mese = ('0' + (dataSelezionata.getMonth() + 1)).slice(-2);
        var giorno = ('0' + dataSelezionata.getDate()).slice(-2);
        let data = '' + anno + mese + giorno;
        console.log(data); // Mostra la data nel formato AAAAMMDD
        
        createSocket(data);
        
        let table = document.getElementById("divTable");
        table.innerHTML = "<tr><td colspan='2'>Caricamento...</td>"

        let datepicker = document.getElementById("datepicker");
        datepicker.classList.add("disabled");

        let download = document.getElementById("download");
        download.classList.add("disabled");
    });  
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
    if (list.length > 0) {  // controllo se list non è vuota
        let table = document.getElementById("divTable");
        let t = "<table id='mainTable'>";

        // ottengo gli attributi dell'oggeto da inserire nella priga riga
        let headers = [];
        for (const key in list[0]) {
            headers.push(key);
        }

        t += "<thead><tr>";
        for (const header of headers) {
            t += "<th>" + header + "</th>"
            t += "<th class='tab-h-div'>" + "</th>" //distanza minima tra le colonne
        }
        t += "</tr></thead>";

        t += "<tbody>";
        let c = 0;  // contatore
        let changeBg = false; //alterna lo sfondo delle righe

        for (let element of list) {
            let className = (changeBg ? "table-row-changeBg" : ""); //se changeBg == true allora aggiunge la classe per cambiare lo sfondo alla riga

            if (element != null) {
                t += "<tr id='row" + c + "'>";
                
                for (const key in element) {
                    t += "<td class='" + className + "'>" + element[key] + "</td>"
                    t += "<td class='" + className + "'>" + "</td>" //distanza minima tra le colonne
                }
                t += "<tr/>";
            }
            c++;
            changeBg = !changeBg;
        }
        t += "</tbody>";
        t += "<table/>";
        table.innerHTML = t;
    }
}

function goToDemoPage(){
    location.href = "realTime.html";
}


function downloadCSV() {
    // Creare un Blob con i dati CSV
    var blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });

    // Creare un elemento <a> temporaneo per il download
    var downloadLink = document.createElement('a');
    document.body.appendChild(downloadLink);
    downloadLink.style = 'display: none';
    downloadLink.href = window.URL.createObjectURL(blob);
    downloadLink.download = fileName;

    // Simulare un click sull'elemento <a>
    downloadLink.click();

    // Rimuovere l'elemento <a> dal DOM
    document.body.removeChild(downloadLink);
}

function aggiornaTempoPassato(dataUltimoAggiornamento) {
    var elementoTesto = document.getElementById('timeElapsed'); // Assicurati che ci sia un elemento con questo id nel tuo HTML
  
    function calcolaTempo() {
        var oraAttuale = new Date();
        var differenzaInMillisecondi = oraAttuale - dataUltimoAggiornamento;
        var differenzaInMinuti = Math.floor(differenzaInMillisecondi / 60000);

        if (differenzaInMinuti < 1) {
            elementoTesto.textContent = 'Ultimo aggiornamento: meno di un minuto fa';
        } else {
            if(differenzaInMinuti == 1) {
                elementoTesto.textContent = 'Ultimo aggiornamento: 1 minuto fa';
            } else {
                elementoTesto.textContent = 'Ultimo aggiornamento: ' + differenzaInMinuti + ' minuti fa';
            }
            
        }
    }
    
    // Aggiorna il testo ogni 60 secondi (60000 millisecondi)
    setInterval(calcolaTempo, 60000);
  
    // Chiama la funzione immediatamente per impostare il testo iniziale
    calcolaTempo();
}

window.addEventListener('scroll', function() {
    var bottone = document.getElementById('tornaSuBtn');
    console.log("scroll "+document.body.scrollTop)
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        bottone.style.display = "block"; // Rende il bottone visibile
    } else {
        bottone.style.display = "none"; // Nasconde il bottone
    }
});

function tornaAllInizio() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}



/*
    WEBSOCKETS EVENTS
*/

function createSocket(data) {
    const wsUri = "ws://172.16.1.16:8765";
    const websocket = new WebSocket(wsUri);

    // Evento che si verifica quando la connessione WebSocket è aperta
    websocket.onopen = function(event) {
        console.log("Connessione WebSocket aperta");
        websocket.send("getData#"+data); //ottiene i dati del giorno corrente
    };

    // Evento che si verifica quando viene ricevuto un messaggio dal server
    websocket.onmessage = function(event) {
        console.log("Dati ricevuti tramite WebSocket: " + event.data);
        
        let command = event.data.split('#');
        if(command[0] == "fileName") {
            //il primo messaggio è il nome del file (per ogni update)
            fileName = command[1];
        } else {
            if (command[0] == "noData") {
                //nessun dato
                let table = document.getElementById("divTable");
                table.innerHTML = "<tr><td colspan='2'>Nessun dato disponibile</td>"
            } else {
                //il resto è il file
                list = listFromCSV(event.data);
                createTable();
                csvString = event.data
                //setDownloadCSV(fileName, event.data);

                //in questa pagina non aggiorna i dati in realtime
                websocket.close();
                aggiornaTempoPassato(new Date());
            }
            let datepicker = document.getElementById("datepicker");
            datepicker.classList.remove("disabled");

            let download = document.getElementById("download");
            download.classList.remove("disabled");
        }
        
        //processWebSocketData(event.data);
        
    };

    // Evento che si verifica quando la connessione WebSocket è chiusa
    websocket.onclose = function(event) {
        console.log("Connessione WebSocket chiusa");
    };

    // Evento che si verifica in caso di errore
    websocket.onerror = function(event) {
        console.error("Errore WebSocket: ", event);
        let table = document.getElementById("divTable");
        table.innerHTML = "<tr><td colspan='2'>Si è verificato un errore!</td>"
    };
}




//carica i dati da github con xhttp requests
/* function run() {

    // Creating Our XMLHttpRequest object 
    let xhr = new XMLHttpRequest();

    // Making our connection  
    let url = 'https://raw.githubusercontent.com/TommyFara/OPC-N3-data/main/DatiOPC-N3_OPC-N3-1_20240606.csv';
    xhr.open("GET", url, true);

    // function execute after request is successful 
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            console.log(this.responseText);
            list = listFromCSV(this.responseText);
            createTable();
        }
    }
    // Sending our request 
    xhr.send();
} */

//carica i dati da github
/* function loadData(){
    const timestamp = new Date().getTime();

    // Costruisci l'URL con il parametro nocache
    const url = `https://raw.githubusercontent.com/TommyFara/OPC-N3-data/main/DatiOPC-N3_OPC-N3-1_20240606.csv?nocache=${timestamp}`;


    $.ajax({
        url: url,
        cache: false, // Disabilita la cache
        success: function (csv) {
            smallList = listFromCSV(csv);
            createTable();
            //fillCmb();
        },
        error: function (err) {
            console.error('Errore nella richiesta del file CSV:', err);
        }
    });
} */
