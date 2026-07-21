import os
import argparse
import json
from pathlib import Path
#from urllib.parse import urlparse

from flask import Flask, request, render_template, jsonify, Response, render_template_string
from bs4 import BeautifulSoup
from jinja2 import Template

# Flask constructor
app = Flask(__name__)

# global vars
blog_json_path = Path.cwd() / ".." / "website" / "assets" / "data" / "blogs" / "blogs.json"
blog_json_path = blog_json_path.resolve(strict=False)
blog_html_dir = Path.cwd() / ".." / "website" / "blogs"
blog_html_dir = blog_html_dir.resolve(strict=False)
blog_domain = "https://dasxplore.com"

# classes
# blog json data
class BlogJson:
    def __init__(self, json_path:str=blog_json_path):
        self.blog_data = {}
        if os.path.exists(json_path):
            print(f"JSON path: {json_path}")
            self.json_path = json_path
            with open(self.json_path, "r") as jfile:
                self.blog_data = json.load(jfile)
        else:
            print(f"JSON path is not accessible: {json_path}")

    def get_blog_data(self, id:str):
        blog_params = {}
        for blog in self.blog_data["blogs"]:
            if blog["pageId"] == id:
                blog_params = blog
                break
        return blog_params

    def get_blog_ids(self):
        blog_ids = []
        for blog in self.blog_data["blogs"]:
            blog_ids.append(blog["pageId"])
        return blog_ids

    def get_keywords(self):
        return self.blog_data['keywords']

# from base template (uses jinja2)
class BlogHtml:
    def __init__(self, html_dir:str=blog_html_dir):
        self.html_dir = html_dir
        blog_html = ""
        with open(f'{self.html_dir}/templates/blog.html', 'r', encoding='utf-8') as file:
            blog_html = file.read()
        self.template = Template(blog_html)

    def add_blog(self, conent:dict):
        final_html = self.template.render(**conent)
        return final_html

# global objects
blogJsonObj = None
blogHtmlObj = None

