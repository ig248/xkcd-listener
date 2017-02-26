#!/usr/bin/env python2

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
import xkcd
import webbrowser
import pandas as pd

## Update database of xkcd comics
# retrieve latest comic
try:
    last = xkcd.getLatestComic()
    nmax = last.number
except:
    nmax = 0

# Load databas from CSV    
try:
    df = pd.DataFrame.from_csv('xkcd.csv')
except:
    df = pd.DataFrame(columns=['title', 'alt'])
    df.index.name = 'n'

# Try to download missing/new comics
new = False
for n in xrange(1,nmax):
    print '\r', n,
    if n not in df.index:
        try:
            comic = xkcd.Comic(n)
            df.loc[n] = [comic.title, comic.altText]
            new = True
        except:
            print 'Failed to import #%d' % n

# Save new data to CSV
if new:
    df.to_csv('xkcd.csv', encoding='utf-8')
     
def score(row, query=()):
    """scoring function to be applied to DF row"""
    query = [q.lower() for q in query]
    try:
        title_matches = [w for w in row.title.lower().split() if w in query]
    except:
        title_matches = []
    try:
        alt_matches = [w for w in row.alt.lower().split() if w in query]
    except:
        alt_matches = []
    return 2*len(title_matches) + len(alt_matches)

# obtain audio from the microphone
r = sr.Recognizer()
text = None

while True:  # while text not in ["exit", "quit", "stop"]:

    print "== Listening... =="

    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    # recognize speech using Google Speech Recognition
    print "-- Recognizing... --"
    
    text = None
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio,            key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        text = r.recognize_google(audio)
        print("Google Speech Recognition thinks you said \"%s\"" % text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    
    if text:
        # Find matching xkcd
        query = text.lower().split()
        query = [q for q in query if len(q) > 3]
        scores = df.apply(score, axis =1, query=query)
        n = scores.idxmax()
        if scores[n]:
            print 'Found matching XKCD #%d' % n
            webbrowser.open('https://www.xkcd.com/%d/' % n)
        else:
            print 'Found no matching XKCD'
