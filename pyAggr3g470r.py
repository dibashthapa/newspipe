#! /usr/local/bin/python
#-*- coding: utf-8 -*-

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.8 $"
__date__ = "$Date: 2010/02/24 $"
__copyright__ = "Copyright (c) 2010 Cedric Bonhomme"
__license__ = "GPLv3"

import os
import sqlite3
import cherrypy
import ConfigParser

from cherrypy.lib.static import serve_file

import utils
import feedgetter

config = ConfigParser.RawConfigParser()
config.read("./cfg/pyAggr3g470r.cfg")
path = config.get('global','path')

bindhost = "0.0.0.0"

cherrypy.config.update({ 'server.socket_port': 12556, 'server.socket_host': bindhost})

path = {'/css/style.css': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/style.css'}, \
        '/css/img/delicious.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/img/delicious.png'}, \
        '/css/img/digg.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/img/digg.png'}, \
        '/css/img/reddit.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/img/reddit.png'}, \
        '/css/img/scoopeo.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/img/scoopeo.png'}, \
        '/css/img/blogmarks.png': {'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'css/img/blogmarks.png'}, \
        '/var/histogram.png':{'tools.staticfile.on': True, \
                'tools.staticfile.filename':path+'var/histogram.png'}}

htmlheader = """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
                lang="en">\n<head>\n<link rel="stylesheet" type="text/css" href="/css/style.css"
                />\n<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>\n
                <title>pyAggr3g470r - RSS Feed Reader</title> </head>"""

htmlfooter =  """<p>This software is under GPLv3 license. You are welcome to copy, modify or
                redistribute the source code according to the GPLv3 license.</p></div>\n
                </body>\n</html>"""

htmlnav = """<body>\n<h1><a name="top"><a href="/">pyAggr3g470r - RSS Feed Reader</a></a></h1>\n<a
href="http://bitbucket.org/cedricbonhomme/pyaggr3g470r/" rel="noreferrer" target="_blank">
pyAggr3g470r (source code)</a>
"""


