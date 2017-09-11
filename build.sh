#!/bin/bash
pyinstaller \
    --onefile \
    --nowindow \
    --noconfirm \
    --log-level=WARN \
    --add-data="README.md:." \
    --add-data="droptopus/assets:assets" \
    --paths droptopus \
    --upx-dir=/usr/local/share/ \
    --name droptopus \
    droptopus/main.py
