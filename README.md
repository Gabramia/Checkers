open console and run this commands in order


cd "[file path into checkers file]"

pip install -r requirements.txt

python -m main



or if you want exe : 
_____________________________
pyinstaller --onefile --add-data "assets;assets" --distpath . main.py

for windows

pyinstaller --onefile --add-data "assets:assets" --distpath . main.py

for linux
___________________________


Run This code in order to create executable file and run game
