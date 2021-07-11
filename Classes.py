import math

class Term:
    def __init__(self, term):
        self.term = term
        self.postings = {}
        self.count = 0
        self.Df = 0

    def addNewPosting(self, id):  # also it must call after initation of the class to add first term in postings list
        self.count +=1
        if id in self.postings:
            self.postings[id].increaseCount()
        else:
            self.Df += 1
            self.postings[id] = DocId(id)
    def addPostingsInMerge(self, id , count):#just for merge state
        if id in self.postings:
            print("id repeated something is wrong")
        else:
            newDocId = DocId(id)
            newDocId.inDocCount = count
            self.postings[id] = newDocId


def mergeTwoTerm(original , added ):
    newTerm = Term(original.term)
    newTerm.count = original.count + added.count

    originalListIndex = list(original.postings.keys())
    secondListIndex = list(added.postings.keys())

    while len(originalListIndex) !=0 or len(secondListIndex)!=0:
        if len(originalListIndex) == 0 :
            newTerm.addPostingsInMerge(secondListIndex[0], added.postings[secondListIndex[0]].inDocCount)
            del secondListIndex[0]
            continue

        if len(secondListIndex) == 0 :
            newTerm.addPostingsInMerge(originalListIndex[0], original.postings[originalListIndex[0]].inDocCount)
            del originalListIndex[0]
            continue

        if originalListIndex[0] == secondListIndex[0]:
            newTerm.addPostingsInMerge(originalListIndex[0] , original.postings[originalListIndex[0]].inDocCount + added.postings[originalListIndex[0]].inDocCount)
            del originalListIndex[0]
            del secondListIndex[0]
        elif originalListIndex[0] < secondListIndex[0] :
            newTerm.addPostingsInMerge(originalListIndex[0],original.postings[originalListIndex[0]].inDocCount)
            del originalListIndex[0]
        elif originalListIndex[0] > secondListIndex[0]:
            newTerm.addPostingsInMerge(secondListIndex[0], added.postings[secondListIndex[0]].inDocCount)
            del secondListIndex[0]

    return newTerm


class DocId:
    def __init__(self, id):
        self.id = id
        self.inDocCount = 1

    def increaseCount(self):
        self.inDocCount += 1
