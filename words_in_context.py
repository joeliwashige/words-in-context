# -*- coding: utf-8 -*-
"""
This is a script to make it easy to create flashcards for Bangla,
showing words in context. It processes text files with simple markup,
from them creating tab-delimited files to import into Anki. To create 
a card for a word, just enclose it in angle brackets, then add a pipe 
and the word's definition.

E.g., if you want to define the word "novel", you'd mark up your text file thus:
"Little Women" is a <novel|a kind of book> by Louisa May Alcott.
We'd then create two flash cards. One would have this on the front:
    "Little Women" is a [a kind of book] by Louisa May Alcott.
with the full sentence on the back: 
    "Little Women" is a [novel] by Louisa May Alcott.
    
We'd also have the reverse card, for understanding "novel":
    "Little Women" is a [novel] by Louisa May Alcott.
and on the back, the same sentence, with the definition:
    "Little Women" is a [novel] by Louisa May Alcott.
                   a kind of book
                   
And, if you're feeling really ambitious, you can add various other
properties to your <>-enclosed term:
    |L2=phrase in L2, e.g., Bangla, defining the word
    |Tags=additional tags you want associated with this term.
          Those tags will be combined (with a space) with any
          active tags specified via <TAGS:mytag> .
    |Part=part of speech
    |Note=any note, presumably containing neither '|' nor '>'. 

An example, in Bangla:
    <গুপ্তহত্যা|assassination> ও <নিখোঁজের|of disappearance> মামলাগুলোর তদন্তে কোনো 
    <অগ্রগতি|progress> নেই। কোনোটিরই <রহস্যভেদ|revealed|L2=তথ্য আবিষ্কার বা উদ্ঘাটন, 
    মর্ম উপলব্ধি বা অবধারণ।|Part=mypartofspeech|note=unable to get this meaning
   pinned down exactly|tags=newspaper crime> হয়নি।
    
Note the treatment of রহস্যভেদ. It's <রহস্যভেদ|english_def|def_in_bangla>. 
Depending on your flashcards, you can make use of this. You could even
completely eliminate the English definition, and have two pipes
in a row to get you straight to BN->BN: <রহস্যভেদ||def_in_bangla>
                   
You can also include several keywords in your text, to specify
the source, source section, source paragraph, or source page for
text, or to add tags that you'd like to have associated with
the card. Each keyword continues in effect until the next one of
its kind is encountered. Keywords are strictly optional. The
text may also include comments, in the format <!--your comment-->
(though we don't enforce the -- before the >).

Thus, an input text file might look like:
    <SOURCE:Little Women Book Report>
    <FILETAGS:alcottbook>
    <PAGE:0001>
    <SECTION:INTRODUCTION>
    <PARAGRAPH:0001>
    <TAGS:essays literature apr2015>
    <!--this comment is ignored.-->
    "Little Women" is a <novel|a kind of book> by Louisa May Alcott.
    ....
    <PARAGRAPH:0002>
    I read this book <long|late in time> into the night. It caught my
    imagination...

Note that a SOURCE tag closes out all open tags, and a 
SECTION tag closes out any open PARAGRAPH tags.
    
"""

import codecs
import hashlib
import string
import sys

