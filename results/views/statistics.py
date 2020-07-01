import operator

from datetime import datetime, date

from django.views.decorators.cache import never_cache
from django.forms.models import model_to_dict
from django.http import JsonResponse
from rest_framework.decorators import api_view

from results.models.results import Result
from results.models.competitions import CompetitionLevel


@never_cache
@api_view()
def statistics_pohjolan_malja(request, year):
    """
    Calculates organization points from SM competitions.

    First athlete or team per category gets 8 points for the organization
    they represent, second gets 7 and so on until 8th get 1 point.

    All SM competitions during a calendar year are counted.
    """
    if not request.user.is_staff:
        return JsonResponse({'message': 'Forbidden'}, status=403)
    level_list = ['SM']
    max_position = 8
    competition_levels = CompetitionLevel.objects.filter(abbreviation__in=level_list)
    results = Result.objects.filter(competition__level__in=competition_levels, position__lte=8,
                                    competition__date_start__year=year).prefetch_related('competition', 'organization')
    data_dict = {}
    for result in results:
        if result.organization:
            points = max_position - result.position + 1
            organization = result.organization
            if organization not in data_dict:
                data_dict[organization] = points
            else:
                data_dict[organization] = data_dict[organization] + points
    object_list = sorted(data_dict.items(), key=operator.itemgetter(1), reverse=True)
    data = []
    for obj in object_list:
        data.append({
            'organization': model_to_dict(obj[0], fields=['id', 'name', 'abbreviation']),
            'value': obj[1]
        })
    return JsonResponse({'results': data})


def _sjal_ranking_add(athlete, division, result_total, result_1440, n, n70):
    """
    Creates a result object

    :param athlete: Athlete
    :param division: division
    :param result_total: total result
    :param result_1440: 1440 round result
    :param n: number of competitions
    :param n70: number of 70m competitions
    :type athlete: Athlete object
    :type division: string
    :type result_total: int
    :type result_1440: int
    :type n: int
    :type n70: int
    :return: result object
    :rtype: dict
    """
    if n70 > 2 and division == 'compound':
        return {
            'athlete': {
                'id': athlete.pk,
                'first_name': athlete.first_name,
                'last_name': athlete.last_name,
                'organization': athlete.organization.abbreviation
            },
            'result': result_total,
            'competitions': n
        }
    else:
        return {
            'athlete': {
                'id': athlete.pk,
                'first_name': athlete.first_name,
                'last_name': athlete.last_name,
                'organization': athlete.organization.abbreviation
            },
            'result': result_total + result_1440,
            'competitions': n
        }


def _sjal_ranking_get_results(division, date_start, date_end):
    """
    Filters Result queryset for SJAL ranking

    :param division: division
    :param date_start: start date
    :param date_end: end date
    :type division: string
    :type date_start: date
    :type date_end: date
    :return: Results
    :rtype: queryset
    """
    categories_recurve = ['Y', 'N', '17', 'T17', '20', 'N20', '50', 'N50', '60', 'N60']

    categories_compound = ['YT', 'NT', '17T', 'T17T', '20T', 'N20T', '50T', 'N50T', '60T', 'N60T', '70T', 'N70T']
    categories_barebow = ['YV', 'NV', '17V', 'T17V', '20V', 'N20V', '50V', 'N50V', '60V', 'N60V', '70V', 'N70V', 'YLB',
                          'NLB', '20LB']
    competition_types = ['18m', '25m', '70m', '1440']
    if date_start and date_end and division in ['recurve', 'compound', 'barebow']:
        results = Result.objects.filter(
            competition__type__abbreviation__in=competition_types,
            athlete__organization__external=False,
            competition__date_end__gte=date_start,
            competition__date_start__lte=date_end).order_by('athlete', '-result')
        if division == 'recurve':
            results = results.filter(category__abbreviation__in=categories_recurve)
        elif division == 'compound':
            results = results.filter(category__abbreviation__in=categories_compound)
        elif division == 'barebow':
            results = results.filter(category__abbreviation__in=categories_barebow)
        results = results.prefetch_related('athlete',
                                           'athlete__organization',
                                           'category',
                                           'competition__type')
        return results
    return Result.objects.none()


@never_cache
@api_view()
def statistics_sjal_ranking(request, division):
    """
    Calculates SJAL ranking by archer.

    Categories that are shooting same distance and target size Y and N are included.
    Three best 18m/25m results and 2 best 70m results and the best 1440 round result (divided by 2) are included.
    Compound and barebow athletes may substitute 1440 round result with third 70m result.

    Returns JSON:
    {
        'results': [
            {
                'athlete': {
                    'id': athlete.pk,
                    'first_name': athlete.first_name,
                    'last_name': athlete.last_name,
                    'organization': athlete.organization.abbreviation
                },
                'result': result total,
                'competitions': number of competitions included (max 6)
            }
        ]
    }
    """
    categories_recurve_outdoor = ['Y', 'N', '20', 'N20']
    competition_types_indoor = ['18m', '25m']
    try:
        date_start = datetime.strptime(request.GET.get('date_start', None), '%Y-%m-%d').date()
        date_end = datetime.strptime(request.GET.get('date_end', None), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        date_start = None
        date_end = None
    try:
        limit = int(request.GET.get('limit', 0))
    except ValueError:
        limit = 0
    if limit < 0:
        limit = 0
    ranking = []
    results = _sjal_ranking_get_results(division, date_start, date_end)
    result_total = 0
    result_1440 = 0
    n = 0
    n18 = 0
    n70 = 0
    n1440 = 0
    athlete = None
    for result in results:
        if athlete and athlete != result.athlete:
            if result_total > 0 or result_1440 > 0:
                ranking.append(_sjal_ranking_add(athlete, division, result_total, result_1440, n, n70))
            result_total = 0
            result_1440 = 0
            n = 0
            n18 = 0
            n70 = 0
            n1440 = 0
        athlete = result.athlete
        if result.competition.type.abbreviation in competition_types_indoor and n18 < 3:
            n18 += 1
            n += 1
            result_total = result_total + result.result
        elif result.competition.type.abbreviation == '1440' and n1440 < 1:
            if division == 'compound' or (division == 'recurve' and
                                          result.category.abbreviation in categories_recurve_outdoor):
                n1440 += 1
                n += 1
                result_1440 = result.result // 2
        elif result.competition.type.abbreviation == '70m':
            if (division == 'compound' or division == 'barebow') and n70 < 3:
                n70 += 1
                n += 1
                if n70 == 3:
                    if result_1440 > result.result:
                        result_total = result_total + result_1440
                    else:
                        result_total = result_total + result.result
                else:
                    result_total = result_total + result.result
            elif division == 'recurve' and n70 < 2 and result.category.abbreviation in categories_recurve_outdoor:
                n70 += 1
                n += 1
                result_total = result_total + result.result
        if (division == 'compound' or division == 'barebow') and n > 6:
            n = 6
    if result_total > 0 or result_1440 > 0:
        ranking.append(_sjal_ranking_add(athlete, division, result_total, result_1440, n, n70))
    sorted_ranking = sorted(ranking, key=lambda k: k['result'], reverse=True)
    rank = 1
    temp_rank = 1
    temp_result = 0
    for item in sorted_ranking:
        if item['result'] == temp_result:
            item['rank'] = temp_rank
        else:
            item['rank'] = rank
            temp_rank = rank
        rank += 1
        temp_result = item['result']
    if limit:
        sorted_ranking = sorted_ranking[:limit]
    return JsonResponse({'results': sorted_ranking})
