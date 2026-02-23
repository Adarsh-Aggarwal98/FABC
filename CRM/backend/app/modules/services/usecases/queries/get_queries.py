"""
Get Queries Use Case
"""
from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.services.repositories import ServiceRequestRepository, QueryRepository
from app.modules.user.repositories import UserRepository


class GetQueriesUseCase(BaseQueryUseCase):
    """Get all queries for a request"""

    def __init__(self):
        self.request_repo = ServiceRequestRepository()
        self.query_repo = QueryRepository()
        self.user_repo = UserRepository()

    def execute(self, request_id: str, user_id: str) -> UseCaseResult:
        """
        Get all queries for a service request.

        Args:
            request_id: ID of the service request
            user_id: ID of the user requesting the queries

        Returns:
            UseCaseResult with list of queries
        """
        request = self.request_repo.get_by_id(request_id)
        if not request:
            return UseCaseResult.fail('Request not found', 'NOT_FOUND')

        user = self.user_repo.get_by_id(user_id)
        if not user:
            return UseCaseResult.fail('User not found', 'NOT_FOUND')

        # Validate access (respects company boundaries)
        is_owner = request.user_id == user_id
        can_access = self.request_repo.can_user_access_request(user, request)

        if not can_access and not is_owner:
            return UseCaseResult.fail('Not authorized to view queries', 'FORBIDDEN')

        # Staff can see internal queries, clients cannot
        is_staff = user.role.name in ['super_admin', 'admin', 'senior_accountant', 'accountant']
        queries = self.query_repo.get_by_request(request_id, include_internal=is_staff)

        return UseCaseResult.ok({
            'queries': [q.to_dict() for q in queries]
        })
