print("Library install for KG career program\nUPDATE:2023/3/29")
import os
from time import sleep
os.system("python.exe -m pip install --upgrade pip")
install_list = ["mecab-python3","numpy","pandas","pykakasi","unidic-lite","python-Levenshtein", "pykakasi"]
import datetime
for install in install_list:
    print(f"----------------------------\nstart\t: {datetime.datetime.now()}")
    print(f"to\t: {install}")
    command = f"pip install {install}" 
    try:
        os.system(command)
        print(f"end\t: {datetime.datetime.now()}")
    except Exception as e:
        print(e)
        print("ダウンロード齟齬が発生しました。開発者にお問い合わせください。")
        print(f"Error\t: {install} couldn't successfully install")
        input()
        exit(1)
print(f"終了時刻\t: {datetime.datetime.now()}")
print("すべてのダウンロードが終了しました\n(任意のキーでプログラムを終了)")

input()
        
"""
import webbrowser
url_list = ["https://www.python.org/ftp/python/3.10.5/python-3.10.5-amd64.exe","https://github.com/ikegami-yukino/mecab/releases/download/v0.996.2/mecab-64-0.996.2.exe"]
for url in url_list:
    #command = f"bitsadmin /transfer {url} {os.getcwd()}"
    #//os.system(command)
    webbrowser.open(url, new = 0, autoraise = True)
"""