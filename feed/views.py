from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.pagination import PageNumberPagination

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from core.api_response import APIResponse
from cache.services.feed_cache_service import DoctorFeedCacheService
from feed.filters import DoctorFeedFilter
from feed.serializers import DoctorFeedCardSerializer
from feed.services.feed_engine import DoctorFeedEngine
from profiles.models.doctor_prof_mod import Doctor


class FeedPagination(PageNumberPagination):
    page_size            = 20
    page_size_query_param = "page_size"
    max_page_size        = 100


@method_decorator(csrf_exempt, name="dispatch")
class DoctorFeedViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class   = FeedPagination

    @swagger_auto_schema(
        tags=["Doctor Feed"],
        operation_summary="Get personalised doctor feed",
        manual_parameters=[
            openapi.Parameter("division",       openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by division ID",       required=False),
            openapi.Parameter("district",       openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by district ID",       required=False),
            openapi.Parameter("specialization", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Filter by specialization ID", required=False),
            openapi.Parameter("page",           openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Page number",                 required=False),
            openapi.Parameter("page_size",      openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Results per page (max 100)", required=False),
        ],
        responses={200: "Feed returned", 401: "Unauthorized"},
    )
    @action(detail=False, methods=["get"], url_path="doctors")
    def doctors(self, request):
        division       = request.GET.get("division")
        district       = request.GET.get("district")
        specialization = request.GET.get("specialization")
        user_id        = request.user.id

        # 1. try cache
        cached = DoctorFeedCacheService.GetFeed(user_id, division, district, specialization)
        if cached:
            return Response(cached)

        # 2. apply filters on the base queryset
        base_qs  = Doctor.objects.select_related("specialization", "division", "district", "evaluation")
        filtered = DoctorFeedFilter(request.GET, queryset=base_qs).qs

        # 3. run feed engine on the filtered queryset
        engine = DoctorFeedEngine(user=request.user)
        feed   = engine.generate_feed(queryset=filtered)

        # 4. attach computed score to each doctor instance for the serializer
        doctors_with_score = []
        for item in feed:
            doctor            = item["doctor"]
            doctor.feed_score = item["score"]
            doctors_with_score.append(doctor)

        # 5. paginate
        paginator = self.pagination_class()
        page      = paginator.paginate_queryset(doctors_with_score, request)

        serializer = DoctorFeedCardSerializer(page, many=True)
        response_data = paginator.get_paginated_response(
            APIResponse.success(
                message="Doctor feed retrieved successfully",
                title="feed",
                data=serializer.data,
            )
        ).data

        # 6. store in cache for one day
        DoctorFeedCacheService.SetFeed(user_id, response_data, division, district, specialization)

        return Response(response_data)
