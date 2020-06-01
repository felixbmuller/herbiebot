# herbiebot

Both scripts use `argparse`, so just start them with `--help` to find out about
command line arguments.

## `herbiebot`

Simple Telegram Bot to send pictures to a file server.

**Deployment:** Install dependencies (requirements.txt) and start the script 
in the background (use `screen` to avoid problems when the SSH connection 
closes).  

## `image_preview`

Script to create previews for all pictures files in a directory (walks 
through all subdirectories too). Also converts raw images to JPEG.

**Deployment:** Add a Cronjob to start it frequently, e.g. every hour. Use 
`nice -n 19`. The script has a locking mechanism to ensure that only one 
instance runs at a time, so there is no problem if one run takes longer than
a hour.

## Feature Requests HerbieBot

- Bei Bildern Bot-Auswahlmenü als Antwort, ob das Bild trotzdem gespeichert werden soll
- Bild angekommen nachricht aggregieren, wenn mehrer Bilder nacheinander kommen
- Dateiendung auf JPG statt JPE ändern (Prio A)
- Automatisch nach Tagen in Ordner legen, wenn mehr als X Bilder für diesen Tag
- Reject files larger than 20MB immediately without downloading (Prio A)

## Feature Requests ImagePreview

- Convert files ending with JPE too (Prio A)
