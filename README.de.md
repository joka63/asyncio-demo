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

### file_crc64

CRC64-Prüfsummenberechnung mit optimierter Datei-I/O:

- Pure Python CRC64-Implementierung (ECMA-182 Polynom)
- Standardvariante mit `read()`-Methode
- Optimierte Variante mit `readinto()` zur Vermeidung von Speicherallokationen
- Async-Unterstützung mit aiofiles und Threading
- Integrierter Benchmark zum Vergleichen der Leistung

```bash
# Prüfsumme berechnen
python -m examples file_crc64 /pfad/zur/datei

# Optimierte readinto-Variante verwenden
python -m examples file_crc64 /pfad/zur/datei --readinto

# Benchmark ausführen
python -m examples file_crc64 /pfad/zur/datei --bench -n 5
```

Siehe [examples/file_checksum/README.md](examples/file_checksum/README.md) für detaillierte Dokumentation.
 

## Links zu Asyncio Tutorials

- [RealPython: Async IO in Python - A Complete Walkthrough](https://realpython.com/async-io-python)
