# 不必要な部分
import os
import pandas as pd
import csv

FILE_DIRECTORY = "C:/Users/yudai/Desktop/TestFile/"

INDEX_NAME = ['date','num','学籍番号','1','2','3','4','5']

#csvファイルの列をカウントします
def count_rows(FILE_DIRECTORY):
    with open(FILE_DIRECTORY, encoding = 'cp932') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    return len(rows)

# ここまで

# ここから実験
newFormatFiles = [] # 新形式のファイルの絶対パスを保存する配列
TARGET_STRING = "report-answer" # ファイル名に含まれる文字列(予定)
for filename in os.listdir(FILE_DIRECTORY):
    if TARGET_STRING in filename: # ファイル名にTARGET_STRINGが含まれる場合
        newFormatFiles.append(os.path.join(FILE_DIRECTORY, filename)) # ファイルの完全パスを配列に追加

for file in newFormatFiles:
    with open(file, encoding='cp932') as read_csv:
        with open(FILE_DIRECTORY + '/new.csv', mode = 'w', encoding = 'cp932', newline = "") as write_csv:
            reader = csv.DictReader(read_csv)
            writer = csv.writer(write_csv)
            # 初期化
            new_student_number = None # 新規学生番号
            old_student_number = None # 既知学生番号
            student_answer_info = [] # 学生回答データ
            writer.writerow(INDEX_NAME) # INDEX
            for read_csv_row in reader:
                new_student_number = read_csv_row['名前（姓）']
                if new_student_number != old_student_number:
                    if old_student_number: # 書き出し
                        writer.writerow(student_answer_info)
                    student_answer_info = [read_csv_row['提出日時'], read_csv_row['提出レポートID'], read_csv_row['名前（姓）'], read_csv_row['ユーザーの回答内容']]
                else:
                    student_answer_info.append(read_csv_row['ユーザーの回答内容'])
                old_student_number = new_student_number
            writer.writerow(student_answer_info) # 最終書き出し