#### kgcareer009.py ####
#### update:2023/4/18 ####

#### ライブラリのインポート ####
import pandas as pd  # pandasのインポート
from pathlib import Path  # path
import tkinter as tk  # 画面生成
from tkinter import ttk  # 画面生成
from tkinter import filedialog  # 画面生成
import tkinter.messagebox as tmsg  # 画面生成
import MeCab  # MeCab(品詞分解要ライブラリ)
import csv  # csv
import os  # os
import datetime  # 時間取得
import time  # 時間取扱
import glob  # ファイル取得用
import shutil  # ファイルのコピー用
from pykakasi import kakasi  # 揺らぎ変換
kakasi = kakasi()

#### グローバル変数定義 ####
FILE_INFO = ""  # 参照するパス＋ファイル名
FILE_DIRECTORY = ""  # 参照するディレクトリのパス
FILE_NAME = ""  # 参照するファイル名
OUTPUT_NAME = "result.csv"  # 書き出しファイルの名前
NGWORD = []  # NGワード一覧
NGWORD_SUM = 0  # NGワードの数
FILE_TYPE = ".csv"

#### 入力画面の関数 ####


def indent(content):
    print("*----------------------------*")
    print("処理:", str(content))
    print("開始:", datetime.datetime.now())


def Input_check(event=None):
    global FILE_DIRECTORY, FILE_INFO, FILE_NAME, file_info
    FILE_INFO = file_info.get()
    FILE_NAME = os.path.basename(FILE_INFO)
    FILE_DIRECTORY = os.path.dirname(FILE_INFO)
    indent("データのダウンロード")
    print("FILE_INFO:", FILE_INFO)
    print("FILE_DIRECTORY:", FILE_DIRECTORY)
    print("FILE_NAME:", FILE_NAME)
    if FILE_INFO == "":
        tmsg.showerror("警告", "必須項目を埋めてください")
    else:
        Input_screen.destroy()
        print("報告:入力を確認しました。")


def find_func():
    global FILE_INFO
    file_info.delete(0, tk.END)
    idir = os.path.abspath(os.path.dirname(__file__))
    filetype = [("csvファイル", "*.csv")]
    FILE_INFO = filedialog.askopenfilename(filetypes=filetype, initialdir=idir)
    file_info.insert(tk.END, FILE_INFO)


def Input_NGWORD():
    global NGWORD, NGWORD_SUM
    print("状態:NGワード")
    s = ngword.get()
    NGword_list.insert(tk.END, s)
    NGWORD.append(s)
    NGWORD_SUM += 1
    print(NGWORD)


def Delete_NGWORD():
    global NGWORD, NGWORD_SUM
    print("delete")
    NGword_list.delete("1.0", "end")
    NGWORD = list()
    NGWORD_SUM = 0


#### 入力画面生成 ####
# キャンバスの作成
os.system('cls')  # ターミナルリセット
indent("入力待機状態")
Input_screen = tk.Tk()
Input_screen.geometry("800x360+0+0")
Input_screen.title("情報入力画面")

# パス入力場所を作成
Input_screen_L1 = ttk.Label(
    Input_screen, text="csvファイルを選択(必須)", font=("Helvetica", 10))
Input_screen_L1.place(x=20, y=20)
file_info = ttk.Entry(width=40, font=("Helventica", 14))
file_info.place(x=250, y=20)
Findpath_button = ttk.Button(Input_screen, text="参照", command=find_func)
Findpath_button.place(x=660, y=20)

# キーワードの入力ボックス
Input_screen_L2 = ttk.Label(
    Input_screen, text="NGワードを入力してください", font=("Helvetica", 10))
Input_screen_L2.place(x=20, y=90)
ngword = ttk.Entry(width=40, font=("Helventica", 14))
ngword.place(x=20, y=110)
ngword.insert(tk.END, "ここにNGワードを入力")
NGword_add = ttk.Button(Input_screen, text="追加",
                        width=20, command=Input_NGWORD)
NGword_add.place(x=450, y=110)
NGword_del = ttk.Button(Input_screen, text="リセット",
                        width=20, command=Delete_NGWORD)
NGword_del.place(x=600, y=110)
Input_screen_L3 = ttk.Label(
    Input_screen, text="NGワードリスト", font=("Helvetica", 10))
Input_screen_L3.place(x=20, y=140)
NGword_list = tk.Text(Input_screen, font=("Helvetica", 14))
NGword_list.place(x=20, y=160, width=400, height=150)
Check_Button = ttk.Button(Input_screen, text="添削開始",
                          width=30, command=Input_check)
