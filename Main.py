import heapq as hq
import operator
import re
import os
import pandas as pd
from openpyxl import load_workbook
from Classes import Term, mergeTwoTerm
from Classes import DocId
import math

dictionary = {}
verbs = None
arabicRoots = None
sameCharacters = None
convertDictionar = {}
allrows = []

# type => termString : Term(object)


def main():
    global dictionary
    xlsx = load_workbook('sample.xlsx')
    sheet = xlsx.active
    rows = sheet.rows
    setupVerbs()
    # headers = [cell.value for cell in next(rows)]
    headers = ['id', 'content', 'url']


    numberOfRows = 0

    for row in rows:
        data = {}
        for title, cell in zip(headers, row):
            data[title] = cell.value

        if data['id'] == None:
            break  # in some test collection files have null valuse in the end of file its check that
        allrows.append(data)
    # print(allrows)

    #     تا اینجای کار فقط فایل اکسل خوانده شده و در یک آرایه ریخته شده است
    for doc in allrows[1:]:
        newTermStrings = re.split('; |, |\*|\n| |-|\(|\)|،|\.|\?|:|»|«', doc['content'])
        for newTermString in newTermStrings:
            newTermString = matchingWords(newTermString)
            if newTermString in dictionary:
                # if already exist
                newTerm = dictionary[newTermString]
                newTerm.addNewPosting(doc['id'])
            else:
                # if not exist
                newTerm = Term(newTermString)
                newTerm.addNewPosting(doc['id'])
                dictionary[newTermString] = newTerm

    print(len(list(dictionary.keys())))
    print(list(dictionary.keys()))

    # در این بخش  کلمات پرتکرار را از بین می بریم
    # حال سورت می کنیم بر اساس بیشترین تکرار
    # دو راه در نظر گرفته شده
    # O(c * n) = O(n)
    # روش اول در تست ها بهتر جواب داد
    numberOfRemoves = 10
    removeTargets = []

    terms = list(dictionary.values())

    for i in range(numberOfRemoves):
        max = 0
        roundTarget = 0
        for j in range(len(terms)):
            if terms[j].count > max:
                max = terms[j].count
                roundTarget = j
        removeTargets.append(terms[roundTarget])
        terms.remove(terms[roundTarget])

    # print("deleted phrases")
    for x in removeTargets:
        # print(x.term + " : " + x.count.__str__())
        del dictionary[x.term]

    # second way to sort but its not good idea  O( n log n)
    # for i in range(len(terms)):
    #     for j in range(i):
    #         if terms[i].count < terms[j].count:
    #             temp = terms[i]
    #             terms[i] = terms[j]
    #             terms[j] = temp

    # for x in terms:
    #     print(x.term + " : "+ x.count.__str__())

    # برای بخش مرج دو پوستینگ لیست
    # print(list( dictionary["فدراسیون"].postings))
    # print(list( dictionary["طاهری"].postings))
    #
    # mergeInDictionary(dictionary["فدراسیون"],dictionary["طاهری"])
    #
    # print(list(dictionary["فدراسیون"].postings))

    print("search engine is ready" ,end="")
    searchedText = None
    while searchedText != 0:
        print("type query : ")
        searchedText = input()
        elements=re.split('; |, |\*|\n| |-|\(|\)|،|\.|\?|:|»|«', searchedText)




        tf_idf(elements)
        # if len(list(elements)) == 1:
        #     print("one word found ")
        #     searchOneWord(elements[0])
        # else:
        #     print("multiple word found ")
        #     searchMultipleWord(elements)




# def sortDictionary():
#     markdict = {"Tom": 67, "Tina": 54, "Akbar": 87, "Kane": 43, "Divya": 73}
#     l = len(dictionary)
#     for i in range(l - 1):
#         for j in range(i + 1, l):
#             if dictionary[i][1] > marklist[j][1]:
#                 t = marklist[i]
#                 marklist[i] = marklist[j]
#                 marklist[j] = t
#         sortdict = dict(marklist)
#         print(sortdict)


def searchOneWord(termString):
    termString = matchingWords(termString)
    if termString in dictionary:
        term = dictionary[termString]
        for index in term.postings.keys():
            print(allrows[index]['url'])
    else:
        return "not found :("


