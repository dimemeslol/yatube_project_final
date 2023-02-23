from django.views.generic.base import TemplateView


class AboutAuthorPage(TemplateView):
    template_name = 'about/about_author.html'


class AboutTechPage(TemplateView):
    template_name = 'about/about_tech.html'
