pyinstaller.exe --noconsole main.py --specpath build/spec --distpath build/dist --workpath build/build
robocopy art build/dist/main/art /E
robocopy sound build/dist/main/sound /E
echo COMPLETED

pause