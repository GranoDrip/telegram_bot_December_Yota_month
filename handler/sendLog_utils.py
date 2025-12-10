import os
import logging
import requests
from telegram import ReplyKeyboardRemove


def checkFileExention(fileName:str):
    return fileName.lower().endswith(('.adi', '.adif'))
