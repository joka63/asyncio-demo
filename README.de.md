[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![de](https://img.shields.io/badge/lang-de-yellow.svg)](README.de.md)

# asyncio-demo
Funktionen von Pythons asyncio erkunden

## Beispiele

### async_periodic_tasks.py

- Periodische Übermittlung von bis zu 20 Aufträgen für ein fiktives Batch-System (alle 2 Sekunden)
- Überprüfung des Status der eingereichten Aufträge in regelmäßigen Abständen (alle 15 Sekunden)
- Beenden, wenn alle fiktiven Aufträge beendet sind und Ausgabe einer Statistik der Turn-Around-Zeiten als Tabelle im .csv-Format.

- Lang andauernde Befehle werden durch einen sleep-Befehl oder durch einen Aufruf von asyncio.sleep() mit einer zufälligen Dauer simuliert
- Verwendung eines Producer/Consumer-Designmusters mit 3 Warteschlangen
- Periodische Aufgaben werden durch Schleifen in zwei Producern implementiert, die jeweils eine Anfrage zur asyncio.Queue hinzufügen und dann für eine feste Dauer schlafen.
- Consumer verarbeiten die Job-Submits oder Job-Statusprüfungen
 

## Links zu Asyncio Tutorials

- [RealPython: Async IO in Python - A Complete Walkthrough](https://realpython.com/async-io-python)