def searchMultipleWord(terms):
    acceptedTerms = []
    for term in terms:
        term = matchingWords(term)
        if term in dictionary:
            foundedTerm = dictionary[term]
            # add one temperory element to object for calc existence of the words
            foundedTerm.temperoryPostingsIndexes = list(foundedTerm.postings.keys())
            acceptedTerms.append(foundedTerm)
        else:
            print('not found' + term)

    # now we know what postings lists must be search

    results = {}
    while True:
        min = math.inf
        for acceptedTerm in acceptedTerms:
            if len(acceptedTerm.temperoryPostingsIndexes) != 0:
                if acceptedTerm.temperoryPostingsIndexes[0] < min:
                    min = acceptedTerm.temperoryPostingsIndexes[0]

        if min == math.inf:
            break

        # now we have min of indexes
        point = 0
        for acceptedTerm in acceptedTerms:
            if len(acceptedTerm.temperoryPostingsIndexes) != 0:
                if acceptedTerm.temperoryPostingsIndexes[0] == min:
                    del acceptedTerm.temperoryPostingsIndexes[0]
                    point += 1
        results[min] = point

    # now we sort final results for output
    sortedResults = {k: v for k, v in sorted(results.items(), key=lambda item: item[1], reverse=True)}

    for key in sortedResults.keys():
        print("" + key.__str__() + "  point : " + sortedResults[key].__str__()  + "  url : " + allrows[key]['url'])


def tf_idf(terms): # based on page 38 ch.6
    how_many_results = 15
    points = {}

    for term in terms:
        term = matchingWords(term)
        if term in dictionary:
            queryTerm_tfid = math.log10(1 + 1) * math.log10(len(allrows) / dictionary[term].Df)
            foundedTerm = dictionary[term]
            for posting in foundedTerm.postings:
                addedDocPoint = math.log10(1 + foundedTerm.postings[posting].inDocCount) * math.log10(len(allrows) / foundedTerm.Df)
                if posting in points:
                    points[posting] = (points[posting] + addedDocPoint) * queryTerm_tfid
                else:
                    points[posting] = addedDocPoint * queryTerm_tfid

            for doc_id in points:
                points[doc_id] = points[doc_id] / len(allrows[doc_id]['content'])

            # now we must heapify our data


        else:
            print('not found' + term)
         # in this part i want choose k best page
        tuple_points= list(points.items())
        reverse_tuples_points = []
        for t in tuple_points:
            reverse_tuples_points.append((t[1],t[0]))

        hq._heapify_max(reverse_tuples_points)

        for i in range(how_many_results):
            if len(reverse_tuples_points) == 0 :
                print("i cant find " + how_many_results.__str__() + "results for our search")
                break
            point = hq._heappop_max(reverse_tuples_points)
            print(point[0])
            print(point[1])


def mergeInDictionary(original, added):
    res = mergeTwoTerm(original, added)
    del dictionary[original.term]
    del dictionary[added.term]
    dictionary[original.term] = res


