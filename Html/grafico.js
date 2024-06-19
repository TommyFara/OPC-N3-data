// valrodi di umidità e temperatura medi da calcolare
var tempMedia = 0;
var umMedia = 0;

function inizialize(){
  let urlData = getUrlParameter('data');
  createSocket(urlData);
}

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

              let listData = parseCSV(event.data);
              createGraph(listData);

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

function createGraph(listData) {
  // Definisci i colori
  const CHART_COLORS = {
      red: 'rgb(255, 99, 132)',
      blue: 'rgb(54, 162, 235)',
      green: 'rgb(63, 190, 37)'  // Corretto colore verde
  };

  // Dati per il grafico
  const data = [];
  const data2 = [];
  const data3 = [];
  var count = 0;
  for (var i = 0; i < listData.length; i++) {
    if (dataAreConsistents(listData[i])){
      data.push({ x: count, y: listData[i].pm1 });
      data2.push({ x: count, y: listData[i].pm25 });
      data3.push({ x: count, y: listData[i].pm10 });

      tempMedia += listData[i].temperature;
      umMedia += listData[i].humidity;
      
      count++;
    }
  }

  tempMedia /= listData.length;
  umMedia /= listData.length;

  inserisciDatiFissi();

  const totalDuration = 10000;
  const delayBetweenPoints = totalDuration / data.length;
  const previousY = (ctx) => ctx.index === 0 ? ctx.chart.scales.y.getPixelForValue(100) : ctx.chart.getDatasetMeta(ctx.datasetIndex).data[ctx.index - 1].getProps(['y'], true).y;
  const animation = {
      x: {
          type: 'number',
          easing: 'linear',
          duration: delayBetweenPoints,
          from: NaN, // the point is initially skipped
          delay(ctx) {
              if (ctx.type !== 'data' || ctx.xStarted) {
                  return 0;
              }
              ctx.xStarted = true;
              return ctx.index * delayBetweenPoints;
          }
      },
      y: {
          type: 'number',
          easing: 'linear',
          duration: delayBetweenPoints,
          from: previousY,
          delay(ctx) {
              if (ctx.type !== 'data' || ctx.yStarted) {
                  return 0;
              }
              ctx.yStarted = true;
              return ctx.index * delayBetweenPoints;
          }
      }
  };

// // Configurazione delle opzioni di zoom e pan
//   const zoomOptions = {
//     limits: {
//       x: {min: 0, max: 200, minRange: 50},
//       y: {min: 0, max: 200, minRange: 50}
//     },
//     pan: {
//       enabled: true,
//       mode: 'xy',
//     },
//     zoom: {
//       wheel: {
//         enabled: true,
//       },
//       pinch: {
//         enabled: true
//       },
//       mode: 'xy',
//       onZoomComplete({chart}) {
//         chart.update('none');
//       }
//     }
//   };

//   // Configurazione delle scale
//   const scaleOpts = {
//     reverse: false,
//     ticks: {
//       callback: (val, index, ticks) => index === 0 || index === ticks.length - 1 ? null : val,
//     },
//     grid: {
//       borderColor: 'rgba(0, 0, 0, 0.1)',
//       color: 'rgba(0, 0, 0, 0.1)',
//     },
//     title: {
//       display: true,
//       text: (ctx) => ctx.scale.axis + ' axis',
//     }
//   };

//   const scales = {
//     x: {
//       type: 'linear',
//       position: 'bottom',
//       suggestedMax: 600,
//       min: 0,
//       max: data.length,
//       ...scaleOpts
//     },
//     y: {
//       position: 'left',
//       min: 0,
//       ...scaleOpts
//     }
//   };

 // Configurazione del grafico
  const config = {
    type: 'line',
    data: {
        datasets: [{
            label: 'PM1',  // Etichetta per il primo dataset
            borderColor: CHART_COLORS.red,
            borderWidth: 1,
            radius: 0,
            data: data,
        },
        {
            label: 'PM2.5',  // Etichetta per il secondo dataset
            borderColor: CHART_COLORS.blue,
            borderWidth: 1,
            radius: 0,
            data: data2,
        },
        {
            label: 'PM10',  // Etichetta per il terzo dataset
            borderColor: CHART_COLORS.green,
            borderWidth: 1,
            radius: 0,
            data: data3,
        }]
    },
    options: {
        animation,
        interaction: {
            intersect: false
        },
        plugins: {
            legend: {
                display: true,  // Mostra la legenda
                position: 'top',  // Posizione della legenda (top, bottom, left, right)
                labels: {
                    font: {
                        size: 14  // Dimensione del carattere della legenda
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'linear',
                suggestedMax: 600
            }
        }
    }
  };

  // Crea il grafico
  const ctx = document.getElementById('progressiveLineChart').getContext('2d');
  const myChart = new Chart(ctx, config);
}


function getUrlParameter(name) {
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
      results = regex.exec(window.location.href);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function inserisciDatiFissi(){

  var s = "<label>Temperatura media</label><input type='text' name='txtTempMedia' id='txtTempMedia' readonly='true'><label>Umidità media</label><input type='text' name='txtUmMedia' id='txtUmMedia' readonly='true'></input>";

  document.getElementById("datiFissi").innerHTML = s;
  document.getElementById("txtTempMedia").value = tempMedia.toFixed(2);;
  document.getElementById("txtUmMedia").value = umMedia.toFixed(2);;
}

function dataAreConsistents(obj){
  var x = true;
  for (const key in obj) {
    if (Object.hasOwnProperty.call(obj, key) && key != "longitude" && key != "latitude") {
      if(typeof obj[key] === 'number' && isNaN(obj[key])){   // se uno degli elementi dell'oggetto è NaN ritorna false
        x = false;
        break;
      }
    }
  }
  return x;
}