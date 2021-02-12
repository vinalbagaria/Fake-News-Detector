from django.shortcuts import render
from newsbot.strainer import *
from newsbot.models import *
from newsbot.util import *
import pandas as pd
from django.http import HttpResponse
# Create your views here.

def dictBuilder(request):
    print("Loading dictionary...")
    cDict = loadCanonDict()

    qs_Examples = ArticleExample.objects.all()
    print("Examples: " + str(qs_Examples.count()))

    for ex in qs_Examples:
        cwords = ex.body_text.split()
        for cwrd in cwords:
            if(cwrd in cDict.keys()):
                print('.', end='', flush=True)
            else:
                print('X', end='', flush=True)
                nde = DictEntry(canonWord = cwrd)
                nde.save()
                cDict[cwrd] = nde.pk
    return HttpResponse('<h1>Done</h1>')

def someMoreData(request):
    cDict = loadCanonDict()

    fp = open(r'C:\Users\DELL\Downloads\Fake-News-Detector-master\Fake-News-Detector-master\words_alpha.txt','r')
    cwords = fp.readlines()
    count = 0
    for cwrd in cwords:
        if(cwrd in cDict.keys()):
            print('.', end='', flush=True)
        else:
            print('X', end='', flush=True)
            count += 1
            if count < 638:
                nde = DictEntry(canonWord = cwrd)
                nde.save()
                cDict[cwrd] = nde.pk
            else:
                break
    return HttpResponse('<h1>Done</h1>')

def moreArticles(request):
    ss = SoupStrainer()
    print("Initializing dictionary...")
    ss.init()

    def more_harvest_Politifact_data():
        print("Ready to harvest Politifact data.")
        input("[Enter to continue, Ctl+C to cancel]>>")
        print("Reading URLs file")
        df_csv = pd.read_csv(r"C:\Users\DELL\Downloads\Fake-News-Detector-master\Fake-News-Detector-master\newsbot\more_politifact_data.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
        for index, row in df_csv.iterrows():
            print("Attempting URL: " + row['news_url'])
            try:
                if(ss.loadAddress(row['news_url'])):
                    print("Loaded OK")

                    # some of this data loads 404 pages b/c it is a little old, some load login pages. I've found that
                    # ignoring anything under 500 characters is a decent strategy for weeding those out.
                    if(len(ss.extractText)>500):
                        ae = ArticleExample()
                        ae.body_text = ss.extractText
                        ae.origin_url = row['news_url']
                        ae.origin_source = 'politifact data'
                        ae.bias_score = 0 # Politifact data doesn't have this
                        ae.bias_class = 5 # on this 1 to 4 scale, 5 is 'no data'
                        ae.quality_score = row['score']
                        ae.quality_class = row['class']
                        ae.save()
                        print("Saved, napping for 1...")
                    else:
                        print("**** This URL produced insufficient data.")
                else:
                    print("**** Error on that URL ^^^^^")
            except:
                continue
        
    more_harvest_Politifact_data()
    return HttpResponse('<h1>Done</h1>')
    
def myView(request):
    ss = SoupStrainer()
    print("Initializing dictionary...")
    ss.init()

    def harvest_Politifact_data():
        print("Ready to harvest Politifact data.")
        input("[Enter to continue, Ctl+C to cancel]>>")
        print("Reading URLs file")
        df_csv = pd.read_csv(r"C:\Users\DELL\Downloads\Fake-News-Detector-master\Fake-News-Detector-master\newsbot\politifact_data.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
        for index, row in df_csv.iterrows():
            print("Attempting URL: " + row['news_url'])
            try:
                if(ss.loadAddress(row['news_url'])):
                    print("Loaded OK")

                    # some of this data loads 404 pages b/c it is a little old, some load login pages. I've found that
                    # ignoring anything under 500 characters is a decent strategy for weeding those out.
                    if(len(ss.extractText)>500):
                        ae = ArticleExample()
                        ae.body_text = ss.extractText
                        ae.origin_url = row['news_url']
                        ae.origin_source = 'politifact data'
                        ae.bias_score = 0 # Politifact data doesn't have this
                        ae.bias_class = 5 # on this 1 to 4 scale, 5 is 'no data'
                        ae.quality_score = row['score']
                        ae.quality_class = row['class']
                        ae.save()
                        print("Saved, napping for 1...")
                    else:
                        print("**** This URL produced insufficient data.")
                else:
                    print("**** Error on that URL ^^^^^")
            except:
                continue
        
        
    def harvest_MBC_data():
        print("Ready to harvest Media Bias Chart data.")
        input("[Enter to continue, Ctl+C to cancel]>>")
        print("Reading URLs file")
        df_csv = pd.read_csv(r"C:\Users\DELL\Downloads\Fake-News-Detector-master\Fake-News-Detector-master\newsbot\MediaBiasChartData.csv", error_bad_lines=False, quotechar='"', thousands=',', low_memory=False)
        for index, row in df_csv.iterrows():
            print("Attempting URL: " + row['Url'])
            try:
                if(ss.loadAddress(row['Url'])):
                    print("Loaded OK")
                    ae = ArticleExample()
                    ae.body_text = ss.extractText
                    ae.origin_url = row['Url']
                    ae.origin_source = row['Source']
                    ae.bias_score = row['Bias']
                    ae.quality_score = row['Quality']
                    ae.bias_class = 5
                    if(ae.quality_score <= 16.25):
                        ae.quality_class = 1
                    elif(ae.quality_score <= 32.50):
                        ae.quality_class = 2
                    elif(ae.quality_score <= 48.75):
                        ae.quality_class = 3
                    else:
                        ae.quality_class = 4
                    ae.save()
                    print("Saved, napping for 1...")
                else:
                    print("Error on that URL ^^^^^")
            except:
                continue
        

    #harvest_MBC_data()
    harvest_Politifact_data()