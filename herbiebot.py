from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import logging
import secrets
import exifread
import re
from datetime import datetime
import mimetypes
import traceback
import sys
import argparse

logger = logging.getLogger(__name__)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=(
        "Hi, I'm HerbieBot. I will save every picture that is sent to me on "
        "the server I am running on. Please send pictures as documents to "
        "avoid loss of quality."))

def extract_file_id(msg):
    was_document = True
    file_id_to_download = None
    file_ending = None

    if msg.document is not None:
        file_id_to_download = msg.document.file_id
        file_ending = mimetypes.guess_extension(msg.document.mime_type)
    elif msg.photo:
        max_width = -1
        for photo in msg.photo:
            if photo.width > max_width:
                max_width = photo.width
                file_id_to_download = photo.file_id
        was_document = False

    if file_ending is None:
        file_ending = ".jpg"

    if msg.forward_from is not None:
        sender = msg.forward_from.username
    elif msg.from_user is not None:
        sender = msg.from_user.username
    else:
        sender = "UNKNOWN"

    logger.info(f"Captured message: file_id={file_id_to_download}, "
                f"was_document={was_document}, file_ending={file_ending}, sender={sender})")
    
    return file_id_to_download, was_document, file_ending, sender

def download_and_save_file(bot, file_id, save_dir, source_username, file_ending):
    """
    param is file ending with dot!
    """

    # can do max 20MB -> no videos
    file = bot.get_file(file_id)

    # avoid collisions
    random_name = secrets.token_urlsafe()

    full_path = os.path.join(save_dir, random_name)

    file.download(custom_path=full_path)

    with open(full_path, 'rb') as fh:
        tags = exifread.process_file(fh, stop_tag="EXIF DateTimeOriginal")
        dateTaken : str= str(tags.get("EXIF DateTimeOriginal", ""))

    if re.match(r"\d{4}:\d{2}:\d{2} \d{2}:\d{2}:\d{2}", dateTaken):
        file_name = dateTaken.replace(" ", "_").replace(":", "-") + "_" + source_username + file_ending
    else:
        file_name = "META_UNKNOWN_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + source_username + file_ending

    new_path = os.path.join(save_dir, file_name)

    while os.path.isfile(new_path):
        # ensure unique file name
        new_path = new_path[:-len(file_ending)] + "-" + file_ending

    logger.info(f"Saved file as {new_path}")

    # small race condition, but thats okay 
    os.rename(full_path, new_path)

SAVE_DIR = ""

def handle_files(update, context):
    msg = update.message

    try:
        file_id, was_document, file_ending, sender = extract_file_id(msg)
        if file_id is None:
            logger.warn("No file id to download even though a document/picture mail was received")
        download_and_save_file(context.bot, file_id, SAVE_DIR, sender, file_ending)
        if was_document:
            text = "Saved file successfully."
        else:
            text = "Saved image successfully. Please consider sending images as files (attachment > file > gallery) for better quality if feasible."
        
    except Exception as e:
        logger.error(type(e).__name__ + ": " + str(e))
        text = "Saving the image failed, please try again later. Error Message: " + type(e).__name__ + ": " + str(e)
        #traceback.print_exc()

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)

def handle_video(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I cannot handle videos.")

def main():
    global SAVE_DIR


    parser = argparse.ArgumentParser(description='Run HerbieBot to save pictures from Telegram.')
    parser.add_argument('save_dir', help='where to save the images')
    parser.add_argument("--logfile", default="herbiebot.log", help="logfile location (default: herbiebot.log)")

    args = parser.parse_args()

    SAVE_DIR = os.path.abspath(os.path.expanduser(os.path.expandvars(args.save_dir)))

    logging.basicConfig(filename=args.logfile, 
                        filemode='a', 
                        level=logging.INFO,
                        format='%(asctime)s [%(levelname)s]: %(message)s')


    logger.info(f"Saving files to {SAVE_DIR}")

    updater = Updater(token=os.environ['HERBIE_ACCESS_TOKEN'], use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.photo | Filters.document, handle_files))
    dispatcher.add_handler(MessageHandler(Filters.video, handle_video))

    updater.start_polling()


if __name__ == "__main__":
    main()