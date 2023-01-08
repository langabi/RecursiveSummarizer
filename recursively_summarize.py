import sys

import openai
import os
from time import time,sleep
import textwrap
import re
from pypdf import PdfReader


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


# get directory of the current file
dir_path = os.path.dirname(os.path.realpath(__file__))
# get api key from directory that this script is in
openai.api_key = open_file(dir_path + '/openaiapikey.txt')


def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.6, top_p=1.0, tokens=1000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open(dir_path + '/gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def pdf_extract(filename):
    # take the pdf referred with filename variable, and write input.txt with the text from the pdf, using PyPDF
    reader = PdfReader(filename + '.pdf')
    outfile = open(filename + '.txt', 'w')
    # iterate over each page
    for page in reader.pages:
        text = page.extract_text()
        outfile.write(text)


def summarise(text):
    # chunk into multiple character chunks, so that doesn't exceed 4000 tokens for davinci, with some leeway
    chunk_size = 8000
    sub_chunk_size = chunk_size / 8
    sub_chunks = textwrap.wrap(text, sub_chunk_size)
    # set chunks to be sets of slices, length 8, from sub_chunks, with one overlapping subchunk each time
    chunks = [" ".join(sub_chunks[i:i + 7]) for i in range(0, len(sub_chunks), 7)]
    result = list()
    count = 0
    for chunk in chunks:
        count = count + 1
        prompt = open_file(dir_path + '/prompt.txt').replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
        response = gpt3_completion(prompt)
        print('\n\n\n', count, 'of', len(chunks), ' - ', response)
        result.append(response)
    return result


if __name__ == '__main__':
    # check if there's a command line argument
    if len(sys.argv) > 1:
        # if there is, use it as the filename
        filename = sys.argv[1]
        if filename[-4:] == '.pdf':
            filename = filename[:-4]
        pdf_extract(filename)
    alltext = open_file(filename + '.txt')
    summary = summarise(alltext)
    save_file('\n\n'.join(summary), filename + '_long_summary.txt')
    if len(summary) > 1:
        summary2 = summarise('\n\n'.join(summary))
        save_file('\n\n'.join(summary2), filename + '_shorter_summary.txt')
        if len(summary2) > 1:
            summary3 = summarise('\n\n'.join(summary2))
            save_file('\n\n'.join(summary3), filename + '_shortest_summary.txt')
