# Returbil skanner

Dette python-skriptet vil skanne returbil.no etter aktuelle turer ut ifra en forhåndsdefinert *fra by* og *til by*. 
Hvis et funn blir gjort vil den sende en push-notifikasjon til mobilen din. 
Klikk på lenken som blir lagt ved for å gå rett til booking-siden.

<img height="576" alt="demo" src="https://user-images.githubusercontent.com/6738930/60929330-35fa0680-a2b1-11e9-9224-a8cb37ae01c7.png">

## Installasjon

* Skriptet krever integrasjon mot appen [Pushover](https://pushover.net/) for å kunne motta push-meldinger. Følg lenken for å registrere brukerkonto samt installere appen på mobilen din.
    - Når du har opprettet en brukerkonto vil då få tildelt en `user key`.
    - Klikk deretter på "Create an Application/API Token" for å generere en `app token`.
* Klon eller last ned alle filene fra dette github-repoet
* Sørg for at du har python+pip installert. Naviger inn i prosjektmappen og kjør `pip install -r requirements.txt` (gjerne med virtualenv aktivert)

Systemkrav: Utviklet for Python 3.7 eller høyere, men kan potensielt fungere på lavere versjoner også.

## Bruk

Skriptet er beregnet for å kunne kjøre i bakgrunnen. Bruk f.eks. [nohup](https://www.computerhope.com/unix/unohup.htm) til dette formålet.

Kjør følgende kommando for å starte:
```bash
python scan.py -app APP_TOKEN -usr USER_KEY --from-city FROM --to-city TO
```
hvor du bytter ut `USER_KEY`, `APP_TOKEN`, `FROM` og `TO` med dine egne verdier.

Alternativt kan skriptet søke etter flere ønsker samtidig, ved at man lager en fil med navn `wanted.txt`. Denne må være formatert som en .csv-fil uten headers. Verdiene må være separert med komma, og må ikke inneholde mellomrom. Du trenger ikke ta hensyn til store/små bokstaver.

**wanted.txt**:
```csv
Oslo,Kristiansand
Oslo,Bergen
```

Kjør deretter skriptet med flagget `--fromfile`:
```bash
python scan.py -app APP_TOKEN -usr USER_KEY --fromfile
```

## Hjelp

For å vise hjelpeinformasjonen kjør:

```
>>> python scan.py --help
usage: scan.py [-h] [-usr USER_KEY] [-app APP_TOKEN] [--from-city FROM]
               [--to-city TO] [--interval INTERVAL] [--fromfile] [--fuzzy]

This script scans http://returbil.no for desired trips.

optional arguments:
  -h, --help           show this help message and exit
  -usr USER_KEY        Pushover user key
  -app APP_TOKEN       Pushover app token
  --from-city FROM     The city to travel from
  --to-city TO         The city to travel to
  --interval INTERVAL  Interval time for scan in seconds (default 60)
  --fromfile           Load trips from `wanted.txt` instead
  --fuzzy              Allow non-exact matches for city names, by only looking
                       at the first word (e.g. `Trondheim LUFTHAVN VÆRNES`
                       would match if you have entered `Trondheim`)
```