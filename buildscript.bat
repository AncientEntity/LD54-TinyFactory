:: windows exe
pyinstaller.exe --noconsole main.py --specpath build/spec --distpath build/dist --workpath build/build
robocopy art build/dist/main/art /E
robocopy sound build/dist/main/sound /E
robocopy data build/dist/main/data /E

:: windows with python3 virtual environment
::robocopy art build/winpy/art /E
::robocopy sound build/winpy/sound /E
::robocopy data build/winpy/data /E
::robocopy venv build/winpy/venv /E

::copy "main.py" "build/winpy/main.py"
::copy "item.py" "build/winpy/item.py"
::copy "itemgen.py" "build/winpy/itemgen.py"
::copy "spritesheet.py" "build/winpy/spritesheet.py"
::copy "button.py" "build/winpy/button.py"
::copy "Tiny Factory.lnk" "build/winpy/Tiny Factory.lnk"


echo COMPLETED

pause