# WT2 Prakitkum: WG App
Hi
# Installation
Repo runterladen, venv erstellen & dependencies in der venv installieren:
```
$ cd myCodes
$ git clone https://github.com/ChristianFigge/wt2-wg-app 
$ cd wt2-wg-app
$ python -m venv .venv

# venv aktivieren (Linux)
$ source .venv/Scripts/activate
# ODER (Windows cmd.exe)
> call .venv/Scripts/activate.bat
# ODER (Windows PowerShell) - ggf. vorher mit zB "set-executionpolicy remotesigned" ausführung erlauben
> .venv/Scripts/Activate.ps1

$ pip install -r app/requirements.txt
```

# Server starten
In der aktivierten python venv:
```
$ fastapi dev start_app.py
```
dann im Browser http://127.0.0.1:8000/ aufrufen.
(Und den AttributeError zu bcrypt.__about__ ignorieren ...)
