# herbiebot

Both scripts use `argparse`, so just start them with `--help` to find out about
command line arguments.

## `herbiebot`

Simple Telegram bot to send pictures to a file server.

**Deployment:** Install dependencies (`requirements.txt`), set the Telegram 
bot access token as environment variable (`HERBIE_ACCESS_TOKEN`) and start 
the script in the background (use `screen` when using a remote server 
to avoid problems when the SSH connection closes).

## `image_preview`

Script to create previews for all pictures files in a directory (walks 
through all subdirectories too). Also converts raw images to JPEG.

**Deployment:** Add a Cronjob to start it frequently, e.g. every hour. Use 
`nice -n 19`. The script has a locking mechanism to ensure that only one 
instance runs at a time, so there is no problem if one run takes longer than
a hour.
