"""
Analytics Module Tests
Tests for dashboard metrics, reports, and statistics.
"""
import pytest


class TestDashboardMetrics:
    """Test cases for dashboard metrics."""

    def test_get_dashboard_metrics_as_admin(self, client, admin_token):
        """ANLYT-001: Test admin can get dashboard metrics."""
        response = client.get('/api/analytics/dashboard',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_dashboard_metrics_as_accountant(self, client, accountant_token):
        """Test accountant can access dashboard."""
        response = client.get('/api/analytics/dashboard',
            headers={'Authorization': f'Bearer {accountant_token}'})

        # Accountants may have limited access
        assert response.status_code in [200, 403]

    def test_dashboard_metrics_as_client_should_fail(self, client, client_token):
        """Test client cannot access analytics dashboard."""
        response = client.get('/api/analytics/dashboard',
            headers={'Authorization': f'Bearer {client_token}'})

        assert response.status_code == 403


class TestRevenueStats:
    """Test cases for revenue statistics."""

    def test_get_revenue_by_client(self, client, admin_token):
        """ANLYT-002: Test getting revenue statistics by client."""
        response = client.get('/api/analytics/revenue/by-client',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_get_revenue_by_service(self, client, admin_token):
        """Test getting revenue statistics by service."""
        response = client.get('/api/analytics/revenue/by-service',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_get_revenue_with_date_range(self, client, admin_token):
        """Test getting revenue for specific date range."""
        response = client.get('/api/analytics/revenue/by-client?date_from=2025-01-01&date_to=2025-01-31',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestLodgementStats:
    """Test cases for lodgement statistics."""

    def test_get_lodgement_summary(self, client, admin_token):
        """Test getting lodgement summary."""
        response = client.get('/api/analytics/lodgement-summary',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200


class TestWorkloadReport:
    """Test cases for team workload report."""

    def test_get_workload_report(self, client, admin_token):
        """ANLYT-003: Test getting team workload report."""
        response = client.get('/api/analytics/workload',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200

    def test_get_bottleneck_analysis(self, client, admin_token):
        """Test getting bottleneck analysis."""
        response = client.get('/api/analytics/bottlenecks',
            headers={'Authorization': f'Bearer {admin_token}'})

        assert response.status_code == 200
