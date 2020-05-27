import re

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView

from academic_helper.models.course import Course
from academic_helper.utils.logger import log


def index(request):
    return render(request, "index.html")


class ExtendedViewMixin(TemplateView):
    @property
    def title(self) -> str:
        base_name = self.__class__.__name__
        base_name = base_name.replace("View", "")
        return re.sub(r"(.)([A-Z])", "\\1 \\2", base_name)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class AjaxView(ExtendedViewMixin):
    template_name = "ajax.html"

    @property
    def title(self):
        return "Ajax"

    def get(self, request: WSGIRequest, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request: WSGIRequest, *args, **kwargs):
        log.info("We are in POST")
        if request.is_ajax():
            value = "Hi " + request.POST["value"]
            log.info(f"User sent {value} via Ajax")
            return JsonResponse({"success": True, "value": value})
        else:
            value = request.POST["post-text"]
            log.info(f"User sent {value} via POST")
            return self.render_to_response(context={"value": value})


class CourseDetailsView(DetailView, ExtendedViewMixin):
    model = Course
    template_name = "course-details.html"

    @property
    def title(self) -> str:
        return f"Course {self.object.course_number}"

    @property
    def object(self):
        return Course.objects.filter(course_number=self.kwargs["course_number"]).first()


class CoursesView(ExtendedViewMixin, ListView):
    model = Course
    template_name = "courses.html"

    @property
    def title(self) -> str:
        return "All Courses"

    @property
    def object_list(self):
        return Course.objects.all()


    def post(self, request: WSGIRequest, *args, **kwargs):
        log.info("Courses POST")
        if not request.is_ajax():
            raise NotImplemented()
        # log.info(f"User sent {value} via Ajax")
        name = request.POST["free_text"]
        result = Course.find_by(name)
        return JsonResponse({"success": True, "courses": list(result)})


class AboutView(ExtendedViewMixin):
    template_name = "about.html"