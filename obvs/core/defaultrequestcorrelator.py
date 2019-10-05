import uuid

from obvs.core.typing import RequestCorrelator


class DefaultRequestCorrelator(RequestCorrelator):
    def set_request_correlation_ids(self, request) -> None:
        if request.request_id is None:
            request.request_id = uuid.uuid1()
        if request.requester_id is None:
            request.requester_id = uuid.uuid1()

    def set_correlation_ids(self, request, response) -> None:
        response.request_id = request.request_id
        response.requester_id = request.requester_id

    def are_correlated(self, request, response) -> bool:
        return request.request_id == response.request_id and\
               request.requester_id == response.requester_id
