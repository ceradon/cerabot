#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path, getcwd
import re
import sys
import datetime
from pywikibot import Page, Site, Category, User
import mwparserfromhell as parser
SUBST = u"""
==[[{0}|{1}]] nominated for DYK!==
{2}subst:User:Cerabot/DYK|{1}{3}\n
—~~~~
"""
 
class DYKNotifier():
    def __init__(self, test=False):
        self.site = Site()
        self.test = test
        self.log = None
        self.dyk_cat = "Category:Pending DYK nominations"
        self.summary = u" ".join((u"[[WP:DYK|Did you know?]] notifier: [[{0}]]",
        u"has been nominated! ([[User:Cerabot/Run/Task 2|bot]])"))
        self.notified_comment = u" ".join((u"\n* {2}BotComment{3} It appears that",
        u"[[User:{0}|{0}]] created this article. They have been notified",
        u"of this ''Did you know?'' nomination. ([{1} diff]) <small>(Bot edit: did I",
        u"make an error? [[User talk:Ceradon|Report it to my owner!]])</small>"
        u"—~~~~"))
        self.notified_summary = u" ".join((u"[[WP:DYK|Did you know?]] notifier:",
        u"notified {0} of DYK nomination. ([[User:Cerabot/Run/Task 2|bot]])"))
        self.not_notified_details = {
            "inactive":u"has not edited in 1 year or more",
            "blocked":u"has been blocked",
            "ip":u"is an IP address"
        }
        self.not_notified_comment = u" ".join((u"\n* {3}BotComment{4} {0}, the creator",
        u"of the article in question was not notified of this ''Did you know''",
        u"nomination because {1}.{2} Did I make an error? [[User talk:Ceradon|",
        u"Report it to my owner!]] —~~~~"))
        self.not_notified_summary = u" ".join((u"[[WP:DYK|Did you know?]] notifier:",
        u"{0} was not notified because {1}. ([[User:Cerabot/Run/Task 2|bot]])"))
        self.diff_add = u"".join((u"https://en.wikipedia.org/w/index.php?",
        u"title={0}&diff={1}"))
    
    def _do_page(self, dyk, article, notify_expanders=False):
        self.check_run_page()
        dyk_end = " ".join(("}}<!--Please do not write below this line or remove",
        u"this line. Place comments above this line.-->"))
        dyk_regex = re.compile(dyk_end, re.IGNORECASE)
        dyk_creator = unicode(dyk.oldest_revision.user)
        article_creator = unicode(article.oldest_revision.user)
        if article_creator != dyk_creator:
            revs_users = dyk.contributingUsers(total=5000)
            if not article_creator in revs_users:
                dyk_text = dyk.get()
                talk_title = "User talk:" + article_creator
                talk = Page(self.site, talk_title)
                talk_text = talk.get()
                a = self._creator_checks(article_creator)
                if not a["check_bool"]:
                    proof = a["proof"]
                    detail = self.not_notified_details[a["type"]]
                    reason = "the user " + detail
                    if self._already_handled(dyk, "comment"):
                        return 1
                    dyk_put_text = self.not_notified_comment.format(
                        article_creator,
                        reason,
                        proof,
                        "{{",
                        "}}"
                        )
                    summary = self.not_notified_summary.format(
                        artice_creator,
                        reason
                        )
                    dyk_text = dyk_regex.sub("", dyk_text)
                    dyk_text = dyk_text.strip() + dyk_put_text + "\n\n" + dyk_end
                    dyk.put(newtext=dyk_text,
                            comment=summary,
                            botflag=True
                            )
                    return True
                if not self._already_handled(talk, stage="notify", dyk=article.title()):
                    put_text = SUBST.format(dyk.title(), 
                                            article.title(),
                                            "{{",
                                            "}}"
                                            )
                    talk_text = talk_text.strip() + put_text
                    summary = self.summary.format(article.title())
                    talk.put(newtext=talk_text, 
                            comment=summary,
                            botflag=True
                            )
                    diff = self.diff_add.format(talk_title.replace(" ", "_"),
                                                talk.latest_revision_id,
                                                "{{",
                                                "}}"
                                                )
                    dyk_put_text = self.notified_comment.format(article_creator,
                                                                diff,
                                                                "{{",
                                                                "}}"
                                                                )
                    dyk_text = dyk_regex.sub("", dyk_text)
                    dyk_text = dyk_text + dyk_put_text + "\n\n" + dyk_end
                    summary = self.notified_summary.format(article_creator)
                    dyk.put(newtext=dyk_text,
                            comment=summary,
                            botflag=True
                        )
                    return True
                elif not self._already_handled(dyk, "comment"):
                    diff = self.diff_add.format(talk_title.replace(" ", "_"),
                                                talk.latest_revision_id
                                                )
                    dyk_put_text = self.notified_comment.format(article_creator,
                                                                diff,
                                                                "{{",
                                                                "}}"
                                                                )
                    dyk_text = dyk_regex.sub("", dyk_text)
                    dyk_text = dyk_text + dyk_put_text + "\n\n" + dyk_end
                    summary = self.notified_summary.format(article_creator)
                    dyk.put(newtext=dyk_text,
                            comment=summary,
                            botflag=True
                            )
        if notify_expanders:
            ranked = {}
            rev_users = [a.user for a in article.revisions(total=5000)]
            a = list(set(rev_users))
            for member in a:
                ranked[member] = rev_users.count(member)
            for key, val in ranked:
                if val > 10:
                    x = self._creator_checks(self, key)
                    pass
        return True

    def _creator_checks(self, user):
        user = unicode(user)
        user_object = User(self.site, user)
        return_dict = {
            "check_bool":True,
            "type":None,
            "proof":""
            }
        if user_object.isBlocked():
            return_dict["check_bool"] = False
            block_add = u"".join((u"https://en.wikipedia.org/w/index.php?",
            u"title=Special/Log&type=block&user={0}".format(user)))
            return_dict["proof"] = u" ([" + block_add + " block log])"
            return_dict["type"] = "blocked"
            return return_dict
        elif user_object.isAnonymous():
            return_dict["check_bool"] = False
            return_dict["type"] = "ip"
            return return_dict
        year = datetime.datetime.today().year
        last_edit = [a for a in user_object.contributions(total=1)][0]
        x = year - last_edit[2].year
        if x >= 1:
            return_dict["check_bool"] = False
            contribs_add = u"Special:Contributions/{0}".format(user)
            return_dict["proof"] = u" ([[" + contribs_add + "|contribs]])"
            return_dict["type"] = "inactive"
            return return_dict
        return return_dict

    def _collect_handled(self):
        a = getcwd + self.log_file
        if path.isfile(a):
            f = open(a, "r")
            contents = f.read()
            if not contents:
                return False
            self.log = [eval(a.strip()) for a in contents.split("\n")]
            self.collected_handled = True
            return True
        return False

    def _already_handled(self, article, stage="notify", dyk=""):
        if stage == "notify":
            text = article.get()
            code = parser.parse(text)
            for t in code.filter_templates():
                if not t.has("bot"):
                    continue
                elif unicode(t.get("bot").value).lower().strip() == "cerabot":
                    a = t.get("text").value
                    link = a.filter_wikilinks()[0]
                    if unicode(link.title).lower() == unicode(dyk).lower():
                        return True
                else:
                    return False
        elif stage == "comment":
            text = article.get()
            regex = re.compile(u"\{\{botcomment\}\}\s*(?:.*)\—\[\[user:(.*)\|(.*)\]\]",
                re.IGNORECASE)
            result = regex.search(text)
            if not result:
                return False
            if "cerabot" in result.group(2).lower().strip():
                return True
            else:
                return False
        else:
            raise ValueError("variable 'stage' did not have a recognized value.")

    def _cleanup_log(self):
        pass

    def generator(self):
        cat = Category(self.site, self.dyk_cat)
        dyks = [a for a in cat.articles(namespaces=[10])]
        for dyk in dyks:
            title = dyk.title().split("/")
            if len(title) > 3:
                title = title[1:]
            else:
                title = title[1]
            article = Page(self.site, title)
            yield (dyk, article)

    def check_run_page(self):
        stop_page = Page(self.site, "User:Cerabot/Run/Task 2")
        text = stop_page.get(force=True)
        if not u'yes' in text.lower().strip():
            raise Exception("Stop page disabled")
            
    def deploy_task(self):
        if self.test:
            a = Page(self.site, "User:Cerabot/Sandbox")
            b = Page(self.site, "User:Cerabot/Sandbox/2")
            self._do_page(a, b)
            return 1
        for dyk, article in self.generator():
            print "[[" + unicode(article.title()) + "]]"
            self._do_page(dyk, article)
        self._cleanup_log()

if __name__ == "__main__":
    dykbot = DYKNotifier()
    dykbot.deploy_task()
