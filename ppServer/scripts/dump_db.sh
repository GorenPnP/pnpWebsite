#!/bin/bash

x=1
y=$(date +"%w")

if (( x == y )); then
    datum=$(date +%y-%m-%d)
    cp /home/vstein/penPaperWeb/ppServer/db.sqlite3 /home/vstein/penPaperWeb/ppServer/dumps/$datum
fi
