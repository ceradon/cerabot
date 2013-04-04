#!usr/bin/python
# -*- coding: utf-8 -*-
import sys
import mwparserfromhell
from dateutil.parser import parse
from datetime import datetime
from cerabot.wiki.tasks import Task

class TemplateDater(Task):
    """Task to date all maintenance templates on
    Wikipedia article if they do not contain one 
    already."""
    name = "template_dater"
    task = 1

    def setup(self):
        """Sets up a few very important variables."""
        self._pages = []
        self._redirects = {}
        self._templates = []
        self.year = datetime.today().strftime('%Y')
        self.month = datetime.today().strftime('%B')
        self.load_templates()
        self.load_pages()

    def load_templates(self):
        page = "Wikipedia:AutoWikiBrowser/Dated templates"
        templates = self._site.page(page)
        templates.load()
        content = templates.content
        code = mwparserfromhell.parse(content)
        # Firstly, we need to load all of the actual names
        # of the template we aree to date. "Why?", "Citation 
        # needed", etc.
        for template in code.filter_templates():
            name = template.name.lower()
            if name == "tl":
                t = template.get(1).value.lower()
                self.templates.append(t)
            else:
                continue

        # Afterwards, all redirects to the above templates we've
        # listed need to be loaded, for the sake of proficiency.
        page = "Wikipedia:AutoWikiBrowser/Template redirects"
        redirects = self._site.page(page)
        redirects.load()
        content = redirects.content
        section = content[content.find(
                    "===Maintenance templates===")
                    +len("===Maintenance templates==="):
                    content.find("===Navbox templates===")
                    +len("===Navbox templates===")]
        delimeter = u'→'
        lines = section.split("\n")
        for line in lines:
            if not delimeter in unicode(line):
                continue
            split = line.split(delimeter)
            if len(split) != 2:
                continue
            code_1 = mwparserfromhell.parse(split[0])
            code_2 = mwparserfromhell.parse(split[1])
            destination = code_2.filter_templates()[0].get(1).value
            for template in code_1.filter_templates():
                if template.name.lower() == "tl":
                    name = template.get(1).value
                    self._redirects[name.lower()] = destination
                    self._redirects[destination.lower()] = destination
                else:
                    continue
        self._bot.logger.info("Completed loading of templates and redirects.")
        return

    def load_pages(self):
        i = "Category:Wikipedia maintenance categories sorted by month"
        categoryobj = self._site.category(i)
        categoryobj.load_attributes(get_all_members=True)
        for item in categoryobj.subcats:
            itemobj = self._site.category(item.title)
            for page in itemobj.load_attributes(get_all_members=True).members:
                self.pages.append(page)
            break
        return

    def _in_use(self, page):
        """Checks if the page is in use."""
        code = mwparserfromhell.parse(page.content)
        templates = code.filter_templates()
        for template in templates:
            if 'in use' in template.lower():
                return True
        return False

    def is_dormant(self, page):
        timestamp = page.last_edited
        delta = datetime.datetime.now() - timestamp
        result = delta > datetime.timedelta(seconds=600)
        return result

    @property
    def pages(self):
        return self._pages

    @property
    def templates(self):
        if not hasattr(self, "_templates"):
            self._templates = []
        return self._templates

    @property
    def redirects(self):
        if not hasattr(self, "_redirects"):
            self._redirects = {}
        return self._redirects

    @property
    def correct_dates(Self):
        correct_dates = {
            'january':'January',
            'jan':'January',
            'february':'February',
            'feb':'February',
            'march':'March',
            'mar':'March',
            'april':'April',
            'apr':'April',
            'may':'May',
            'june':'June',
            'jun':'June',
            'july':'July',
            'jul':'July',
            'august':'August',
            'aug':'August',
            'september':'September',
            'sep':'September',
            'sept':'September',
            'october':'October',
            'oct':'October',
            'november':'November',
            'nov':'November',
            'december':'December',
            'dec':'December'
        }
        return correct_dates

    def handle_page(self, page):
        """Date the maintenance templates on a particular page,
        returning the updated text and the summary for the edit."""
        summary = {}
        content = page.content
        code = mwparserfromhell.parse(content)
        templates = code.filter_templates(recursive=True)
        for template in templates:
            name = template.name.lower().strip()
            if name in self._redirects.keys():
                new_name = self._redirects[name]
                if new_name.lower() != name:
                    template.name = new_name
            if template.name.lower() in self._to_date:
                if not template.has_param("date"):
                    template.add('date', datetime.datetime.today()
                            .strftime('%B %Y'))
                    if template.name.lower() in summary.keys():
                        summary[template.name.lower()] += 1
                    else:
                        summary[template.name.lower()] = 1
                else:
                    old_date = temp.get('date').value
                    date = temp.get('date').value.lower()
                    month = date.split()[0]
                    year = date.split()[1]
                    if month in self.correct_dates.keys():
                        month = self.correct_dates[month]
                    if 'currentmonthname' in month.lower():
                        month = self.month
                    if 'currentyear' in year.lower():
                        year = self.year
                    months = map(lambda x: x.lower(), self.correct_dates.values())
                    if not month.lower() in months:
                        month = self.month
                    new_date = month+' '+year
                    if old_date != new_date:
                        temp.get('date').value = new_date
                        if temp.name.lower() in summary.keys():
                            summary[temp.name.lower()] += 1
                        else:
                            summary[temp.name.lower()] = 1
                    else:
                        continue
        msg = ', '.join('{{%s}} (%s)' % (item, summary[item]) 
                for item in summary.keys())
        return unicode(code), msg

    def run(self):
        for page in self.pages:
            print "[["+page.title+"]]"
            if page.is_redirect:
                continue
            if self._in_use(page):
                print "Page "+page.title+" is in use."
                continue
            if not self.is_dormant(page):
                continue
            if not page.is_excluded:
                continue
            newtext, msg = self.run_bot(page)
            if not msg:
                continue
            try:
                self.run_page_enabled()
                newtext = newtext.encode('utf-8')
                res = page.edit(text=newtext, summary=self.build_summary(
                        'Dating templates: '+msg))
            except exceptions.CerabotError as e:
                msg = "Exception was raised: {1}"
                self._logger.warn(msg.format(e.message))
                continue
        return