class TextFragment(object):
    def __init__(self):
        self.type = u"unset"
        self.text = u""
        self.definition = u""
        
    # Returns the source string with this token popped.
    def load(self, from_text):
    
        def starts_with_keyword(text_to_check, keyword_to_check):
            if len(text_to_check) < len(keyword_to_check):
                return False
            if text_to_check[:len(keyword_to_check)].upper() == keyword_to_check:
                return True
            return False
            
        def is_punctuation(text):
            return text in string.punctuation# or text in "ঃ।"
            
        source_keyword = "<SOURCE:"
        section_keyword = "<SECTION:"
        paragraph_keyword = "<PARAGRAPH:"
        page_keyword = "<PAGE:"
        file_tags_keyword = "<FILETAGS:"
        user_tags_keyword = "<TAGS:"
        comment_keyword = "<!--"
        flawed_comment_keyword = "<--"
        is_bracketed = False
        start_index = 0
        
        if starts_with_keyword(from_text, source_keyword):
            self.type = "source"
            is_bracketed = True
            start_index = len(source_keyword)
        elif starts_with_keyword(from_text, section_keyword):
            self.type = "section"
            is_bracketed = True
            start_index = len(section_keyword)
        elif starts_with_keyword(from_text, page_keyword):
            self.type = "page"
            is_bracketed = True
            start_index = len(page_keyword)
        elif starts_with_keyword(from_text, paragraph_keyword):
            self.type = "paragraph"
            is_bracketed = True
            start_index = len(paragraph_keyword)
        elif starts_with_keyword(from_text, file_tags_keyword):
            self.type = "file_tags"
            is_bracketed = True
            start_index = len(file_tags_keyword)
        elif starts_with_keyword(from_text, user_tags_keyword):
            self.type = "user_tags"
            is_bracketed = True
            start_index = len(user_tags_keyword)
        elif starts_with_keyword(from_text, comment_keyword):
            self.type = "comment"
            is_bracketed = True
            start_index = len(comment_keyword)    
        elif starts_with_keyword(from_text, flawed_comment_keyword):
            self.type = "comment"
            is_bracketed = True
            start_index = len(flawed_comment_keyword)    
        elif from_text[0] == "<":
            self.type = "defined_word"
            is_bracketed = True
            start_index = 1
        else:
            self.type = "word"
        
        if not is_bracketed and from_text[start_index].isspace():
            self.type = "whitespace"
            self.text = from_text[start_index]
            if start_index == len(from_text) - 1:
                return ""
            return from_text[start_index + 1:]
        elif not is_bracketed and is_punctuation(from_text[start_index]):
            self.type = "punctuation"
            self.text = from_text[start_index]
            if start_index == len(from_text) - 1:
                return ""
            return from_text[start_index + 1:]
        else:   
            cur_index = start_index + 1
            while cur_index < len(from_text):
                if is_bracketed:
                    if from_text[cur_index] == '>':
                        self.text = from_text[start_index:cur_index]
                        return from_text[cur_index + 1:]
                else:
                    if is_punctuation(from_text[cur_index]) or from_text[cur_index].isspace():
                        self.text = from_text[:cur_index]
                        return from_text[cur_index:]
                
                cur_index = cur_index + 1
            
            self.text = from_text[start_index:]            
            return "" 
    
    def base_text(self):
        if self.type == "defined_word":
            items = self.text.split('|')
            return items[0]
        elif self.is_tag():
            return ""
        return self.text

    def english_text(self):
        if self.type == "defined_word":
            items = self.text.split('|')
            if len(items) > 1:
                return items[1]
        elif self.type == "section" or self.type == "paragraph":
            return ""
        return self.text
        
    def bangla_definition(self):
        if self.type == "defined_word":
            items = self.text.split('|')
            text = ""
            if len(items) > 2:
                text = items[2]
            if len(text) > 3 and text[:3].upper() == "L2:":
                text = text[3:]
            return ""
        elif self.type == "section" or self.type == "paragraph":
            return ""
        return self.text
        
    def text_prop(self, property_name):
        items = []
        if self.type == "defined_word":
            items = self.text.split('|')
        for item in items:
            equals_pos = item.find('=')
            this_property = ""
            value = ""
            if (equals_pos != -1):
                this_property = item[:equals_pos]
                if len(item) > equals_pos + 1:
                    value = item[equals_pos + 1:]              
            if this_property.upper() == property_name.upper():
                return value
        return ""
        
    def is_word(self):
        return self.type == "word" or self.type == "defined_word"
        
    def is_tag(self):
        return self.type == "source" or self.type == "section" or \
        self.type == "page" or self.type == "paragraph" or \
        self.type == "user_tags" or self.type == "comment" or \
        self.type == "file_tags"
        
    def breaks_context(self):
        return self.type == "source" or self.type == "section" \
        or self.type == "paragraph" or self.type == "user_tags" or \
        self.type == "file_tags"
        
    def tag_text(self):
        if self.is_tag():
            return self.text
        return ""
        
    def __str__(self):
        s = u"type=%s, text='%s'" % (self.type, self.text)
        if self.type == "defined_word":
            s = s + u", base=%s, def=%s" % (self.base_text(), self.english_text())
        return s
            
