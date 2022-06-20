import os
import sys
import requests
import bs4
import urllib

PICTURE_BASE_TEX = """
\\begin{wrapfigure}{O}{\\figwidth}
	\\begin{center}
		\\includegraphics[width=\\figwidth]{pic}
	\\end{center}
\\end{wrapfigure}
"""

def link_to_soup(link):
    page = requests.get(link)
    soup = bs4.BeautifulSoup(page.content, 'lxml')
    return soup

def print_soup(soup):
    pretty_html = soup.prettify()
    print(pretty_html)

if len(sys.argv) < 3:
    print('Need link to chapter and chapter number!')
    exit()

def prepare_text(text):
    _t = ''
    for t in text.contents:
        if type(t) == bs4.element.NavigableString: # normal text
            _t += t.replace('.” ', '”. \n').replace('. ', '. \n').replace('? ', '? \n').replace('! ', '! \n').replace('; ', '; \n').replace(': ', ': \n')
        else: # probably greentext
            _t += '\greentext{' + t.string + '}\n'
    return _t.replace('&', '\&').replace('#', '\#')

def extract_picture(dip, large=False):
    """ <img src="images/ship/2.png"/> """
    point = 'href' if large else 'src'
    if dip[point].endswith('html'): # workaround for misplaced footers
        return ''
    pic_link = "/".join(link.split('/')[:-1]) + '/' + dip[point]
    pic_link = pic_link.replace(' ', '%20')
    local_pic_file = 'pics/' + chap_number + '/' + dip[point].split('/')[-1]
    if not os.path.isfile(local_pic_file):
        urllib.request.urlretrieve(pic_link, local_pic_file)
    return PICTURE_BASE_TEX.replace('pic', local_pic_file)

link = sys.argv[1]
chap_number = sys.argv[2]
main_soup = link_to_soup(link)
chapter_name = main_soup.find('title').contents[0]

if not os.path.exists('pics/' + chap_number):
    os.mkdir('pics/' + chap_number)

main_body = main_soup.find(attrs={"class": "wrapper"})
#print_soup(main_body)

main_tex_text = '\\chapter{' + chapter_name + '}\n'

for subsection in main_body.contents:
    if type(subsection) == bs4.element.NavigableString:
        continue
    if subsection.find_all('a'):
        main_tex_text += extract_picture(subsection.a, large=True)
    else:
        main_tex_text += extract_picture(subsection.img)
    main_tex_text += prepare_text(subsection.p)

chap_number = int(chap_number)
with open(f'TeX_files/chapter{chap_number:02d}.tex', 'w') as f:
    f.write(main_tex_text)






