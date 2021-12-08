from rest_framework.pagination import LimitOffsetPagination, _positive_int


class CustomPagination(LimitOffsetPagination):
	default_limit = 25
	max_limit = 50
	min_limit = 1
	min_offset = 1
	max_offset = 50

	def get_limit(self, request):
		if self.limit_query_param:
			try:
				return _positive_int(
					request.query_params[self.limit_query_param],
					strict=True,
					cutoff=self.max_limit
				)
			except (KeyError, ValueError):
				pass

		return self.default_limit

	def get_offset(self, request):
		try:
			return _positive_int(
				request.query_params[self.offset_query_param],
			)
		except (KeyError, ValueError):
			return 0