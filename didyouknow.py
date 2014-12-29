#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
from pywikibot import Page, Site, Category, User
import mwparserfromhell as parser

class DYKNotifier():
    def __init__(self, test=False):
        self.site = Site()
        self.test = test
        self.dyk_cat = "Category:Pending DYK nominations"
        self.subst = """
        ==[[{0}|{1}]] nominated for DYK!==
        {2}subst:User:Cerabot/DYK|{1}{3}\n
        —~~~~
        """
        self.summary = " ".join(("[[WP:DYK|Did you know]] notifier: [[{0}]]",
        "has been nominated! ([[User:Cerabot/Run/Task 2|bot]])"))
        self.notified_comment = " ".join(("\n* {{BotComment}} It appears that",
        "[[User:{0}|{0}]] created this article. They have been notified",
        "of this Did you know nomination. ([{1} diff]) Did I make an",
        "error? [[User talk:Ceradon|Report it to my owner!]] —~~~~"))
        self.notified_summary = " ".join(("[[WP:DYK|Did you know]] notifier:",
        "notified {0} of DYK nomination. ([[User:Cerabot/Run/Task 2|bot]])"))
        self.not_notified_details = {
            "inactive":"has not edited in 1 year or more",
            "blocked":"has been blocked",
            "ip":"is an IP address"
        }
        self.not_notified_comment = " ".join(("\n* {{BotComment}} {0} was not",
        "notified because {1}.{2} Did I make an error? [[User talk:Ceradon|",
        "Report it to my owner!]]"))
        self.not_notified_summary = " ".join(("[[WP:DYK|Did you know]] notifier:",
        "{0} was not notified because {1}. ([[User:Cerabot/Run/Task 2|bot]])"))
        self.diff_add = " ".join(("https://en.wikipedia.org/w/index.php?",
        "title={0}&diff={1}"))
    
    def do_page(self, dyk, article):
        self.check_run_page()
        dyk_creator = dyk.oldest_revision.user
        article_creator = article.oldest_revision.user
        if article_creator != dyk_creator:
            revs_users = dyk.contributingUsers(total=5000)
            if not article_creator in revs_users:
                dyk_text = dyk.get()
                a = self.creator_checks(article_creator)
                if not a["check_bool"]:
                    proof = a["proof"]
                    detail = self.not_notified_details[a["type"]]
                    reason = "the user " + detail
                    dyk_put_text = self.not_notified_comment.format(
                        article_creator,
                        reason,
                        proof
                        )
                    summary = self.not_notified_summary.format(
                        artice_creator,
                        reason
                        )
                    dyk_text = dyk_text + dyk_put_text
                    dyk.put(newtext=dyk_text,
                            comment=summary,
                            botflag=True,
                            minor=True
                            )
                    return True
                talk_title = "User talk:" + article_creator
                talk = Page(self.site, talk_title)
                text = talk.get()
                put_text = self.subst.format(dyk.title(), 
                                             article.title(),
                                             "{{",
                                             "}}"
                                            )
                text = text + put_text
                summary = self.summary.format(dyk.title())
                talk.put(newtext=text, 
                        comment=summary,
                        botflag=True,
                        minor=False
                        )
                diff = self.diff_add.format(dyk.title(),
                                            dyk.latest_revision_id
                                            )
                dyk_put_text = self.notified_comment(dyk_creator,
                                                     diff
                                                    )
                dyk_text = dyk_text + dyk_put_text
                summary = self.notified_summary.format(article_creator)
                dyk.put(newtext=dyk_text,
                        comment=summary,
                        botflag=True,
                        minor=True
                        )
        return True

    def creator_checks(self, user):
        user_object = User(self.site, user)
        return_dict = {
            "check_bool":True,
            "type":None,
            "proof":""
            }
        if user_object.isBlocked():
            return_dict["check_bool"] = False
            block_add = " ".join(("https://en.wikipedia.org/w/index.php?",
            "title=Special/Log&type=block&user={0}".format(user)))
            return_dict["proof"] = " ([" + block_add + " block log])"
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
            contribs_add = "Special:Contributions/{0}".format(user)
            return_dict["proof"] = " ([[" + contribs_add + "|contribs]])"
            return_dict["type"] = "inactive"
            return return_dict
        return return_dict
    
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
        if not 'yes' in text.lower().strip():
            raise Exception("Stop page disabled")
            
    def deploy_task(self):
        if self.test:
            a = Page(self.site, "User:Cerabot/Sandbox")
            b = Page(self.site, "User:Cerabot/Sandbox/2")
            self.do_page(a, b)
            return 1
        for dyk, article in self.generator():
            print "[[" + article.title() + "]]"
            self.do_page(dyk, article)

if __name__ == "__main__":
    dykbot = DYKNotifier()
    dykbot.deploy_task()
