@echo off
setlocal

echo =======================================================
echo    J.A.R.V.I.S. AUTOMATYCZNY INSTALATOR (WINDOWS 10)
echo =======================================================
echo.

:: Sprawdzenie czy Python jest zainstalowany
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [BLAD] Python nie jest zainstalowany lub nie ma go w zmiennych PATH.
    echo Zainstaluj Pythona ze strony python.org i zaznacz opcje "Add Python to PATH".
    pause
    exit /b
)

:: Tworzenie wirtualnego środowiska, jeśli nie istnieje
if not exist "venv\Scripts\activate" (
    echo [1/4] Tworzenie wirtualnego srodowiska (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [BLAD] Nie udalo sie utworzyc srodowiska venv.
        pause
        exit /b
    )
) else (
    echo [1/4] Wirtualne srodowisko (venv) juz istnieje, pomijam tworzenie.
)

:: Aktywacja wirtualnego środowiska
echo [2/4] Aktywacja srodowiska wirtualnego...
call venv\Scripts\activate

:: Instalacja pakietów z requirements.txt
echo [3/4] Instalowanie i aktualizowanie bibliotek...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [BLAD] Wystapil problem podczas instalacji pakietow z requirements.txt.
    pause
    exit /b
)

echo.
echo [4/4] Instalacja zakonczona sukcesem! 
echo Uruchamianie glownego serwera J.A.R.V.I.S...
echo.
echo =======================================================

:: Uruchomienie J.A.R.V.I.S. w środowisku wirtualnym
python main_live.py

:: Zatrzymanie po zakończeniu lub wysypaniu się błędu
pause
