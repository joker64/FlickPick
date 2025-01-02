@echo off
echo Starting FlickPick Movie Recommender...
echo.

:: Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r "IPv4.*[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*"') do (
    set LOCAL_IP=%%a
)
set LOCAL_IP=%LOCAL_IP:~1%

:: Display access information
echo Your app will be available at:
echo http://%LOCAL_IP%:5000
echo.

:: Create firewall rule if it doesn't exist
netsh advfirewall firewall show rule name="Flask App" >nul 2>&1
if errorlevel 1 (
    echo Creating firewall rule...
    netsh advfirewall firewall add rule name="Flask App" dir=in action=allow protocol=TCP localport=5000
) else (
    echo Firewall rule already exists
)

echo Starting the application...
echo Press Ctrl+C to stop the server
echo.

:: Start the Flask application
python main.py

pause 