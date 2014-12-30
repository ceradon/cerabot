#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pywikibot import Site
from template_replace import TemplateReplacer

class HKMTRReplace():
    def __init__(self):
        site = Site()
        templates = ["Template:HK-MTRL color"]
        target = "Template:HK-MTR color"
        test=(True, "User:Cerabot/Sandbox")
        bot = TemplateReplacer(site, names=templates, target=target,
            namespaces=[0], test=test, bot="Cerabot", 
            runpage="Run/Task 2")
        bot.deploy_task()
        templates = ["Template:HK-MTRL line"]
        target = "Template:HK-MTR line"
        bot = TemplateReplacer(site, names=templates, target=target,
            namespaces=[0], test=test, bot="Cerabot", 
            runpage="Run/Task 2")
        bot.deploy_task()