def setupVerbs():
    global verbs
    global arabicRoots
    global sameCharacters
    global convertDictionar
    verbs = [("رو", "رفت"), ("زن", "زد"), ("گوی", "گفت"), ("بین", "دید"), ("خور", "خرد"), ("گیر", "گرفت"),
             ("کن", "کرد"), ("شو", "شد"), ("شناس", "شناخت"), ("دان", "دانستن"), ("اور", "اورد"), ("بار", "بارید"),
             ("ده", "داد"), ("خواه", "خواست"), ("پرداز", "پرداخت"), ("", ""), ]
    arabicRoots = ["کتب", "رجع", "قبض", "رکب", "جعل", "حفظ", "غفر", "شهد", "علم", "نظر", "فعل", "جهل", "رفع", "وضع",
                   "کفر", "کذب", "رفع", "جهد", "کشف", "حمل", "ورد", "رمز"]
    sameCharacters = {"إ": "ا", "أ": "ا", "ك": "ک", "ئ": "ی", "آ": "ا", "َ": "", "ِ": "", "ُ": "" ,"ً":"","ٍ":"" , "ٌ":"" }

    for tup in verbs:
        # مضارع ها
        convertDictionar["می" + tup[0] + "م"] = tup[0]
        convertDictionar["می" + tup[0] + "ی"] = tup[0]
        convertDictionar["می" + tup[0] + "د"] = tup[0]
        convertDictionar["می" + tup[0] + "یم"] = tup[0]
        convertDictionar["می" + tup[0] + "ید"] = tup[0]
        convertDictionar["می" + tup[0] + "ند"] = tup[0]

        # ماضی استمراری
        convertDictionar["می" + tup[1] + "م"] = tup[0]
        convertDictionar["می" + tup[1] + "ی"] = tup[0]
        convertDictionar["می" + tup[1]] = tup[0]
        convertDictionar["می" + tup[1] + "یم"] = tup[0]
        convertDictionar["می" + tup[1] + "ید"] = tup[0]
        convertDictionar["می" + tup[1] + "ند"] = tup[0]

        # ماضی ساده
        convertDictionar[tup[1] + "م"] = tup[0]
        convertDictionar[tup[1] + "ی"] = tup[0]
        convertDictionar[tup[1]] = tup[0]
        convertDictionar[tup[1] + "یم"] = tup[0]
        convertDictionar[tup[1] + "ید"] = tup[0]
        convertDictionar[tup[1] + "ند"] = tup[0]

        # ماضی نقلی
        convertDictionar[tup[1] + "هام"] = tup[0]
        convertDictionar[tup[1] + "های"] = tup[0]
        convertDictionar[tup[1] + "هاست"] = tup[0]
        convertDictionar[tup[1] + "هیم"] = tup[0]
        convertDictionar[tup[1] + "هید"] = tup[0]
        convertDictionar[tup[1] + "هند"] = tup[0]

        # اینده
        convertDictionar["خواهم" + tup[1]] = tup[0]
        convertDictionar["خواهی" + tup[1]] = tup[0]
        convertDictionar["خواهد" + tup[1]] = tup[0]
        convertDictionar["خواهیم" + tup[1]] = tup[0]
        convertDictionar["خواهید" + tup[1]] = tup[0]
        convertDictionar["خواهند" + tup[1]] = tup[0]

    for verb in arabicRoots:
        if len(verb) != 3:
            print("فعل 3 حرفی در داده ها یافت شده که ممنوع است")
            continue

        # فعال به فاعل مثل جهال به جاهل
        input = verb[0] + verb[1] + "ا" + verb[2]
        res = verb[0] + "ا" + verb[1] + verb[2]
        convertDictionar[input] = res

        # علما به عالم
        input = verb[0] + verb[1] + verb[2] + "ا"
        convertDictionar[input] = res  # فاعل به دلیل اشتراک با قبلی دباره ساخته نشده

        # افعال به فعل مثل اوراد به ورد
        input = "ا" + verb[0] + verb[1] + "ا" + verb[2]
        res = verb[0] + verb[1] + verb[2]
        convertDictionar[input] = res

        # فعول به فعل مثل رموز رمز
        input = verb[0] + verb[1] + "و" + verb[2]
        convertDictionar[input] = res


def matchingWords(str):
    global sameCharacters
    # حذف ها به شرط وجود نیم اسپیس
    if str.endswith("‌ها"):
        str = str.replace("‌ها", "")
    # first remove half space
    str = str.replace("‌", '')

    # تغییر کارکتر های عربی به فارسی
    for char in sameCharacters.keys():
        str = str.replace(char, sameCharacters[char])

    # اگر کلمه بیشتر از 6 کاراکتر باشد صفت نیست زیرا از ماکسیمم صفت بر وزن افتعال هست که 6 حرفه
    if len(str) <= 6:
        # حذف تر و ترین
        if str.endswith("تر"):
            str = str[:-2]
        else:
            if str.endswith("ترین"):
                str = str[:-4]

    if str in convertDictionar:
        return convertDictionar[str]
    else:
        # اگر به اینجای کد برسیم یعین واژه ما فعل نیست
        return str


# def replaceSameCharacters(str):


def test4():
    marklist = {"Tom": 67, "Tina": 54, "Akbar": 87, "Kane": 43, "Divya": 73}
    l = len(marklist)
    for i in range(l - 1):
        for j in range(i + 1, l):
            if marklist[i][1] > marklist[j][1]:
                t = marklist[i]
                marklist[i] = marklist[j]
                marklist[j] = t
        sortdict = dict(marklist)
        print(sortdict)


def test5():
    str = "می‌رومترینتر"
    if str.endswith("تر"):
        str = str[:-2]
    print(str)
    if str.endswith("ترین"):
        str = str[:-4]
    print(str)
    # str = "می" + str + "م"
    str = str.replace("‌", '')
    print(str)
    v = "فعل"
    str = v[0] + v[1] + "ا" + v[2]
    print(str)
    print(str)


if __name__ == '__main__':
    main()
