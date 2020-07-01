from rest_framework import routers

from divari.views import CompetitionViewSet, ResultViewSet, SeasonViewSet, SeasonResultViewSet

router = routers.DefaultRouter()
router.register(r'competitions', CompetitionViewSet)
router.register(r'results', ResultViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'seasonresults', SeasonResultViewSet)
