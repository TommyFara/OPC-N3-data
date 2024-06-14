let list = [];

let filter = "";

function inizializzaPagina() {
    $.ajax({
        url: 'https://raw.githubusercontent.com/longhimatteo/data/master/nazionale2006.csv',
        success: function (csv) {

            list = listFromCSV(csv);
            fillCmb();
        }
    });
}

function listFromCSV(csv) {

    let lines = csv.split("\r\n");
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

    return result;
}

function createTable() {
    //ToDo: document.getElementById("div1").innerHTML = data;
    //      oppure creaTabella()....
    if (list.length > 0) {  // controllo se list non è vuota
        let table = document.getElementById("div1");
        let t = "<table id='mainTable'>";

        // ottengo gli attributi dell'oggeto da inserire nella priga riga
        let headers = [];
        for (const key in list[0]) {
            headers.push(key);
        }

        t += "<thead><tr>";
        for (const header of headers) {
            t += "<th>" + header + "</th>"
        }
        t += "</tr></thead>";

        t += "<tbody>";
        let c = 0;  // contatore
        for (let element of list) {
            if (element != null) {
                t += "<tr id='row" + c + "'>";
                if (element.ruolo == filter || filter == "") {   // controllo per il filtro ruoli
                    for (const key in element) {
                        t += "<td>" + element[key] + "</td>"
                    }
                    t += "<td><input type='button' onclick='convoca(" + c + ")' value='Convoca'/></td>"    // aggiungo bottone per convocare
                    t += "<tr/>";
                }
            }
            c++;
        }
        t += "</tbody>";
        t += "<table/>";
        table.innerHTML = t;
    }
}

function fillCmb() {
    let cmbRuolo = document.getElementById("cmbRuolo");
    let ruoli = [];

    for (const obj of list) {
        if (!ruoli.includes(obj.ruolo)) {
            ruoli.push(obj.ruolo);
        }
    }

    let s = "";

    // prima opzione combobox per non filtrare nulla
    s += "<option value=''>Tutti</option>"

    for (const ruolo of ruoli) {
        s += "<option value='" + ruolo + "'>" + ruolo + "</option>";
    }

    cmbRuolo.innerHTML = s;
}

function changeFilter() {
    let value = document.getElementById("cmbRuolo").value;
    filter = value;
    createTable();
}

function convoca(nRiga) {
    let riga = document.getElementById("row" + nRiga)
    riga.children[2].style.fontWeight = "bold";
}
