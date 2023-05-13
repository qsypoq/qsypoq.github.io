#!/usr/bin/python

import markdown
import os
import errno
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree
from bs4 import BeautifulSoup
import readtime

### Clean old renders
os.system(f"rm -rf docs/*")
os.system(f"echo 'magnier.io' > docs/CNAME")

def check_exist(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def render_medias(folder, target_path):
    fromDirectory = f"sources/{folder}medias"
    toDirectory = f"docs/{target_path}medias"
    check_exist(toDirectory)
    copy_tree(fromDirectory, toDirectory)

def render_assets():
    fromDirectory = f"assets"
    toDirectory = f"docs/assets"
    check_exist(toDirectory)
    copy_tree(fromDirectory, toDirectory)

render_assets()

template_env = Environment(loader=FileSystemLoader(searchpath='./assets'))
template_home = template_env.get_template('home.html')
template_post = template_env.get_template('layout.html')
template_page = template_env.get_template('page.html')

md = markdown.Markdown(extensions=['fenced_code', 'meta', 'pymdownx.tilde'])

### Render Posts
POSTS = {}
for path in Path('sources/articles').rglob('*.md'):
    page = str(path)
    with open(page, 'r') as current_page:
        text = current_page.read()
        article = md.convert(text)

    if md.Meta:
        if md.Meta['draft'][0] == 'False':

            source = page.split("/", 1)
            target_path = page.split("/", 3)[3][:-8]
            folder = f"{source[1][:-8]}"
            target = f"docs/{target_path}/index.html"
            
            render_medias(folder, target_path)

            ### Insert extra meta
            intro = str(BeautifulSoup(article[0:250], features="html.parser").text).split("\n", 1)
            md.Meta['summary'] = intro[0]
            md.Meta['slug'] = target_path
            md.Meta['timeread'] = readtime.of_text(article).text
            POSTS[page] = md.Meta

            with open(f"{target}", 'w+') as x:
                x.write(template_post.render(
                    title=md.Meta['title'][0],
                    cover=md.Meta['cover'][0],
                    date=md.Meta['date'][0],
                    article=article
                ))

### Render Home
POSTS = {
    post: POSTS[post] for post in sorted(POSTS, key=lambda post: POSTS[post]['date'], reverse=True)
}
posts_metadata = [POSTS[post] for post in POSTS]

with open('docs/index.html', 'w+') as file:
    file.write(template_home.render(posts=posts_metadata))

### Render Pages
for path in Path('sources/pages').rglob('*.md'):
    page = str(path)
    with open(page, 'r') as current_page:
        text = current_page.read()
        article = md.convert(text)

    if md.Meta:
        if md.Meta['draft'][0] == 'False':
            source = page.split("/", 1)
            target_path = page.split("/", 2)[2][:-8]
            folder = f"{source[1][:-8]}"
            target = f"docs/{target_path}/index.html"

            render_medias(folder, target_path)

            with open(f"{target}", 'w') as x:
                x.write(template_page.render(
                    title=md.Meta['title'][0],
                    cover=md.Meta['cover'][0],
                    article=article
                ))
