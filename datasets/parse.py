import os
from bs4 import BeautifulSoup
from bs4 import Tag, NavigableString, BeautifulSoup
from tqdm import tqdm
import json
from pathlib import Path


def get_authors_from_html(fname: str):
    authors = []
    try:
        with open(fname) as fp:
            html_doc = fp.read()
            soup = BeautifulSoup(html_doc, 'html.parser')            
            l = soup.find_all("div", {"class": "poster"})
            for ll in l:
                author = ll.h4.text.strip()
                authors.append(author)
    except Exception as e:
        print(e)

    return authors

def get_comments_from_html(fname: str):
    comments = []
    whitelist_divs = ['b', 'strong', 'i', 'em', 'mark', 'small', 'del', 'ins', 'sub', 'sup', 'font']
    try:
        with open(fname) as fp:
            html_doc = fp.read()
            soup = BeautifulSoup(html_doc, 'html.parser')            
            divs = soup.find_all("div", {"class": "inner"})
            for div in divs:
                post_str = ""
                for div_el in div:
                    if isinstance(div_el, NavigableString):
                        stripped_str = div_el.strip()
                        if len(stripped_str) > 0:
                            post_str += stripped_str + ' '
                    # if smiley, add 'alt' string to text
                    elif isinstance(div_el, Tag):
                        #print(div_el.name, ": ", div_el.text)
                        if 'class' in div_el.attrs:
                            if div_el['class'][0] == 'smiley':
                                #print('smiley_div: ', div_el['alt'])
                                post_str += div_el['alt'] + ' '
                        elif div_el.name in whitelist_divs:
                            post_str += div_el.text.strip() + ' '
                comments.append(post_str)
                #print("================")
    except Exception as e:
        print(e)

    return comments
    
def get_comments_from_forums(forum_dir_path):
    # Returns a dictionary {author_name: [comment1, comment2, ...]}
    # path: path to root directory of forum
    # agora/silkroad1
    author_comment = {}

    print("rglobing")
    file_paths = list(Path(forum_dir_path).rglob("*topic*"))
    print("finished rglobing")
    count = 0
    for path in tqdm(file_paths):
        path_string = str(path)
        if os.path.isfile(path) and 'topic' in path_string and '.js' not in path_string:
            authors = get_authors_from_html(path_string)
            comments = get_comments_from_html(path_string)
            if len(authors) != len(comments):
                print(path_string, ': #a = ', len(authors), '#c = ', len(comments))
                continue
            for a,c in zip(authors, comments):
                if len(c) < 10:
                    continue
                if a in author_comment:
                    author_comment[a].append(c)
                else:
                    author_comment[a] = [c]
        
    return author_comment

    
if __name__ == '__main__':
    forum_paths = {
        'agora': '/darkweb/agora-forums',
        'silkroad1': '/darkweb/2013-11-03_topics'
    }
    FORUM_NAME = 'silkroad1'
    
    author_comments = get_comments_from_forums(forum_paths[FORUM_NAME])
    json.dump(
        author_comments,
        open('/darkweb/author_comments_%s.json' % (FORUM_NAME), 'w'),
        indent=2
    )
