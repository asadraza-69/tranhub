import json
import re
import codecs
import time
import math


def newPhrase():
    return {'start_time': '', 'end_time': '', 'words': []}


# Format and return a string that contains the converted number of seconds into SRT format
def getTimeCode(seconds):
    (frac, whole) = math.modf(seconds)
    frac = frac * 1000
    return str('%s,%03d' % (time.strftime('%H:%M:%S', time.gmtime(whole)), frac))


def writeTranscriptToSRT(transcript, sourceLangCode, srtFileName):
    # Write the SRT file for the original language
    print("==> Creating SRT from transcript")
    phrases = getPhrasesFromTranscript(transcript)
    writeSRT(phrases, srtFileName)


# ==================================================================================
# Function: getPhrasesFromTranscript
# Purpose: Based on the JSON transcript provided by Amazon Transcribe, get the phrases from the translation
#          and write it out to an SRT file
# Parameters:
#                 transcript - the JSON output from Amazon Transcribe
# ==================================================================================
def getPhrasesFromTranscript(transcript):
    # This function is intended to be called with the JSON structure output from the Transcribe service.  However,
    # if you only have the translation of the transcript, then you should call getPhrasesFromTranslation instead

    # Now create phrases from the translation
    ts = json.loads(transcript)
    items = ts['results']['items']
    # print( items )

    # set up some variables for the first pass
    phrase = newPhrase()
    phrases = []
    nPhrase = True
    x = 0
    c = 0
    lastEndTime = ""

    print("==> Creating phrases from transcript...")

    for item in items:

        # if it is a new phrase, then get the start_time of the first item
        if nPhrase == True:
            if item["type"] == "pronunciation":
                phrase["start_time"] = getTimeCode(float(item["start_time"]))
                nPhrase = False
                lastEndTime = getTimeCode(float(item["end_time"]))
            c += 1
        else:
            # get the end_time if the item is a pronuciation and store it
            # We need to determine if this pronunciation or puncuation here
            # Punctuation doesn't contain timing information, so we'll want
            # to set the end_time to whatever the last word in the phrase is.
            if item["type"] == "pronunciation":
                phrase["end_time"] = getTimeCode(float(item["end_time"]))

        # in either case, append the word to the phrase...
        phrase["words"].append(item['alternatives'][0]["content"])
        x += 1

        # now add the phrase to the phrases, generate a new phrase, etc.
        if x == 10:
            # print c, phrase
            phrases.append(phrase)
            phrase = newPhrase()
            nPhrase = True
            x = 0

    # if there are any words in the final phrase add to phrases
    if (len(phrase["words"]) > 0):
        if phrase['end_time'] == '':
            phrase['end_time'] = lastEndTime
        phrases.append(phrase)

    return phrases


# ==================================================================================
# Function: writeSRT
# Purpose: Iterate through the phrases and write them to the SRT file
# Parameters:
#                 phrases - the array of JSON tuples containing the phrases to show up as subtitles
#                 filename - the name of the SRT output file (e.g. "mySRT.srt")
# ==================================================================================
def writeSRT(phrases, filename):
    print("==> Writing phrases to disk...")

    # open the files
    e = codecs.open(filename, "w+", "utf-8")
    x = 1

    for phrase in phrases:
        # determine how many words are in the phrase
        length = len(phrase["words"])

        # write out the phrase number
        e.write(str(x) + "\n")
        x += 1

        # write out the start and end time
        e.write(phrase["start_time"] + " --> " + phrase["end_time"] + "\n")

        # write out the full phase.  Use spacing if it is a word, or punctuation without spacing
        out = getPhraseText(phrase)

        # write out the srt file
        e.write(out + "\n\n")

    # print out

    e.close()


# ==================================================================================
# Function: getPhraseText
# Purpose: For a given phrase, return the string of words including punctuation
# Parameters:
#                 phrase - the array of JSON tuples containing the words to show up as subtitles
# ==================================================================================

def getPhraseText(phrase):
    length = len(phrase["words"])

    out = ""
    for i in range(0, length):
        if re.match('[a-zA-Z0-9]', phrase["words"][i]):
            if i > 0:
                out += " " + phrase["words"][i]
            else:
                out += phrase["words"][i]
        else:
            out += phrase["words"][i]

    return out









