import MeCab
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import os
import re
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.messagebox import showinfo
import time
import jaconv
from pykakasi import kakasi

kks = kakasi()


class PlagiarismChecker:
    def __init__(self, threshold):
        self.threshold = threshold
        self.start_time = time.time()

    def print_elapsed_time(self):
        elapsed_time = time.time() - self.start_time
        print(f"Elapsed time: {elapsed_time:.2f} seconds")

    def wakati_text(self, text):
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

    def read_submissions(self, main_file_path, past_files):
        submissions = defaultdict(list)
        file_paths = [main_file_path] + past_files

        for file_path in file_paths:
            with open(file_path, encoding='cp932') as f:
                reader = csv.reader(f)
                next(reader)

                for row in reader:
                    student_id, submission = row[2], row[3:8]
                    submission = [self.wakati_text(text) for text in submission]
                    # 漢字をひらがなに、カタカナをひらがなに、英語をすべて小文字に変換する
                    kks.setMode('J', 'H')  # 漢字をひらがなに統一
                    conv = kks.getConverter()
                    # 各要素に対して conv.do() を適用
                    submission = [conv.do(text) for text in submission]
                    submission = [jaconv.kata2hira(jaconv.z2h(
                        text.lower(), digit=True, ascii=True)) for text in submission]
                    submission = [re.sub(r'[^ぁ-ん]', '', text)
                                for text in submission]
                    if student_id not in submissions:
                        submissions[student_id] = []
                    submissions[student_id].append(
                        ''.join(sorted(' '.join(submission))))

        return submissions


    def detect_copied_submissions(self, submissions, threshold, search_keywords):
        vectorizer = TfidfVectorizer()

        all_submissions = [text for student_submissions in submissions.values()
                        for text in student_submissions]
        tfidf_matrix = vectorizer.fit_transform(all_submissions)
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

        copied_pairs = set()
        num_submissions = len(all_submissions)

        for i in range(num_submissions):
            for j in range(i + 1, num_submissions):
                if similarity_matrix[i][j] >= threshold:
                    if any(keyword in all_submissions[i] for keyword in search_keywords) or any(keyword in all_submissions[j] for keyword in search_keywords):
                        copied_pairs.add((i, j))
                        print(f"{i} <=> {j}")

        return copied_pairs, similarity_matrix, all_submissions

    def write_output_file(self, main_file_path, copied_pairs, similarity_matrix, all_submissions, output_file):
        output_file_path = os.path.splitext(output_file.name)[0] + ".csv"
        index_to_student_id = {}
        index_to_datetime = {}
        teacher = {}
        with open(main_file_path, encoding='cp932') as input_file:
            reader = csv.reader(input_file)

            # Skip the header
            next(reader)

            for i, row in enumerate(reader):
                student_id = row[2]
                index_to_student_id[i] = student_id
                datetime = row[0]
                index_to_datetime[i] = datetime
                s = str(student_id)[0:2]
                if (s == '21' or s == '22' or s == '23' or s == '27' or s == '29' or s == '31' or s == '36' or s == '37' or s == '38'):
                    teacher[i] = '森'
                else:
                    teacher[i] = '吉松'

        with open(main_file_path, encoding='cp932') as input_file, open(output_file_path, 'w', encoding='cp932', newline='') as output_file:

            reader = csv.reader(input_file)
            writer = csv.writer(output_file)

            next(reader)
            writer.writerow(["担当教員", "学籍番号", "1", "2", "3", "4", "5", " ", "コピペ群",
                            "コピペ率", "重複ワード", "参考情報", "回答日時", " ", "NGワード数", "NGワード一覧", "再履修"])

            # 学籍番号でソートするために、リストに変換し、インデックスを保持
            input_rows = list(enumerate(reader))
            input_rows.sort(key=lambda x: x[1][2])  # 学籍番号は各行の3番目の要素（インデックス2）

            for i, row in input_rows:
                copied_students = set()
                copied_similarities = set()
                copied_texts = set()
                copied_datetimes = set()
                for pair in copied_pairs:
                    if i in pair:
                        copied_index = pair[0] if pair[1] == i else pair[1]
                        if copied_index in index_to_student_id:
                            copied_students.add(
                                index_to_student_id[copied_index])
                            copied_datetimes.add(
                                index_to_datetime[copied_index])
                            similarity = similarity_matrix[i][copied_index]
                            if similarity < 1.0:
                                similarity_str = f"{similarity:.2%}"
                            else:
                                similarity_str = "100%"
                            copied_similarities.add(similarity_str)
                            copied_texts.add(all_submissions[copied_index])
                        else:
                            print(f"Invalid pair: ({i}, {copied_index})")
                # 以下の行で回答日時列と受付番号列を出力csvに出力しないようにする
                writer.writerow((teacher[i], row[2], *row[3:], " ", ", ".join(sorted(list(copied_students))),
                                ", ".join(sorted(list(copied_similarities))),
                                ", ".join(sorted(list(copied_texts))),
                                ", ".join(sorted(list(copied_datetimes)))))

    def run(self, main_file_path, threshold, search_keywords):
        main_directory = os.path.dirname(main_file_path)
        past_files = [os.path.join(main_directory, file) for file in os.listdir(main_directory) if file.endswith('.csv') and file != os.path.basename(main_file_path)]
        submissions = self.read_submissions(main_file_path, past_files)

        copied_pairs, similarity_matrix, all_submissions = self.detect_copied_submissions(
            submissions, threshold, search_keywords)
        output_path = os.path.join(main_directory, "result.csv")
        with open(output_path, 'w', encoding='cp932', newline='') as output_file:
            self.write_output_file(main_file_path, copied_pairs,
                                similarity_matrix, all_submissions, output_file)
        print(f"Results saved to {output_path}")
        return output_path


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("盗作チェッカー")
        self.geometry("500x300")

        self.threshold = tk.DoubleVar(value=0.8)
        self.search_keywords = tk.StringVar()
        self.file_path = tk.StringVar()

        self.create_widgets()


    def create_widgets(self):
        ttk.Label(self, text="ファイル：").grid(
            column=0, row=0, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(self, textvariable=self.file_path, width=30).grid(
            column=1, row=0, padx=10, pady=10)
        ttk.Button(self, text="参照", command=self.browse_file).grid(
            column=2, row=0, padx=10, pady=10)

        ttk.Label(self, text="類似度:").grid(
            column=0, row=1, padx=10, pady=10, sticky=tk.W)
        ttk.Scale(self, from_=0, to=1, orient=tk.HORIZONTAL, variable=self.threshold, length=200,
                command=self.update_threshold_label).grid(column=1, row=1, padx=10, pady=10)
        self.threshold_label = ttk.Label(
            self, text=f"{self.threshold.get():.2f}")
        self.threshold_label.grid(
            column=2, row=1,
            padx=10, pady=10, sticky=tk.W)

        ttk.Label(self, text="検索ワード:").grid(
            column=0, row=2, padx=10, pady=10, sticky=tk.W)
        ttk.Entry(self, textvariable=self.search_keywords, width=30).grid(
            column=1, row=2, padx=10, pady=10)

        ttk.Button(self, text="START", command=self.check_plagiarism).grid(
            column=1, row=3, padx=10, pady=20)

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            self.file_path.set(file_path)

    def check_plagiarism(self):
        file_path = self.file_path.get()
        threshold = self.threshold.get()
        search_keywords = self.search_keywords.get()

        if not file_path:
            showinfo("Error", "Please select a file.")
            return

        search_keywords_list = search_keywords.split(',')

        self.destroy()  # GUIのwindowを閉じる
        checker = PlagiarismChecker(threshold)
        output_path = checker.run(file_path, threshold, search_keywords_list)

        checker.print_elapsed_time()  # 経過時間を表示

        showinfo("Success", f"Results saved to {output_path}")

    def update_threshold_label(self, value):
        self.threshold_label.config(text=f"{float(value):.2f}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
