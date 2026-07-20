from rest_framework import viewsets

from apps.commission.models import CommissionRule
from apps.commission.serializers import CommissionRuleSerializer
from apps.users.permissions import IsAdminRole


class CommissionRuleViewSet(viewsets.ModelViewSet):
    """/api/commission/admin/rules/ — admin-only CRUD on commission
    overrides (see apps.commission.selectors.resolve_commission_rate
    for how these are applied at checkout)."""

    permission_classes = [IsAdminRole]
    serializer_class = CommissionRuleSerializer
    queryset = CommissionRule.objects.all()
