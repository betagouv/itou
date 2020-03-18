import datetime
import random

from django.db.models import F
from django.shortcuts import render

from itou.siaes.models import Siae
from itou.utils.pagination import pager
from itou.www.search.forms import SiaeSearchForm


def search_siaes(request, template_name="search/siaes_search_results.html"):

    form = SiaeSearchForm(data=request.GET)
    siaes_page = None

    if form.is_valid():

        city = form.cleaned_data["city"]
        distance_km = form.cleaned_data["distance"]
        kind = form.cleaned_data["kind"]

        siaes = (
            Siae.active_objects.within(city.coords, distance_km)
            .annotate(shuffled_rank=get_shuffled_rank())
            .order_by("shuffled_rank")
            .prefetch_job_description_through(is_active=True)
            .prefetch_related("members")
        )
        if kind:
            siaes = siaes.filter(kind=kind)
        siaes_page = pager(siaes, request.GET.get("page"), items_per_page=10)

    context = {"form": form, "siaes_page": siaes_page}
    return render(request, template_name, context)


def get_shuffled_rank():
    """
    Quick and dirty solution to shuffle results with a
    determistic seed which changes every day.

    We may later implement a more rigorous shuffling but this will
    need an extra column in db.

    Note that we have about 3K siaes.

    We produce a large pseudo-random integer on the fly from id
    with the static PG expression `(A+id)*(B+id)`
    which has the advantage of still be using index scan by PG.
    It is important that this large integer is far from zero to avoid
    that id=1,2,3 always stay on the top of the list.
    Thus we choose rather large A and B.

    We then take a modulo which changes everyday.
    """
    # Seed changes every day at midnight.
    random.seed(datetime.date.today())
    a = random.randint(1000, 10000)
    b = random.randint(1000, 10000)
    modulo = random.randint(100, 1000)
    return (a + F("id")) * (b + F("id")) % modulo
