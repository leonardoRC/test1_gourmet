import json
from datetime import datetime, timedelta
from models import Sequences, Transactions
from difflib import SequenceMatcher

def import_json():
    """
        This code read the json and create transactions on database
    """
    with open('transactions.json') as json_file:
        data = json.load(json_file)
        for t in data:
            Trans, created = Transactions.get_or_create(desc = t['description'],amount = t['amount'], date = t['date'], defaults={'pub': datetime.now()})

def look_similars():
    """
        looks all transactions and group by  similar descriptions using diff
        :return:
           returns groups of similarity in a data list
    """
    query = Transactions.select()
    groups = []
    for Trans in query:
        #print("grupos", groups)
        ratio = 0
        for g in groups:
            for tr in g:
                print(tr.desc)
                if SequenceMatcher(None, Trans.desc, tr.desc).ratio() >= 0.6:
                    ratio =+ 1
                    g.append(Trans)
                    break
        if ratio <= 0:
            #print("Creating a new group" , Trans.desc)
            groups.append([Trans])
    return groups

def frequency(groups):
    """
     This part gets the groups and applies rules to detect time recurrence based on the frequency
        margin of error can be changed here for greater or lesser accuracy
    :return:
     List with all Frequency grouped by
    """

    p_seq = []
    for e,g in enumerate(groups):
        #grupos aqui
        temp = []
        while g:
            done = False
            for tmp in temp:
                if tmp[0]:
                    distance = datetime.strptime(tmp[0].date, '%m/%d/%Y').day - datetime.strptime(g[0].date, '%m/%d/%Y').day
                    if distance >= -3 and distance <= 3:
                        diff = (datetime.strptime(g[0].date, '%m/%d/%Y')) - datetime.strptime(tmp[-1].date, '%m/%d/%Y')
                        if diff.days > 4:
                            tmp.append(g.pop(0))        #that poart add in the current sequence
                            done = True
                            break
            if done == False:
                temp.append([g.pop(0)])                 # that creates a new sequence inside temporary
        p_seq.append(temp)
    print("pre sequence", p_seq)
    print("grupost", groups)
    return p_seq

def create_sequences(p_seq):
    """
        analyzes the pre sequence and if it is a block with more than 4 it creates the entries on the database
        and appointments in the transitions also remake  if it changed
    :return:
        returns the list off sequences with all transactions changed
    """
    for pre in p_seq:
        for temp in pre:
            if len(temp) >= 4:
                seq = Sequences.create(desc = temp[0].desc, pub = datetime.now())
                seq.save()
                for i, p in enumerate(temp):
                        p.sequence = seq
                        p.save()
                        print(p.desc, p.date, p.sequence)
            else:
                print("\n\nSequence out", temp)
                for i, p in enumerate(temp):
                    p.sequence = None
                    p.save()
    return p_seq

if __name__ == "__main__":
    """
    Run this file will import all data on json file and create the sequences or insert in existing one
        *it is not necessary for a transaction to be part of a sequence*
    """
    import_json()
    groups = look_similars()
    p_seq = frequency(groups)
    p_seq = create_sequences(p_seq)