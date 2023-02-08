# Recursive Summarizer

## DISCLAIMER: INFORMATIONAL AND EXPERIMENTATION PURPOSES ONLY

Any summarizations made with this code come with no warranty (see MIT license) and should not be used for financial, medical, legal, or any other critical applications.

## What is this?

Use OpenAI to summarise PDF documents of *any* length.

The tool converts the PDF to text, splits it into chunks, and summarises each chunk. That makes a "long" summary. Then, it applies the same approach to product a much shorter summary, by summarising the summary. The result is a useful (though not perfect) summary of the main themes in a PDF of any length.

## Using the script directly
Needs an OpenAI API key, which can be provided either with a file called `openai_api_key.txt` in the same directory as the script, or by setting the environment variable `OPENAI_API_KEY`.

Then, call `python3 recursive_summarizer.py <file> [<prompt>]` with the path to a PDF file as the first argument, and optionally the name of a prompt file as the second argument. Prompt files are in the /prompt/ folder, and are named after the type of prompt they use. Give the name of the prompt file without the .txt extension.

## Using the MacOS Finder shortcut

1. Right-click on "Summarise PDF" workflow, and select to open with Automator (NOT the installer)
2. Insert your OpenAI API key in the "Run Shell Script" step, as well as the full path to where this file is located
3. Save the workflow
4. Now, double click on the workflow, it will ask to install as a shortcut; agree.
5. Right click any PDF, and select "Summarise PDF" from the quick action context menu. It will take a few seconds to run, and will write txt files with the text and summary(s)

Thanks to https://github.com/daveshap/RecursiveSummarizer for the starting version of this package.
