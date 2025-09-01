set -x

pyinstaller --add-data=logging.yaml:LabGym --noconfirm app.py 

wc -l build/app/warn-app.txt

(
    date
    dist/app/app --debug
)
