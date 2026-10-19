#!/bin/bash
while true; do
    raspi-gpio get 8
    raspi-gpio get 7
    sleep 1
done
