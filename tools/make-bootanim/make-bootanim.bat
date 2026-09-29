@echo off
rem make-bootanim: turn a PNG or GIF into a boot-splash mod for the Digitakt
rem mk1 or Digitone mk1. It calls make_bootanim.py next to this file.
setlocal
if "%~1"=="" goto usage

where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0make_bootanim.py" %*
  exit /b %errorlevel%
)
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 "%~dp0make_bootanim.py" %*
  exit /b %errorlevel%
)

echo Python 3 was not found on PATH.
echo Install it, or run:  python "%~dp0make_bootanim.py" IMAGE.png
exit /b 1

:usage
echo make-bootanim - turn a PNG or GIF into a boot-splash mod
echo.
echo   make-bootanim.bat IMAGE.png [options]
echo   make-bootanim.bat IMAGE.gif [options]
echo.
echo   -o DIR        output mod folder (default NAME-bootanim)
echo   --name NAME   mod name/title
echo   --dn          Digitone mk1 ^(1.43^) instead of Digitakt mk1 ^(1.53^)
echo   --frames N    max frames to keep (default 60)
echo   --invert      swap ink and paper
echo   --dither      Floyd-Steinberg instead of threshold
echo   --text STR    render text instead of an image
echo.
echo Needs Pillow:  python -m pip install pillow
exit /b 2