# Get the blog html content from the existing blog
@app.route('/get-blog', methods=['POST'])
def get_blog_html():
    # variables
    head_desc = ""
    blog_title = ""
    canonical_href = ""
    meta_ogImg = ""
    meta_keywords = ""

    data = request.get_json()
    print(f"Received data: {data}") # debug
    blogId = data.get('id')
    blog = blogJsonObj.get_blog_data(blogId)
    cal = blog['cal']
    b_year = cal[3:7]
    b_month = cal[:2]
    blog_path = f"{blog_html_dir}/{b_year}/{b_month}/{blogId}/index.html"

    if not os.path.exists(blog_path):
        respJson = {
            "html": "none"
        }
        return jsonify(respJson)

    with open(blog_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    # Find the tag by id, then read the 'content' attribute
    meta_tag = soup.find(id="metaDesc")
    if meta_tag:
        head_desc = meta_tag['content']
    meta_tag = soup.find(id="blogTitle")
    if meta_tag:
        blog_title = meta_tag['content']
    meta_tag = soup.find(id="canonicalHref")
    if meta_tag:
        canonical_href = meta_tag['href']
    meta_tag = soup.find(id="metaOgImg")
    if meta_tag:
        meta_ogImg = meta_tag['content']
    meta_tag = soup.find(id="metaKeywords")
    if meta_tag:
        meta_keywords = meta_tag['content']

    # Get the blog content
    element = soup.find(id="blogContent")

    if element:
        inner_html = element.decode_contents()
        respJson = {
            "html": inner_html,
            "blog_title": blog_title,
            "head_desc": head_desc,
            "canonical_href": canonical_href,
            "og_img": meta_ogImg,
            "keywords": meta_keywords
        }
        return jsonify(respJson)
    return "blogContent Element not found", 404

# Update the blog
@app.route('/update-blog', methods=['POST'])
def update_blog_html():
    global blogHtmlObj

    # get the request data
    data = request.get_json()
    blogId = str(data.get('id'))
    blogContent = str(data.get('content'))
    blogContent = blogContent.strip()

    # get blog data from json
    blog = blogJsonObj.get_blog_data(blogId)
    cal = blog['cal']
    b_year = cal[3:7]
    b_month = cal[:2]

    # check if path exists
    blog_path = f"{blog_html_dir}/{b_year}/{b_month}/{blogId}/index.html"
    os.makedirs(f"{blog_html_dir}/{b_year}/{b_month}/{blogId}", exist_ok=True)

    # get the page related values from request
    pageTitle = str(data.get('title'))
    pageDesc = str(data.get('desc'))
    pagePath = str(data.get('path'))
    pageOgImg = str(data.get('ogimg'))
    pageKeywords = str(data.get('keywords'))
    pagefindVal = str(data.get('pagefind'))
    if pageTitle == "":
        pageTitle = blog['title']
    if pageDesc == "":
        pageDesc = blog['title']
    if pageOgImg == "":
        pageOgImg = blog['ogImage']
    if pageKeywords == "":
        pageKeywords = blogJsonObj.get_keywords()

    # The complete payload json for the jinja2 update
    blogPayload = {
        "blog_title": pageTitle,
        "head_desc": pageDesc,
        "og_img": pageOgImg,
        "blog_html": blogContent,
        "blog_domain": blog_domain,
        "blog_path": pagePath,
        "keywords": pageKeywords,
        "pagefind": pagefindVal
    }
    blog_template = blogHtmlObj.add_blog(blogPayload)
    with open(blog_path, 'w', encoding="utf-8") as output_file:
        output_file.write(blog_template)
    return jsonify({"stat": "ok"}), 200

# The main home page of the app
@app.route('/', methods =["GET"])
def home():
    global blogJsonObj
    blog_ids = []
    if blogJsonObj:
        blog_ids = blogJsonObj.get_blog_ids()
    return render_template("web.html", blog_ids=blog_ids)

# main function with args
def main():
    global blogJsonObj
    global blogHtmlObj
    global blog_json_path
    global blog_html_dir
    global blog_domain

    parser = argparse.ArgumentParser(description="Blog Maker app params")

    parser.add_argument(
        '--host', 
        type=str, 
        default='127.0.0.1',
        help='Host address to run the Flask app (default: 127.0.0.1)'
    )

    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Port number for the application (default: 5000)'
    )

    parser.add_argument(
        '--json', 
        type=str, 
        default="../website/assets/data/blogs/blogs.json",
        help='Blog json path (default: ../website/assets/data/blogs/blogs.json)'
    )

    parser.add_argument(
        '--html_dir', 
        type=str, 
        default="../website/blogs",
        help='Blog html main directory (default: ../website/blogs)'
    )

    parser.add_argument(
        '--domain', 
        type=str, 
        default="https://dasxplore.com",
        help='Blog domain without path (default: https://dasxplore.com)'
    )

    # For True/False flags
    parser.add_argument(
        '--debug', 
        action='store_true', # Defaults to False; becomes True if --debug is passed
        help='Enable Flask debug mode (default: False)'
    )

    # 3. Parse the arguments
    args = parser.parse_args()

    print(f"Starting server on http://{args.host}:{args.port}")
    print(f"Debug mode status: {args.debug}")

    blog_json_path = Path(args.json)
    blog_json_path = blog_json_path.resolve(strict=False)
    blog_html_dir = Path(args.html_dir)
    blog_html_dir = blog_html_dir.resolve(strict=False)
    print(f"JSON path: {blog_json_path}") # debug
    print(f"HTML dir: {blog_html_dir}") # debug
    blogJsonObj = BlogJson(blog_json_path)
    blogHtmlObj = BlogHtml(blog_html_dir)
    blog_domain = str(args.domain)

    app.run(
        port=args.port,
        host=args.host,
        debug=args.debug
    )

# When runs directly
if __name__ == '__main__':
    main()
