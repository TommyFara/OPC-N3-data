function createMap(misurazioni){
    var map = L.map('map').setView([45.64203, 9.105091], 7);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
   
    let markers = [];

    for (let i = 0; i < misurazioni.length; i++){
        if (!isNaN(misurazioni[i].latitude) && !isNaN(misurazioni[i].longitude)){
            markers[i] = L.marker([misurazioni[i].latitude, misurazioni[i].longitude]).addTo(map);
            markers[i].bindPopup("<b>PM1: </b>" + misurazioni[i].pm1 + "<br><b>PM2.5: </b>" + misurazioni[i].pm25 + "<br><b>PM10: </b>" + misurazioni[i].pm10);
        }
    }

    var popup = L.popup();

    function onMapClick(e) {
        popup
            .setLatLng(e.latlng)
            .setContent("You clicked the map at " + e.latlng.toString())
            .openOn(map);
    }

    map.on('click', onMapClick);
}

function inizialize(){
    let urlData = getUrlParameter('data');
    createSocket(urlData);
}

// function createSocket() {
//     const wsUri = "ws://172.16.1.16:8765";
//     const websocket = new WebSocket(wsUri);

//     websocket.onopen = function (event) {
//         console.log("Connessione WebSocket aperta");
//         websocket.send("getData#"+urlData);
//     };

//     websocket.onmessage = function (event) {
//         console.log("Dati ricevuti tramite WebSocket: " + event.data);

//         let command = event.data.split('#');
//         if (command[0] == "fileName") {
//             fileName = command[1];
//         } else {
//             let data = parseCSV(event.data);

//             createMap(data);
//             websocket.close();
//         }
//     };

//     websocket.onclose = function (event) {
//         console.log("Connessione WebSocket chiusa");
//     };

//     websocket.onerror = function (event) {
//         console.error("Errore WebSocket: ", event);
//         alert("Impossibile caricare i dati, riprovare più tardi");
//     };
// }

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
                alert("Nessun dato ricevuto dal server, riprovare più tardi");
            } else {

                let data = parseCSV(event.data);
                createMap(data);

                websocket.close();
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
        alert("Impossibile recuperare i dati, riprova più tardi");
    };
}

function parseCSV(strCSV) {
    const rows = strCSV.trim().split('\n');  // Divide il CSV in righe
    const data = rows.slice(1).map(row => {  // Salta la riga di intestazione e itera sulle restanti righe
        const columns = row.split(';');
        return {
            datetime: columns[0],
            temperature: parseFloat(columns[1]),
            humidity: parseFloat(columns[2]),
            pm1: parseFloat(columns[3]),
            pm25: parseFloat(columns[4]),
            pm10: parseFloat(columns[5]),
            latitude: parseFloat(columns[6]),
            longitude: parseFloat(columns[7])
        };
    });

    return data;
}


function getUrlParameter(name) {
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(window.location.href);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

// dati di esempio per provare la mappa
const csvData = [
    "Data e ora;Temperatura;Umidita;PM 1;PM 2.5;PM 10;Latitudine;Longitudine",
    "2024-06-06 14:10:53;31.806;41.232;1.221;3.25;15.74;45.624;9.346",
    "2024-06-06 14:10:58;32.217;40.726;0.279;0.591;0.703;47.624;11.346",
    "2024-06-06 14:11:03;32.191;40.721;0.27;1.711;15.795;39.624;10.346",
    "2024-06-06 14:11:08;32.191;40.733;0.39;0.934;1.082;45.624;9.346",
    "2024-06-06 14:11:13;32.191;40.721;0.374;0.979;1.492;48.624;10.346",
    "2024-06-06 14:11:18;32.204;40.749;0.416;1.249;1.871;44.624;13.346"
];