class FileProcessor:
    desired_context_words = 20
    
    def __init__(self):
        self.text_window = []
        self.words_in_window = 0
        self.window_focus = -1
        self.active_tags = {}
        
    def process_file(self, input_name, output_name):
        self.output_file = codecs.open(output_name, u"w", u"utf-8")    
        self.input_file = codecs.open(sys.argv[1], u"r", u"utf-8")
        self.cur_input_line = self.input_file.readline()
        
        self.output_file.write("Hash\tBefore\tL2\tL1\t"
            "L2Def\tAfter\tSource\tSection\t"
            "Page\tPara\tPartOfSpeech\tNote\tFreq\tTags\n")
        
        while self.expand_window():
            # If we hit the start of something that "breaks context",
            # e.g., a source, section, or paragraph boundary, then
            # finish processing the window and close it before continuing.
            if (self.text_window[-1].breaks_context()):
                while (self.process_next_fragment()):
                    pass
                self.text_window = []
                self.window_focus = 0
                self.words_in_window = 0
                continue
                
            
            # Once we have at least enough for "context-after" words
            # following the first word, we start processing one token
            # for every token we read. If words are front-loaded, we
            # might start, and then pause until we have enough words
            # for "after" context again. The goal, though, is to get
            # enough words in the window for a "before" and an "after"
            # context.
            if self.words_in_window >= self.desired_context_words + 1:
                self.process_next_fragment()
            
            # If the last read resulted in the window being over-full,
            # move the window start just past the first word in the window.
            assert self.words_in_window <= (self.desired_context_words * 2) + 2          
            if self.words_in_window == (self.desired_context_words * 2) + 2:
                for index, fragment in enumerate(self.text_window):
                    if fragment.is_word():
                        new_start = index + 1
                        self.text_window = self.text_window[index + 1:]
                        self.window_focus = self.window_focus - new_start
                        self.words_in_window = self.words_in_window - 1
                        break
            
        # Process final entries. Now, we aren't expanding the window any
        # more; we're just reading through what's left of it.
        while (self.process_next_fragment()):
            pass
            
        self.output_file.close()
        self.input_file.close()
        del self.input_file
        del self.output_file
    
    def expand_window(self):
        fragment = TextFragment()
        self.cur_input_line = fragment.load(self.cur_input_line)
        if self.cur_input_line == u"":
            self.cur_input_line = self.input_file.readline()
        if fragment.is_word():
            self.words_in_window = self.words_in_window + 1
        self.text_window.append(fragment)
        return self.cur_input_line != u""
            
    def process_next_fragment(self):
        self.window_focus = self.window_focus + 1
        if self.window_focus == len(self.text_window):
            return False
        fragment = self.text_window[self.window_focus]
        if fragment.is_tag():
            if fragment.type == "source":
                # File tag is the only tag that persists.
                saved_file_tag = u""
                if self.active_tags["file_tags"]:
                    saved_file_tag = self.active_tags["file_tags"]
                self.active_tags = {}
                if saved_file_tag != "":
                    self.active_tags["file_tags"] = saved_file_tag
                    
            if fragment.type == "section":
                self.active_tags["paragraph"] = ""                
            self.active_tags[fragment.type] = fragment.tag_text()                            
        elif fragment.type == "defined_word":
            self.write_cur_defined_word()
        return True
            
        
    def write_cur_defined_word(self):
        def sanitize(text):
            return text.replace('\t', '').replace('\r', '').replace('\n', '').replace('\"', '&quot;')
            
        before_text = u""        
        for fragment in self.text_window[0 : self.window_focus]:
            before_text = before_text + fragment.base_text()
        before_text = sanitize(before_text.lstrip())
                
        focus_item = self.text_window[self.window_focus]
        this_bangla = sanitize(focus_item.base_text())
        this_english = sanitize(focus_item.english_text())
        this_bangla_def = sanitize(focus_item.bangla_definition())
        
        after_text = u""
        if self.window_focus < len(self.text_window) - 1:
            for fragment in self.text_window[self.window_focus + 1:]:            
                after_text = after_text + sanitize(fragment.base_text())
                    
        source = u""
        if "source" in self.active_tags:
            source = sanitize(self.active_tags["source"])
            
        section = u""
        if "section" in self.active_tags:
            section = sanitize(self.active_tags["section"])
            
        page = u""
        if "page" in self.active_tags:
            page = sanitize(self.active_tags["page"])
            
        paragraph = u""
        if "paragraph" in self.active_tags:
            paragraph = sanitize(self.active_tags["paragraph"])
            
        file_tags = u""
        if "file_tags" in self.active_tags:
            file_tags = sanitize(self.active_tags["file_tags"])
            
        user_tags = u""
        if "user_tags" in self.active_tags:
            user_tags = sanitize(self.active_tags["user_tags"])
            
        frequency = u"" # to be populated later
        
        this_lang2_def = sanitize(focus_item.text_prop("l2"))
        this_word_tags = sanitize(focus_item.text_prop("tags"))
        part_of_speech = sanitize(focus_item.text_prop("part"))
        note = sanitize(focus_item.text_prop("note"))
        
        if user_tags != u"" and this_word_tags != "":
            user_tags = user_tags + " "
        user_tags = user_tags + this_word_tags + " " + file_tags
        user_tags = sanitize(user_tags)
                        
        output_str = before_text + u"\t" + this_bangla + u"\t" + \
                     this_english + u"\t" + this_lang2_def + u"\t" + \
                     after_text + u"\t" + source + u"\t" + \
                     section + u"\t" + page + u"\t" + paragraph + \
                     u"\t" + part_of_speech + u"\t" + note + u"\t" + \
                     frequency + u"\t" + user_tags
        hash = hashlib.md5()
        hash.update(before_text.encode('utf-8'))
        hash.update('|')
        hash.update(this_bangla.encode('utf-8'))
        hash.update('|')
        hash.update(after_text.encode('utf-8'))
        self.output_file.write(hash.hexdigest() + u"\t" + output_str + u"\n")
        
    
def main():
    processor = FileProcessor()
    processor.process_file(sys.argv[1], "c:\\temp\\foranki\\FlashcardsOutput.txt")    

if __name__ == "__main__":
    mystr = "abc"
    str2 = mystr[3:]
    main()
            