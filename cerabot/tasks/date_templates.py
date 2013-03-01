import re
import sys
import inspect
from datetime import datetime
from cerabot import *

class DateTemplates(bot.Bot):
    """Bot to date maintenance templates that have none."""
    name = "template_dater"
    task = 1

    def __init__(self):
        """Ensures DateTemplates is the child of the
        `Bot` class.
        """
        super(DateTemplates, self).__init__()
        self.pages = []
        self._to_date = []
        self._redirects= {}
        self.year = datetime.today().strftime('%Y')
        self.month = datetime.today().strftime('%B')
        self.correct_dates = {
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

    def _load_templates(self):
        """Load the templates we have to date."""
        templates_page = page.Page(self.wiki, "Wikipedia:AutoWikiBrowser/"+
                                   "Dated templates")
        text = templates_page.getWikiText()
        code = parser.parse(text)
        for template in code.filter_templates():
            if template.name.lower() == "tl":
                self._to_date.append(template.get(1)
                        .value.lower())
        
        """Load the redirects to the templates we
        must date.
        """
        redirects_page = page.Page(self.wiki, "Wikipedia:AutoWikiBrowser/"+
                                   "Template redirects")
        text_ = redirects_page.getWikiText()
        section = re.search('===Maintenance templates===\n?(.*)'+
                        '===Navbox templates===', text, re.DOTALL)
        for line in section.group(0).splitlines():
            if not '→' in line:
                continue
            split = line.split('→')
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
        return

    def _in_use(self, text):
        """Checks if the page is in use."""
        code = parser.parse(text)
        templates = code.filter_templates()
        for template in templates:
            if 'in use' in template.lower():
                return True
        return False

    def _generate_pages(self):
        """Generates a list of all pages to date."""
        category_object = category.Category(self.wiki, "Category:Wikipedia maintenance "+
                "categories sorted by month")
        members = category_object.getAllMembers(titleonly=True, namespaces=[14])
        for item in members:
            item_object = category.Category(self.wiki, item)
            for page in item_object.getAllMembers(namespaces=[0]):
                yield page
        return

    def start(self):
        self.pages = self._generate_pages()
        self._load_templates()
    
    def run_bot(self, page=None):
        templates = {}
        if page and inspect.isclass(page):
            text = page.getWikiText()
            code = parser.parse(text)
            templates = code.filter_templates(recursive=True)
            for template in templates:
                name = template.name.lower().strip()
                if name in self._redirects.keys():
                    new_name = self._redirects[name]
                    if new_name.lower() != name:
                        template.name = new_name
                if template.name.lower() in self._to_date:
                    if not template.has_param("date"):
                        template.add('date', datetime.today().strftime('%B %Y'))
                        if template.name.lower() in summary.keys():
                            summary[template.name.lower()] += 1
                        else:
                            summary[template.name.lower()] = 1
                    else:
                        old_date = tempalte.get("date").value
                        date = template.get("date").value.lower()
                        month = date.split()[0]
                        year = date.split()[1]
                        if month in self.correct_dates.keys():
                            month = self.correct_dates[month]
                        if 'currentmonthname' in month.lower():
                            month = self.month
                        if 'currentyear' in year.lower():
                            year = self.year
                        months = map(lambda x: x.lower(), self.correct_dates
                                .values())
                        if not month in months:
                            month = self.month
                        new_date = month+' '+year
                        if old_date != new_date:
                            template.get('date').value = new_date
                            if template.name.lower() in summary.keys():
                                summary[template.name.lower()] += 1
                            else:
                                summary[template.name.lower()] = 1
                        else:
                            continue
        msg = ', '.join('Dating templates: {{%s}} (%s)' % 
                (item, summary[item]) for item in summary.keys())
        return unicode(code), msg

    def run(self):
        for page in self.pages:
            print "[["+page.title+"]]"
            if page.isRedir():
                return
            if self._in_use(page.getWikiText):
                raise exceptions.PageInUseError("Page "+page.title+" is in use.")
            newtext, msg = self.run_bot(page)
            if not msg:
                return
            try:
                self.run_page_enabled()
                res = page.edit(text=newtext, summary=self.build_summary(msg))
                if res['edit']['result'] == "Success":
                    out = "Edit was successful. New revision id is: {revid}."
                    print out.format(revid=res['edit']['newrevid'])
                else:
                    out = "Edit failed for some reason\n Here is the data the API"+ \
                            "sent us: {api_data}"
                    print out.format(api_data=res)
            except wiki.WikiError as e:
                print "Exception was raised: {1}".format(e)
                continue

if __name__ == '__main__':
    bot = DateTemplates()
    bot.run()
