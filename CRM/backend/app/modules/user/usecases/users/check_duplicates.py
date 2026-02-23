"""
Check Duplicates Use Case - Check for potential duplicate users
"""
from sqlalchemy import or_

from app.common.usecase import BaseQueryUseCase, UseCaseResult
from app.modules.user.models import User
from app.modules.user.repositories import UserRepository


class CheckDuplicatesUseCase(BaseQueryUseCase):
    """
    Check for potential duplicate users.

    Business Rules:
    - Check exact match on email
    - Check exact match on phone
    - Check exact match on TFN (if provided)
    - Check fuzzy match on name
    """

    def __init__(self):
        self.user_repo = UserRepository()

    def execute(self, data: dict, company_id: str = None) -> UseCaseResult:
        duplicates = []

        email = data.get('email', '').lower().strip()
        phone = data.get('phone', '').strip()
        tfn = data.get('tfn', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()

        # Check email
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                duplicates.append({
                    'user': user.to_dict(),
                    'confidence': 'exact',
                    'matched_fields': ['email']
                })
                return UseCaseResult.ok({'duplicates': duplicates})

        # Build query for potential duplicates
        conditions = []

        if phone:
            conditions.append(User.phone == phone)

        if tfn:
            conditions.append(User.tfn == tfn)

        if conditions:
            query = User.query.filter(or_(*conditions))
            if company_id:
                query = query.filter(User.company_id == company_id)

            for user in query.all():
                matched_fields = []
                if phone and user.phone == phone:
                    matched_fields.append('phone')
                if tfn and user.tfn == tfn:
                    matched_fields.append('tfn')

                if matched_fields:
                    duplicates.append({
                        'user': user.to_dict(),
                        'confidence': 'exact',
                        'matched_fields': matched_fields
                    })

        # Fuzzy name match
        if first_name and last_name:
            fuzzy_matches = self._fuzzy_name_match(first_name, last_name, company_id)
            for match in fuzzy_matches:
                if not any(d['user']['id'] == match['user']['id'] for d in duplicates):
                    duplicates.append(match)

        return UseCaseResult.ok({'duplicates': duplicates})

    def _fuzzy_name_match(self, first_name: str, last_name: str, company_id: str = None):
        """Find users with similar names using Levenshtein distance"""
        matches = []

        query = User.query
        if company_id:
            query = query.filter(User.company_id == company_id)

        # Simple approach: look for users where names start with same letters
        users = query.filter(
            User.first_name.isnot(None),
            User.last_name.isnot(None)
        ).all()

        for user in users:
            similarity = self._calculate_name_similarity(
                first_name, last_name,
                user.first_name or '', user.last_name or ''
            )

            if similarity >= 0.8:  # 80% similar
                matches.append({
                    'user': user.to_dict(),
                    'confidence': 'fuzzy',
                    'matched_fields': ['name'],
                    'similarity': round(similarity * 100)
                })

        return matches[:5]  # Return top 5 matches

    def _calculate_name_similarity(self, fn1: str, ln1: str, fn2: str, ln2: str) -> float:
        """Calculate name similarity using simple ratio"""
        fn1, ln1 = fn1.lower(), ln1.lower()
        fn2, ln2 = fn2.lower(), ln2.lower()

        full1 = f'{fn1} {ln1}'
        full2 = f'{fn2} {ln2}'

        # Simple character-based similarity
        if full1 == full2:
            return 1.0

        # Calculate Jaccard similarity
        set1 = set(full1)
        set2 = set(full2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0