class Root:
    def index(self):
        """
        Main page containing the list of feeds and articles.
        """
        self.dic, self.dic_info = utils.load_feed()
        html = htmlheader
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/fetch/">Fetch all feeds</a>\n<br />\n"""
        html += """<a href="/mark_as_read/All:">Mark all articles as read</a>\n<br />\n"""
        html += """<a href="/management/">Management of feed</a>\n"""
        html += """<form method=get action="/q/"><input type="text" name="querystring" value=""><input
        type="submit" value="Search"></form>\n"""
        html += "<hr />\n"
        html += """Your feeds (%s):<br />\n""" % len(self.dic.keys())
        for rss_feed_id in self.dic.keys():

            html += """<a href="/#%s">%s</a> (<a href="/unread/%s"
                    title="Unread article(s)">%s</a> / %s)<br />\n""" % \
                                (rss_feed_id.encode('utf-8'), \
                                self.dic[rss_feed_id][0][5].encode('utf-8'), \
                                rss_feed_id, self.dic_info[rss_feed_id][1], \
                                self.dic_info[rss_feed_id][0])

        html += """</div>\n<div class="left inner">\n"""

        for rss_feed_id in self.dic.keys():
            html += """<h2><a name="%s"><a href="%s" rel="noreferrer"
                    target="_blank">%s"</a></a>
                    <img src="%s" width="20" height="20" /></h2>\n""" % \
                        (rss_feed_id, self.dic[rss_feed_id][0][6].encode('utf-8'), \
                        self.dic[rss_feed_id][0][5].encode('utf-8'), \
                        self.dic_info[rss_feed_id][2].encode('utf-8'))

            # The main page display only 10 articles by feeds.
            for article in self.dic[rss_feed_id][:10]:

                if article[7] == "0":
                    # not readed articles are in bold
                    not_read_begin = "<b>"
                    not_read_end = "</b>"
                else:
                    not_read_begin = ""
                    not_read_end = ""

                html += article[1].encode('utf-8') + \
                        " - " + not_read_begin + \
                        """<a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                        not_read_end + \
                        "<br />\n"
            html += "<br />\n"

            html += """<a href="/all_articles/%s">All articles</a>""" % (rss_feed_id,)
            html += """ <a href="/mark_as_read/Feed_FromMainPage:%s">Mark all as read</a>""" % (rss_feed_id,)
            if self.dic_info[rss_feed_id][1] != 0:
                html += """ <a href="/unread/%s" title="Unread article(s)"
                        >Unread article(s) (%s)</a>""" % (rss_feed_id, \
                                        self.dic_info[rss_feed_id][1])
            html += """<h4><a href="/#top">Top</a></h4>"""
            html += "<hr />\n"
        html += htmlfooter
        return html

    index.exposed = True


    def management(self):
        """
        """
        self.dic, self.dic_info = utils.load_feed()
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">\n"""
        html += "<h1>Add Feeds</h1>\n"
        html += """<form method=get action="add_feed/"><input type="text" name="v" value="">\n<input
        type="submit" value="OK"></form>\n"""

        html += "<h1>Delete Feeds</h1>\n"
        html += """<form method=get action="del_feed/"><select name="feed_list">\n"""
        for feed_id in self.dic.keys():
            html += """\t<option value="%s">%s</option>\n""" % \
                    (feed_id, self.dic[feed_id][0][5].encode('utf-8'))
        html += """</select></form>\n"""

        html += "<hr />\n"

        html += """<p>The database contains a total of %s articles with
                %s unread articles.<br />""" % \
                    (sum([feed[0] for feed in self.dic_info.values()]),
                    sum([feed[1] for feed in self.dic_info.values()]))
        html += """Database: %s.\n<br />Size: %s bytes.</p>\n""" % \
                    (os.path.abspath("./var/feed.db"), os.path.getsize("./var/feed.db"))

        html += """<form method=get action="/fetch/">\n<input
        type="submit" value="Fetch all feeds"></form>\n"""
        html += """<form method=get action="add_feed/">\n<input
        type="submit" value="Delete all articles"></form>\n"""

        html += "<hr />\n"
        if self.dic:
            html += "<h1>Statistics</h1>\n"
            top_words = utils.top_words(self.dic, 10)

            html += "<table border=0>\n<tr><td>"
            html += "<ol>\n"
            for word, frequency in top_words:
                html += """\t<li><a href="/q/?querystring=%s">%s</a>: %s</li>\n""" % \
                                (word, word, frequency)
            html += "</ol>\n</td><td>"
            utils.create_histogram(top_words)
            html += """<img src="/var/histogram.png" /></td></tr></table>"""
            html += "<hr />\n"

        html += htmlfooter
        return html

    management.exposed = True


    def q(self, querystring=None):
        """
        Search for a feed. Simply search for the string 'querystring'
        in the description of the article.
        """
        param, _, value = querystring.partition(':')
        feed_id = None
        if param == "Feed":
            feed_id, _, querystring = value.partition(':')
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""

        html += """<h1>Articles containing the string <i>%s</i></h1><br />""" % (querystring,)

        if feed_id is not None:
            for article in self.dic[rss_feed_id]:
                article_content = utils.remove_html_tags(article[4].encode('utf-8') + article[2].encode('utf-8'))
                if querystring.lower() in article_content.lower():
                    if article[7] == "0":
                        # not readed articles are in bold
                        not_read_begin = "<b>"
                        not_read_end = "</b>"
                    else:
                        not_read_begin = ""
                        not_read_end = ""

                    html += article[1].encode('utf-8') + \
                            " - " + not_read_begin + \
                            """<a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                    (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                            not_read_end
        else:
            for rss_feed_id in self.dic.keys():
                for article in self.dic[rss_feed_id]:
                    article_content = utils.remove_html_tags(article[4].encode('utf-8') + article[2].encode('utf-8'))
                    if querystring.lower() in article_content.lower():
                        if article[7] == "0":
                            # not readed articles are in bold
                            not_read_begin = "<b>"
                            not_read_end = "</b>"
                        else:
                            not_read_begin = ""
                            not_read_end = ""

                        html += article[1].encode('utf-8') + \
                                " - " + not_read_begin + \
                                """<a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                        (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                                not_read_end + """ from <i><a href="%s">%s</a></i><br />\n""" % \
                                        (article[6].encode('utf-8'), article[5].encode('utf-8'))
        html += "<hr />"
        html += htmlfooter
        return html

    q.exposed = True


    def fetch(self):
        """
        Fetch all feeds
        """
        feed_getter = feedgetter.FeedGetter()
        feed_getter.retrieve_feed()
        return self.index()

    fetch.exposed = True


    def description(self, article_id):
        """
        Display the description of an article in a new Web page.
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        for rss_feed_id in self.dic.keys():
            for article in self.dic[rss_feed_id]:
                if article_id == article[0]:

                    if article[7] == "0":
                        self.mark_as_read("Article:"+article[3]) # update the database

                    html += """<h1><i>%s</i> from <a href="/all_articles/%s">%s</a></h1><br />""" % \
                            (article[2].encode('utf-8'), rss_feed_id, article[5].encode('utf-8'))
                    description = article[4].encode('utf-8')
                    if description:
                        html += description
                    else:
                        html += "No description available."
                    html += """<hr />\n<a href="%s">Complete story</a>\n<br />\n""" % \
                                    (article[3].encode('utf-8'),)
                    # Share this article:
                    # on delicious
                    html += """<a href="http://delicious.com/post?url=%s&title=%s"
                            rel="noreferrer" target="_blank">\n
                            <img src="/css/img/delicious.png" title="Share on del.iciou.us" /></a> &nbsp;&nbsp; """ % \
                                    (article[3].encode('utf-8'), article[2].encode('utf-8'))
                    # on Digg
                    html += """<a href="http://digg.com/submit?url=%s&title=%s"
                            rel="noreferrer" target="_blank">\n
                            <img src="/css/img/digg.png" title="Share on Digg" /></a> &nbsp;&nbsp; """ % \
                                    (article[3].encode('utf-8'), article[2].encode('utf-8'))
                    # on reddit
                    html += """<a href="http://reddit.com/submit?url=%s&title=%s"
                            rel="noreferrer" target="_blank">\n
                            <img src="/css/img/reddit.png" title="Share on reddit" /></a> &nbsp;&nbsp; """ % \
                                    (article[3].encode('utf-8'), article[2].encode('utf-8'))
                    # on Scoopeo
                    html += """<a href="http://scoopeo.com/scoop/new?newurl=%s&title=%s"
                            rel="noreferrer" target="_blank">\n
                            <img src="/css/img/scoopeo.png" title="Share on Scoopeo" /></a> &nbsp;&nbsp; """ % \
                                    (article[3].encode('utf-8'), article[2].encode('utf-8'))
                    # on Blogmarks
                    html += """<a href="http://blogmarks.net/my/new.php?url=%s&title=%s"
                            rel="noreferrer" target="_blank">\n
                            <img src="/css/img/blogmarks.png" title="Share on Blogmarks" /></a>""" % \
                                    (article[3].encode('utf-8'), article[2].encode('utf-8'))
        html += "<hr />\n" + htmlfooter
        return html

    description.exposed = True


    def all_articles(self, feed_id):
        """
        Display all articles of a feed ('feed_title').
        """
        html = htmlheader
        html += htmlnav
        html += """<div class="right inner">\n"""
        html += """<a href="/mark_as_read/Feed:%s">Mark all articles from this feed as read</a>""" % (feed_id,)
        html += """<br />\n<form method=get action="/q/Feed"><input type="text" name="Feed:%s:querystring" value=""><input
        type="submit" value="Search this feed"></form>\n""" % (feed_id,)
        html += "<hr />\n"
        html += """Your feeds (%s):<br />\n""" % len(self.dic.keys())
        for rss_feed_id in self.dic.keys():

            html += """<a href="/#%s">%s</a> (<a href="/unread/%s"
                    title="Unread article(s)">%s</a> / %s)<br />\n""" % \
                                (rss_feed_id.encode('utf-8'), \
                                self.dic[rss_feed_id][0][5].encode('utf-8'), \
                                rss_feed_id, self.dic_info[rss_feed_id][1], \
                                self.dic_info[rss_feed_id][0])
        html += """</div> <div class="left inner">"""
        html += """<h1>Articles of the feed <i>%s</i></h1><br />""" % (self.dic[feed_id][0][5].encode('utf-8'))

        for article in self.dic[feed_id]:

            if article[7] == "0":
                # not readed articles are in bold
                not_read_begin = "<b>"
                not_read_end = "</b>"
            else:
                not_read_begin = ""
                not_read_end = ""

            html += article[1].encode('utf-8') + \
                    " - " + not_read_begin + \
                    """<a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                            (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                    not_read_end + \
                    "<br />\n"

        html += """\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    all_articles.exposed = True


    def unread(self, feed_id):
        """
        Display all unread articles of a feed ('feed_title').
        """
        html = htmlheader
        html += htmlnav
        html += """</div> <div class="left inner">"""
        html += """<h1>Unread article(s) of the feed <a href="/all_articles/%s">%s</a></h1>
                <br />""" % (feed_id, self.dic[feed_id][0][5].encode('utf-8'))

        for article in self.dic[feed_id]:

            if article[7] == "0":

                html += article[1].encode('utf-8') + \
                        """ - <a href="/description/%s" rel="noreferrer" target="_blank">%s</a>""" % \
                                (article[0].encode('utf-8'), article[2].encode('utf-8')) + \
                        "<br />\n"

        html += """<hr />\n<a href="/mark_as_read/Feed:%s">Mark all as read</a>""" % (feed_id,)
        html += """\n<h4><a href="/">All feeds</a></h4>"""
        html += "<hr />\n"
        html += htmlfooter
        return html

    unread.exposed = True


    def mark_as_read(self, target):
        """
        Mark one (or more) article(s) as read by setting the value of the field
        'article_readed' of the SQLite database to 1.
        """
        param, _, identifiant = target.partition(':')
        try:
            conn = sqlite3.connect("./var/feed.db", isolation_level = None)
            c = conn.cursor()
            # Mark all articles as read.
            if param == "All":
                c.execute("UPDATE articles SET article_readed=1")
            # Mark all articles from a feed as read.
            elif param == "Feed" or param == "Feed_FromMainPage":
                c.execute("UPDATE articles SET article_readed=1 WHERE feed_site_link='" + self.dic[identifiant][0][6] + "'")
            # Mark an article as read.
            elif param == "Article":
                c.execute("UPDATE articles SET article_readed=1 WHERE article_link='" + identifiant + "'")
            conn.commit()
            c.close()
        except Exception, e:
            pass

        self.dic, self.dic_info = utils.load_feed()

        if param == "All" or param == "Feed_FromMainPage":
            return self.index()
        elif param == "Feed":
            return self.all_articles(identifiant)

    mark_as_read.exposed = True




if __name__ == '__main__':
    # Point of entry in execution mode
    root = Root()
    cherrypy.quickstart(root, config=path)