Check_Button.place(x=500, y=260)

Input_screen.mainloop()

#### 関数一覧 ####
# csvファイルの列カウント
def count_rows(FILE_DIRECTORY):
    with open(FILE_DIRECTORY, encoding='cp932') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    return len(rows)

# 名詞抽出
def wakati_text(text):
    tagger = MeCab.Tagger('')
    select_conditions = ['名詞']
    node = tagger.parseToNode(text)
    terms = []
    while node:
        term = node.surface
        pos = node.feature.split(',')[0]
        if pos in select_conditions:
            terms.append(term)
        node = node.next
    text_result = ''.join(terms)
    return text_result


#### csvファイル読取 & 変換 ####
INDEX_NAME = ['回答日時', '受付番号', '学籍番号', '1', '2', '3', '4', '5']

indent("新規形式ファイルの検出")
newFormatFiles = []  # 新形式のファイルの絶対パスを保存する配列
TARGET_STRING = "report-answer"  # ファイル名に含まれる文字列(予定)
for filename in os.listdir(FILE_DIRECTORY):
    if TARGET_STRING in filename:  # ファイル名にTARGET_STRINGが含まれる場合
        newFormatFiles.append(os.path.join(
            FILE_DIRECTORY, filename))  # ファイルの完全パスを配列に追加
print(f"検出：{newFormatFiles}")
print("終了:", datetime.datetime.now())

indent("新規形式ファイルの統合")
for file in newFormatFiles:
    with open(file, encoding='cp932') as read_csv:
        with open(FILE_DIRECTORY + "newFormatTemp.csv", mode='w', encoding='cp932', newline="") as write_csv:
            reader = csv.DictReader(read_csv)
            writer = csv.writer(write_csv)
            new_student_number = None  # 新規学生番号
            old_student_number = None  # 既知学生番号
            student_answer_info = []  # 学生回答データ
            writer.writerow(INDEX_NAME)  # INDEX
            #### ファイル書換処理 ####
            for read_csv_row in reader:
                new_student_number = read_csv_row['名前（姓）']
                if new_student_number != old_student_number:
                    if old_student_number:  # 書き出し
                        writer.writerow(student_answer_info)
                    student_answer_info = [
                        read_csv_row['提出日時'], read_csv_row['提出レポートID'], read_csv_row['名前（姓）'], read_csv_row['ユーザーの回答内容']]
                else:
                    student_answer_info.append(read_csv_row['ユーザーの回答内容'])
                old_student_number = new_student_number
            writer.writerow(student_answer_info)  # 最終書き出し
    #### ファイル名の統合 ####
    new_FILE_INFO = file.replace(TARGET_STRING, "")
    if str(os.path.basename(file)) == str(FILE_NAME): # 選択ファイルが新形式の場合
        FILE_INFO = new_FILE_INFO
        FILE_NAME = os.path.basename(FILE_INFO)
        FILE_DIRECTORY = os.path.dirname(FILE_INFO)
    os.remove(file)
    shutil.copy(FILE_DIRECTORY + "newFormatTemp.csv", new_FILE_INFO)
    os.remove(FILE_DIRECTORY + "newFormatTemp.csv")
print("終了:", datetime.datetime.now())

indent("指定csvファイルに対する印付け")
datafile = pd.read_csv(FILE_INFO, dtype='object',
                       names=INDEX_NAME, encoding='cp932')
with open(FILE_DIRECTORY + '/marked.csv', mode='w', encoding='cp932', newline="") as f:
    writer = csv.writer(f)
    writer.writerow(INDEX_NAME)
    for i in range(1, count_rows(FILE_INFO)):
        writer.writerow(["check", datafile.loc[i, '受付番号'], datafile.loc[i, '学籍番号'], datafile.loc[i, '1'],
                        datafile.loc[i, '2'], datafile.loc[i, '3'], datafile.loc[i, '4'], datafile.loc[i, '5']])
print("終了:", datetime.datetime.now())

indent("該当ディレクトリのcsvファイルの合成")
files = sorted(glob.glob(FILE_DIRECTORY + '/*.csv'))
file_number = len(files) - 1
print("状態:", file_number, "のファイルを検出")
csv_list = []
for file in files:
    if str(FILE_NAME) not in str(file):
        csv_list.append(pd.read_csv(file, dtype="object",
                        names=INDEX_NAME, encoding='cp932'))
        print("対象:", file)
