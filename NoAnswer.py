import math
import time
import os
import urllib.request
import urllib.parse
import json

# constance
DEBUG = False
client_id = "네이버에서 직접 발급 받아야함"
client_secret = "마찬가지"
ranking = ["1st", "2nd", "3rd", "4th", "5th"]
special_words = ["~", "!", "@", "#", "$", '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '`', '[', ']', '{', '}',
                 '\\', '|', ';', ':', '\'', '\"', ',', '<', '.', '>', '/', '?']
global gcnt
gcnt = 1

# variables
global df_data, idf_data, tf_data, result, tf_idf_data
n = 100
df_data = {}
idf_data = {}
tf_data = {}
tf_idf_data = {}
result = {}


# functions
def strNormalizing(word):
    encText = urllib.parse.quote(word)
    url = "https://openapi.naver.com/v1/search/encyc?query=" + encText  # json 결과
    ret = ""
    try:
        time.sleep(0.11)
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read().decode('utf-8')
        else:
            return ""
        parse_body = json.loads(response_body)
        if parse_body["total"] == 0:
            return word
        check = parse_body["items"][0]["title"].split("b>")
        if len(check) < 3:
            return word
        ret = check[1].split("<")[0]
    except:
        time.sleep(0.11)
        print(word)
        ret = strNormalizing(word)
        pass
    finally:
        return ret


def sentenceNormalizing(content):
    if DEBUG:
        global gcnt
        print("Normalizing processing..", gcnt)
        gcnt += 1
    normalizing_content = " "
    for word in content.split():
        for i in special_words:
            if i in word:
                word = word.replace(i, "")
        if len(word) == 0:
            continue
        normalizing_content = normalizing_content + strNormalizing(word.strip()) + " "
    return normalizing_content


def calculating(input_doc):
    global tf_data, df_data
    index = input_doc[0]
    words = input_doc[1][1]

    # tf, df 값 구하기
    tf_adding_data = {}

    # get tf
    for i in words.split():
        cnt = tf_adding_data.get(i)
        if cnt is None:
            tf_adding_data[i] = 1
        else:
            tf_adding_data[i] = cnt + 1

    # store tf
    tf_data[index] = tf_adding_data
    # get and store df
    for i in tf_adding_data:
        cnt = df_data.get(i)
        if cnt is None:
            df_data[i] = 1
        else:
            df_data[i] = cnt + 1


def tf_idf_func(query):
    global tf_data, idf_data, tf_idf_data
    normalizing_query = sentenceNormalizing(query).strip()
    if DEBUG:
        print(normalizing_query)
    """
    1. 쿼리와 문서의 일치하는 단어를 찾는다.
    2. 일치하는 단어의 tf를 weight값으로 바꾼다.
    3. 해당 값을 idf와 곱한다.
    4. 그 값을 (index : value)형태로 tf_idf_data에 반영한다.
    """
    # 문서마다
    for index, dict_words in tf_data.items():
        w = 0
        # 단어마다
        for word, cnt in dict_words.items():
            # 모든 쿼리 단어
            for normalizing_word in normalizing_query.split():
                # 1. 찾았다!
                if normalizing_word == word:
                    # 2. 바꾼다.
                    tf_w = 1 + math.log(cnt)
                    idf_value = idf_data.get(word)
                    w += (tf_w * idf_value)
        tf_idf_data[index] = w


"""
============================================================
=             Information Retrieval assignment             =
=           KNU Computer Science and Engineering           =
=                 2020114732 Choi Jun Ho                   =
============================================================
"""
# input query
q = input("Enter the query : ")

# 실행 시간 체크
start = time.time()

# 파일을 열기
dict_json = "./dictionary.json"
f = None
if os.path.exists(dict_json) is False:
    f = open("./full_corpus.txt", "r", encoding="utf-8")

    # 사전 작업
    body = ""
    name = ""
    dict_save = {}
    index = -1
    while True:
        line = f.readline()
        if not line:
            dict_save[index] = (name, sentenceNormalizing(body))
            break
        words = line.split(">")
        if words[0] == "<title":
            if index != -1:
                dict_save[index] = (name, sentenceNormalizing(body))
            title = words[1].split("<")[0].split(".")
            index = title[0]
            name = title[1].lstrip()
            body = ""
            continue
        body += line
    json.dump(dict_save, open("./dictionary.json", "w", encoding="utf-8"))
    f.close()

f = open(dict_json, "r", encoding="utf-8")
data = json.load(open(dict_json, "r", encoding="utf-8"))
f.close()

for i in data.items():
    calculating(i)

for i in range(1, 100):
    result[str(i)] = 0

# idf 계산
for i, j in df_data.items():
    idf_data[i] = math.log(n / (1 + j))

# calculating
tf_idf_func(q)

# tf - idf 결과 출력
if DEBUG:
    print(tf_data)
    print(df_data)
    print(idf_data)
    print(tf_idf_data)

tup = []
for i, j in tf_idf_data.items():
    tup.append((int(i), j))
tup.sort(key=lambda x: (-x[1], x[0]))

# print result
print("Rank : index - title ( value )")
for i in range(5):
    if tup[i][1] == 0:
        print(ranking[i], ": No related Document.")
    else:
        print(ranking[i], ":", tup[i][0], "-", data[str(tup[i][0])][0], "(", tup[i][1], ")")

# 종료 시간 체크
print("Time :", time.time() - start)
