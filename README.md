# words-in-context
A script intended to produce Anki flashcards based on easily marked-up plain text

This is a script I created for personal use--and is the first I've ever coded 
in Python; please excuse flaws in code quality and non-idiomatic work.
Although I want to keep it relatively maintainable, Python is a new 
language to me, and this is a project where for the moment, "good enough"
is the quality standard applied.

Several other projects that, in their own ways, have gone far beyond this
one, include ReadLang (http://www.readlang.com) and Learning With Texts
(http://lwt.sourceforge.net/; 
http://www.fluentin3months.com/learning-with-texts/ ). Check them out;
they might meet your needs better than this script. ReadLang has a laudable
vision of being a "one-stop shop", a database where your knowledge of
words gets shared across different language-learning platforms; I hope
I can integrate with that database at some point.

Possible future evolution includes:
* Direct integration into Anki (which does, after all, use Python-based 
extensions)
* A reading interface, probably Web-based, to make markup even easier.

See the comment at the start of the script for usage.  Note that output
is currently hardcoded to "c:\\temp\\foranki\\FlashcardsOutput.txt";
you will presumably wish to change this path. Also note that as of
the project's creation, it mostly assumes a first language of English
and that Bangla is the language being learned--because this is my situation.