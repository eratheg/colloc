import re, sys
from collections import Counter
from tqdm import tqdm


### Variables
input_file = 'input.txt'
output_clean = 'output_clean.txt'
topList = 25
limitColocation = 1 

### Routine for stripping words from segment
def strip_list(list,np):
    try:
        keyword = [s for s in list if ">" in s ]
        keyword = str(keyword)
        keyword=keyword.strip('[')
        keyword=keyword.strip(']')
        keyword=keyword.strip("'")
        index = list.index(keyword)
        start = max(0, index - np)
        end = index + np + 1
        newlist = list[start:end]
        return newlist
    except ValueError:
        return []

### Main routine to process lines textfiles
def clean_file(input_file, output_clean):
### Initial cleanup, removing empty and irrelevant lines
    cleaned_lines = []
    word_list = []
    linesCount = 1
    file = open(input_file, "r")
    lines = file.readlines()
    new_lines = []
    for line in lines:
        if not re.match(r'^\s*$', line):
            if "KWIC" not in line.strip():
                new_lines.append(line)
    file.close()
    file = open(input_file, "w")
    file.writelines(new_lines)
    file.close()

### Open both input (cleaned from step above) and output files 
    with open(input_file, 'r') as file:
        lines = file.readlines()
        totalLines = sum(1 for _ in open(input_file))
    outFile = open(output_clean, 'w')

### Iterate over each line 
    for line in tqdm(lines, total=len(lines), unit='lines'):
        text = ("ORG(" + str(linesCount) + "):" + line.strip() + "\n")
        outFile.write(text)
        cleaned_line = line.replace('|', '').lstrip()
        cleaned_line = re.sub(r'\[[^[\]]*\]', '', cleaned_line)
        cleaned_line = re.sub(r'\([^()]*\)', '', cleaned_line)
        text = ("CLEAN_LINE: " + cleaned_line.strip() + "\n")
        outFile.write(text)

### Split each line into segments separated by '.', '!' or '?'
        segments = re.split(r'[.!?]', cleaned_line)
        segCount = 1

### Iterate over all segments (sentances).
        for segment in segments:
### If '<no>' detected (our targeted word, no other 'no' to be detected. Also remove any special characters in case we get a hit
            if '<no>' in segment or '<NO>' in segment or '<No>' in segment:
                words = segment.split()
                stopWords = [',', '@', '+', '-', '"', '„', ':', '“']
                for elem in list(words):
                    if elem in stopWords:
                        words.remove(elem)
                words2 = strip_list(words, limitColocation)
                text = ("SEGMENT[" + str(segCount) + "]: [YEY!!!] " + segment +  "  -->  " + str(words) + "  -->  " + str(words2) + "\n")
                outFile.write(text)
                word_list.extend(words2)
            else:
                text = ("SEGMENT[" + str(segCount) + "]: [OH NO!] " + segment.strip('\n') + " (looking for <no>|<No>|<NO>)\n")
                outFile.write(text)
            segCount += 1
        linesCount += 1
        outFile.write('\n')
### Presentation:
    print("Remaining elements: " + str(len(word_list)))
    outFile.write(text)
    word_counts = Counter(word_list)
    top_words = word_counts.most_common(topList)
    print("Total: " + str(totalLines))
    for word, count in top_words:
        print(f"{word}\t{count}")

### MAIN program starts here, checking first if parameters given ($1 is toplist, $2 is word width)
try:
    topList = sys.argv[1]
    topList = int(topList)
except IndexError:
    print("Top " + str(topList) + "will be considered")

try:
    limitColocation = sys.argv[2]
    limitColocation = int(limitColocation)
except IndexError:
    print("Will consider " + str(limitColocation) + " positions around 'no'")

clean_file(input_file, output_clean)
