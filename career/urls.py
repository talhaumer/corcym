from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from career.views import (
    AdminCandidateForJobView,
    AdminCandidateView,
    CandidateDetailView,
    CandidateGroupByView,
    CandidateViewSet,
    DeletedCandidateView,
    DeletedJobView,
    DeleteJobView,
    EmailDataView,
    JobCityListingView,
    JobListingView,
    JobLocationView,
    JobPostingView,
    JobViewSet,
)

app_name = "career"

router = DefaultRouter()
router.register(r"career", JobViewSet)
router.register(r"candidate", CandidateViewSet)


# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path("job-listing", JobListingView.as_view(), name="job-listing"),
    path("deleted-job/<int:pk>", DeletedJobView.as_view(), name="deleted-job"),
    path("location-api", JobLocationView.as_view(), name="location-api"),
    path(
        "deleted-candidate/<int:pk>",
        DeletedCandidateView.as_view(),
        name="deleted-candidate",
    ),
    path("candidate/view/", CandidateDetailView.as_view(), name="candidate-view"),
    path(
        "candidate/view/<int:pk>", CandidateDetailView.as_view(), name="candidate-view"
    ),
    path("job/posting/", JobPostingView.as_view(), name="job-posting"),
    path("job/posting/<int:pk>", JobPostingView.as_view(), name="job-posting"),
    path("candidate/detail/", AdminCandidateView.as_view(), name="candidate-detail"),
    path(
        "candidate/detail/<int:pk>",
        AdminCandidateView.as_view(),
        name="candidate-detail",
    ),
    path(
        "candidate/applied/job/",
        AdminCandidateForJobView.as_view(),
        name="candidate-applied-for-job",
    ),
    path("delete/job/<int:pk>", DeleteJobView.as_view(), name="delete-job"),
    url(r"job-api/", include(router.urls)),
    path("email/data/view/", EmailDataView.as_view(), name="email-data"),
    path("candidate-groupby", CandidateGroupByView.as_view(), name="candidate-groupby"),
    path("job-city", JobCityListingView.as_view(), name="job-city"),
]
