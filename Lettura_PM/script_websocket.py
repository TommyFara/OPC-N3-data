import asyncio
import websockets
import os
import sys
import datetime
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# Path del file da monitorare
date = datetime.date.today()
OPCNAME = "OPC-N3-1"
LOCATION = "DatiOPC-N3"
file_path = '/home/user/Desktop/' + LOCATION + '_' + OPCNAME + '_' + str(date).replace('-','') + ".csv"

# Lista dei client connessi
toUpdate_clients = set()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, loop):
        self.loop = loop

    def on_modified(self, event):
        if event.src_path == file_path:
            print(f"{file_path} è stato modificato")
            # Leggi il file aggiornato
            with open(file_path, 'r') as file:
                data = file.read()
            # Invia i dati a tutti i client connessi
            asyncio.run_coroutine_threadsafe(broadcast_data(data), self.loop)

async def broadcast_data(data):
    if toUpdate_clients:
        await asyncio.gather(*[client.send(data) for client in toUpdate_clients])
        
async def wait_command_response(websocket):
    response = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    await websocket.send(response.strip())
  
async def handle_connection(websocket, path):
    print("Nuovo client connesso")
    
    try:
        async for message in websocket:
            command = message.split('#')
            match command[0]:
                case 'getData':
                    await sendFileOnce(websocket, command[1])
                    
                case 'changeDate':
                    await sendFileOnce(websocket, command[1])
                    
                case 'getUpdates':
                    toUpdate_clients.add(websocket)
                    
                case _:
                    print(message, file=sys.stdout)
                    response_task = asyncio.create_task(wait_command_response(websocket))
                    await response_task
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        print("Client disconnesso")
        toUpdate_clients.remove(websocket)

async def main():
    # Imposta il loop principale di asyncio
    loop = asyncio.get_running_loop()

    # Imposta l'osservatore per monitorare il file
    event_handler = FileChangeHandler(loop)
    observer = Observer()
    observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
    observer.start()
    
    print("Server avviato!", file=sys.stdout)
    sys.stdout.flush()

    try:
        # Avvia il server WebSocket su tutte le interfacce di rete
        async with websockets.serve(handle_connection, "0.0.0.0", 8765):
            await asyncio.Future()  # Mantieni il server in esecuzione
        
    except:
        print("Errore socket!", file=sys.stdout)
    finally:
        observer.stop()
        observer.join()
    
    
async def sendFileOnce(websocket, _date):
    if(_date == 'cur'):
        _date = date
    #la prima stringa è il nome del file per il download
    fileName = "fileName#" + LOCATION + '_' + OPCNAME + '_' + str(_date).replace('-','') + ".csv"
    file_path = '/home/user/Desktop/' + LOCATION + '_' + OPCNAME + '_' + str(_date).replace('-','') + ".csv"
    print(file_path)
    await websocket.send(fileName)
    
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            fileCompleto = []
            for row in reader:
                row += "\n"
                fileCompleto += row
            
            await websocket.send(fileCompleto)
    except:
        await websocket.send("noData")
        
# Esegui il main loop
if __name__ == "__main__":
    asyncio.run(main())