merge_csv = pd.concat(csv_list)
merge_csv.to_csv(FILE_DIRECTORY + '/merge.csv', encoding='cp932', index=False)
print("終了:", datetime.datetime.now())

indent("データ読取")
datafile = pd.read_csv(FILE_DIRECTORY + '/merge.csv',
                       names=INDEX_NAME, dtype='object', encoding='cp932')
datafile.sort_values(by="学籍番号", inplace=True, na_position="last")
datafile.to_csv(FILE_DIRECTORY + "/sort.csv", encoding='cp932', index=False)
datafile = pd.read_csv(FILE_DIRECTORY + '/sort.csv',
                       dtype='object', names=INDEX_NAME, encoding='cp932')
COLUMN_NUM = count_rows(FILE_DIRECTORY + '/sort.csv')
print("終了:", datetime.datetime.now())

indent("不必要なファイルの消去")
FILE_LIST = [FILE_DIRECTORY + '/merge.csv', FILE_DIRECTORY +
             '/sort.csv', FILE_DIRECTORY + '/marked.csv']
for file in FILE_LIST:
    os.remove(file)
    print("実行:", file, "を消去")
print("終了:", datetime.datetime.now())

indent("csvデータの格納を開始")
student_num = []  # 学籍番号格納配列
student_num_preserve = []  # 学籍番号保存格納配列
student_date = []  # 回答時間
student_pattern = []  # コピペ分類
student_retake = []  # 再履修判定
student_keyword1 = []  # キーワード1そのまま格納配列
student_keyword2 = []  # キーワード2そのまま格納配列
student_keyword3 = []  # キーワード3そのまま格納配列
student_keyword4 = []  # キーワード4そのまま格納配列
student_keyword5 = []  # キーワード5そのまま格納配列
student_keyword = []  # キーワードそのまま格納配列
student_keyword_withoutspace = []  # キーワードを1つの単語にまとめた配列
student_keyword_original = []  # キーワードを1つの単語にまとめた配列
student_keyword_sorted = []  # ソート済みキーワード格納配列

