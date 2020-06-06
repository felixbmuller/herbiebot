#!/bin/bash

set -x

scp herbiebot.py root@herbie:/opt/herbiebot/herbiebot.py
scp image_preview.py root@herbie:image_preview/image_preview.py