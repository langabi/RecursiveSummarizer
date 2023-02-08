import sys
import openai
import os
from time import time, sleep
import textwrap
import re
from pypdf import PdfReader


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


# get api key from environment variable OPENAI_API_KEY, or if no such variable, then from file openaiapikey.txt in the directory that this script is in
openai.api_key = os.environ.get('OPENAI_API_KEY', open_file('openaiapikey.txt').strip())


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


def summarise(text, prompt_name):
    # chunk into multiple character chunks, so that doesn't exceed 4000 tokens for davinci, with some leeway
    chunk_size = 12000
    sub_chunk_size = chunk_size / 8
    sub_chunks = textwrap.wrap(text, sub_chunk_size)
    # set chunks to be sets of slices, length 8, from sub_chunks, with one overlapping subchunk each time
    chunks = [" ".join(sub_chunks[i:i + 7]) for i in range(0, len(sub_chunks), 7)]
    count = 0
    for chunk in chunks:
        count = count + 1
        prompt = open_file(os.path.dirname(os.path.realpath(__file__)) + '/prompts/' + prompt_name + '.txt').replace('<<SUMMARY>>', chunk)
        prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
        response = gpt3_completion(prompt)
        print('\n\n\n', count, 'of', len(chunks), ' - ', response)
        yield response


def summarise_pdf(filename, prompt, recurse):
    if filename[-4:] == '.pdf':
        filename = filename[:-4]
    pdf_extract(filename)
    alltext = open_file(filename + '.txt')
    if recurse is True:
        yield 'SUMMARY:'
    summary = list()
    for piece in summarise(alltext, prompt):
        yield piece
        summary.append(piece)
    save_file('\n\n'.join(summary), filename + '_long_summary.txt')
    if len(summary) > 1 and recurse is True:
        yield 'SHORTER SUMMARY:'
        summary2 = list()
        for piece in summarise('\n\n'.join(summary), prompt):
            yield piece
            summary2.append(piece)
        save_file('\n\n'.join(summary2), filename + '_shorter_summary.txt')
        if len(summary2) > 1:
            yield 'SHORTEST SUMMARY:'
            summary3 = list()
            for piece in summarise('\n\n'.join(summary2), prompt):
                yield piece
                summary3.append(piece)
            save_file('\n\n'.join(summary3), filename + '_shortest_summary.txt')


if __name__ == '__main__':
    # check if there's a command line argument
    if len(sys.argv) > 1:
        # if there is, use it as the filename
        if len(sys.argv) > 2:
            promptFile = sys.argv[2]
        else:
            promptFile = 'prompt'
        for piece in summarise_pdf(sys.argv[1], promptFile, True):
            continue
            # print(piece)
    else:
        # write usage instructions
        print('Usage: python3 recursively_summarize.py filename.pdf [prompt]')
        print('If no prompt is specified, the default prompt will be used. Prompt is the name of a file in the "prompts" directory, without the .txt extension.')