for i in range(COLUMN_NUM):
    #### 残り時間計算処理 ####
    interval = 1000
    if i == 0:
        time_sta = time.time()
    if i == interval - 1:
        time_end = time.time()
        tim = time_end - time_sta
    if i > interval:
        time_now = tim * (COLUMN_NUM - i) / interval
        print("残り:約", int(time_now / 60), "分", round(time_now %
              60, 3), "秒", "(", i + 1, "/", COLUMN_NUM, ")")

    #### 全データ読みとり処理 ####
    student_pattern.append(" ")
    student_retake.append(" ")
    student_num_data = datafile.loc[i, "学籍番号"]
    student_date.append(datafile.loc[i, "回答日時"])
    student_keyword1_data = datafile.loc[i, "1"]
    student_keyword2_data = datafile.loc[i, "2"]
    student_keyword3_data = datafile.loc[i, "3"]
    student_keyword4_data = datafile.loc[i, "4"]
    student_keyword5_data = datafile.loc[i, "5"]

    #### 学籍番号及びキーワード1-5を格納 ####
    student_num.append(student_num_data)
    student_num_preserve.append(student_num_data)
    student_keyword1.append(student_keyword1_data)
    student_keyword2.append(student_keyword2_data)
    student_keyword3.append(student_keyword3_data)
    student_keyword4.append(student_keyword4_data)
    student_keyword5.append(student_keyword5_data)

    #### キーワード1-5を一つの変数に格納 ####
    student_data = datafile.loc[i, "1":"5"]  # 行データの取得
    student_data_lst = student_data.astype(str).tolist()  # listに変換
    student_keyword_original.append(','.join(student_data_lst))
    #### 特定品詞除去 ####
    student_data_org0 = wakati_text(
        ','.join(student_data_lst))  # listをstrに変換後、wakatiを通す
    student_data_org1 = student_data_org0
    #### 品詞除去変数を格納 ####
    student_keyword.append(student_data_org0)  # student_keywordに登録
    student_keyword_withoutspace.append(student_data_lst)
    #### 揺らぎ対応処理 ####
    student_data_org1 = student_data_org0.lower()  # (全角、半角問わず)アルファベットを小文字に統一
    student_data_org1 = student_data_org1.translate(str.maketrans(
        {chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))  # 半角 -> 全角
    kakasi.setMode('J', 'H')  # 漢字をひらがなに統一
    conv = kakasi.getConverter()
    student_data_org1 = conv.do(student_data_org1)
    kakasi.setMode('K', 'H')  # カタカナをひらがなに統一
    conv = kakasi.getConverter()
    student_data_org1 = conv.do(student_data_org1)
    student_data_org1 = sorted(student_data_org1)
    student_data_org1 = ''.join(student_data_org1)
    student_data_org1 = student_data_org1.replace(",", "")
    student_keyword_sorted.append(student_data_org1)
print("終了:", datetime.datetime.now())

indent("コピペ検出処理")
h = 0  # グループ番号
for i in range(COLUMN_NUM):
    initial = True
    for j in range(i + 1, COLUMN_NUM):
        if ((student_keyword_sorted[i] == student_keyword_sorted[j]) and (student_num_preserve[i] != student_num_preserve[j])):  # コピペ発見時の処理
            if initial & ("Pattern" not in str(student_num[i])) & ("Pattern" not in str(student_num[j])):
                h += 1
                print("パターン", h, "検出\nキーワード:", student_keyword[i])
                student_num[i] = "Pattern" + str(h)
                student_num[j] = "Pattern" + str(h)
                student_pattern[i] = "対象:" + str(student_num_preserve[j]) + " 時期:" + str(
                    student_date[j]) + "全てのキーワード:" + student_keyword_original[j]
                student_pattern[j] = "対象:" + str(student_num_preserve[i]) + " 時期:" + str(
                    student_date[i]) + "全てのキーワード:" + student_keyword_original[i]
                initial = False
            elif "Pattern" not in str(student_num[j]):
                student_num[j] = student_num[i]
                student_pattern[j] = "対象:" + str(student_num_preserve[i]) + " 時期:" + str(
                    student_date[i]) + "全てのキーワード:" + student_keyword_original[i]
        elif (student_num_preserve[i] == student_num_preserve[j]):
            student_retake[i] = "再履修"
            student_retake[j] = "再履修"
print("終了:", datetime.datetime.now())

student_NG_sum = []
student_ngword = []
ngword_temp = []
indent("採点処理")
print("単語:", ngword)
for i in range(COLUMN_NUM):
    sum = 0
    for j in range(NGWORD_SUM):
        ngWord = "".join(NGWORD[j])
        if (ngWord.lower() in str(student_keyword_withoutspace[i]).lower()) == True:
            ngword_temp.append(ngWord)
            sum += 1
    temp = ",".join(ngword_temp)
    student_ngword.append(temp)
    student_NG_sum.append(sum)
    ngword_temp = list()
print("終了:", datetime.datetime.now())

indent("採点結果の出力")
try:
    with open(FILE_DIRECTORY + "/" + OUTPUT_NAME, 'a', encoding='cp932', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["担当教員", "学籍番号", "1", "2", "3", "4", "5", " ", "採点欄",
                        "備考欄", "コピペ群", "重複ワード", "参考情報", " ", "NGワード数", "NGワード一覧", "再履修"])
        for i in range(COLUMN_NUM):
            # 担当教員振り分け処理
            s = str(student_num_preserve[i])[0:2]
            if (s == '21' or s == '22' or s == '23' or s == '27' or s == '29' or s == '31' or s == '36' or s == '37' or s == '38'):
                teacher = '森'
            else:
                teacher = '吉松'
            # 書き出し処理
            if ("check" == str(student_date[i])):
                row_list_base = [teacher, student_num_preserve[i], student_keyword1[i], student_keyword2[i],
                                 student_keyword3[i], student_keyword4[i], student_keyword5[i], " ", " ", " "]
                if ("Pattern" in str(student_num[i])):
                    writer.writerow(row_list_base + [student_num[i], str(student_keyword[i]),
                                    student_pattern[i], " ", student_NG_sum[i], str(student_ngword[i]), student_retake[i]])
                else:
                    writer.writerow(row_list_base + ["", "", student_pattern[i], " ",
                                    student_NG_sum[i], str(student_ngword[i]), student_retake[i]])
    tmsg.showinfo("報告", "ファイル出力に成功しました")
except Exception as e:
    tmsg.showerror("報告", "ファイル出力に失敗しました")
    print("failed", i, "行目")
    print(e)

print("終了:", datetime.datetime.now())
indent("添削プログラムに置ける全過程が終了")
print("終了:", datetime.datetime.now())
