#!/bin/bash
pyinstaller \
    --onefile \
    --windowed \
    --noconfirm \
    --log-level=WARN \
    --add-data="README.md:." \
    --add-data="droptopus/assets:assets" \
    --paths droptopus \
    --upx-dir=/usr/local/share/ \
    --name droptopus \
    --icon droptopus/assets/droptopus.png \
    droptopus/main.py
