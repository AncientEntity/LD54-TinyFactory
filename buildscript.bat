pyinstaller.exe --noconsole main.py --specpath build/spec --distpath build/dist --workpath build/build
robocopy art build/dist/main/art /E
robocopy sound build/dist/main/sound /E
robocopy data build/dist/main/data /E
echo COMPLETED

pause