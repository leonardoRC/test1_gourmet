import json
from datetime import datetime, timedelta
from models import Sequences, Transactions
from difflib import SequenceMatcher

def import_json():
    """
        This code read the json and create transactions on database
            Test and create unique entries and group similars by diff
    """
    with open('transactions.json') as json_file:
        data = json.load(json_file)
        for t in data:
            Trans, created = Transactions.get_or_create(desc = t['description'],amount = t['amount'], date = t['date'], defaults={'pub': datetime.now()})

def look_similars():
    """
        look all transactions and group by  similar descriptions by diff
        and returns these groups in a data list
    """
    query = Transactions.select()
    groups = []
    for Trans in query:
        #print("grupos", groups)
        ratio = 0
        for g in groups:
            #print(" grupo", g)
            for tr in g:
                print(tr.desc)
                if SequenceMatcher(None, Trans.desc, tr.desc).ratio() >= 0.6:
                    #print(SequenceMatcher(None, Trans.desc,  tr.desc).ratio())
                    ratio =+ 1
                    g.append(Trans)
                    break
        if ratio <= 0:
            #print("Creating a new group" , Trans.desc)
            groups.append([Trans])
    return groups

def frequency(groups):
    """
     This part get the groups and aplly rules to detect time recorrence based on frequency
    :return:
     List with all Frequency gruped by
    """

    p_seq = []
    for e, g in enumerate(groups):
        temp = []
        while g:
            done = False
            for tmp in temp:
                for tp in tmp:
                    if g:
                        distance = datetime.strptime(tp.date, '%m/%d/%Y').day - datetime.strptime(g[0].date, '%m/%d/%Y').day
                        if distance >= -1 and distance <= 1:
                            tmp.append(g.pop(0))
                            done = True
            if done == False:
                if g:                               # because g can be poped before
                    temp.append([g.pop(0)])
        p_seq.append(temp)
    return p_seq

def sequences(p_seq):
    """
        #mounting suquences following the rules - All transactions in a set must be at least 4 days apart from each other.
    :return:
    """
    for pre in p_seq:
        for pr in pre:
                for i, p in enumerate(pr):
                    if i == 0:
                        pass
                    else:
                        diff = (datetime.strptime(p.date, '%m/%d/%Y')) - datetime.strptime(pr[i-1].date, '%m/%d/%Y')
                        if diff.days > 4:
                            print("previous:" , datetime.strptime(pr[i-1].date,'%m/%d/%Y'), "current:", datetime.strptime(p.date, '%m/%d/%Y'), "period", diff)
                        else:
                            del pr[i]
    print(" pre sequence", p_seq)
    return p_seq

def create_sequences(p_seq):
    """
        # analyzes the presequence and if it is a block with more than 4 it creates the entries in the databases and appointments in the transitions
    :param p_seq:
    :return:
    """
    for pre in p_seq:
        for pr in pre:
            if len(pr) >= 4:
                for i, p in enumerate(pr):
                    if i == 0:
                        seq, created = Sequences.get_or_create(desc = p.desc, defaults={'pub': datetime.now()})
                        p.sequence = seq
                        p.save()
                        print(p.desc, p.date, p.sequence)
                    else:
                        p.sequence = seq
                        p.save()
                        print(p.desc, p.date, p.sequence)
            else:
                print("\n\nSequence out", pr)
                for i, p in enumerate(pr):
                    p.sequence = None
                    p.save()
    return p_seq

if __name__ == "__main__":
    """
    Run this file will import all data on json file and create the sequences or insert in existing one
        *it is not necessary for a transaction to be part of a sequence*
    """
    import_json()
    groups =look_similars()
    p_seq = frequency(groups)
    p_seq = sequences(p_seq)
    p_seq = create_sequences(p_seq)