from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend # For more advanced filtering
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer
# from .filters import OrderFilter # If we create a custom filter class

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Orders to be viewed or edited.
    Includes nested OrderItems.
    Supports filtering by status, customer_id, assigned_karigar_id, and date ranges.
    Supports searching by order_number and customer__name.
    """
    queryset = Order.objects.all().select_related(
        'customer', 'assigned_karigar'
    ).prefetch_related(
        'items', 'items__fabric', 'items__measurement' # Prefetch for performance
    ).order_by('-order_date', '-created_at') # Ensure consistent ordering

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can manage orders

    # Advanced filtering setup
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Define fields for DjangoFilterBackend
    # filterset_class = OrderFilter # Uncomment and define OrderFilter in orders/filters.py for complex logic
    filterset_fields = {
        'status': ['exact', 'in'], # ?status=Pending or ?status__in=Pending,Confirmed
        'customer__id': ['exact'],
        'customer__name': ['icontains'], # ?customer__name__icontains=Ahmed
        'customer__phone_number': ['exact', 'icontains'],
        'assigned_karigar__id': ['exact', 'isnull'], # ?assigned_karigar__isnull=true for unassigned
        'assigned_karigar__name': ['icontains'],
        'order_date': ['date', 'year', 'month', 'day', 'gte', 'lte', 'range'], # e.g. ?order_date__year=2023
        'delivery_due_date': ['date', 'year', 'month', 'day', 'gte', 'lte', 'range', 'isnull'],
        'total_amount': ['exact', 'gte', 'lte', 'gt', 'lt'],
    }

    search_fields = [
        'order_number',
        'customer__name',
        'customer__phone_number',
        'items__item_name', # Search within order items as well
        'order_details',
        'assigned_karigar__name',
    ]
    ordering_fields = [
        'order_date', 'delivery_due_date', 'status',
        'total_amount', 'customer__name', 'updated_at', 'created_at'
    ]

    def perform_create(self, serializer):
        # User creating the order could be associated here if needed:
        # serializer.save(created_by=self.request.user)
        serializer.save()
        # TODO: Consider post-save signals or overriding save in serializer
        # for complex logic like inventory deduction.

    def perform_update(self, serializer):
        # The serializer's update method handles the logic for items.
        # Ensure that if items are updated, total_amount is recalculated correctly in the serializer.
        serializer.save()

    # Example of a custom action to change order status
    # from rest_framework.decorators import action
    # @action(detail=True, methods=['post'], url_path='change-status')
    # def change_status(self, request, pk=None):
    #     order = self.get_object()
    #     new_status = request.data.get('status')
    #     if not new_status:
    #         return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)
    #     if new_status not in [choice[0] for choice in Order.ORDER_STATUS_CHOICES]:
    #         return Response({'error': 'Invalid status value'}, status=status.HTTP_400_BAD_REQUEST)

    #     order.status = new_status
    #     order.save()
    #     # TODO: Potentially trigger notifications or other actions based on status change
    #     return Response(OrderSerializer(order, context={'request': request}).data)

# Note: A separate OrderItemViewSet is generally not needed if items are always managed
# via the OrderSerializer's nested capabilities. If independent item manipulation is required
# (e.g. adding one item to an existing order without sending the whole order payload, or complex
# item-specific status tracking), then an OrderItemViewSet could be implemented, possibly nested under orders.
# For this phase, we assume items are managed with the order.
#
# If you were to add it:
# class OrderItemViewSet(viewsets.ModelViewSet):
#     queryset = OrderItem.objects.all().select_related('order__customer', 'fabric', 'measurement')
#     serializer_class = OrderItemSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     # Add filtering, search, ordering as needed
#
#     def perform_create(self, serializer):
#         order_item = serializer.save()
#         self._recalculate_order_total(order_item.order)
#
#     def perform_update(self, serializer):
#         order_item = serializer.save()
#         self._recalculate_order_total(order_item.order)
#
#     def perform_destroy(self, instance):
#         order = instance.order
#         instance.delete()
#         self._recalculate_order_total(order)
#
#     def _recalculate_order_total(self, order):
#         order.total_amount = sum(item.total_item_price for item in order.items.all())
#         order.save()
#
# This would require `django-filter` to be installed if using `filterset_fields` more extensively.
# For now, basic filtering is enabled via `filterset_fields` dictionary.
# pip install django-filter (if not already included)
# And add 'django_filters' to INSTALLED_APPS
# And ensure `REST_FRAMEWORK['DEFAULT_FILTER_BACKENDS'] = ['django_filters.rest_framework.DjangoFilterBackend']`
# or add it to specific ViewSets. Current setup uses DjangoFilterBackend explicitly.
# The `filterset_fields` as a dictionary works directly with DjangoFilterBackend.
# If `filterset_class` is used, then `django-filter` must be installed.
# For now, `django-filter` is not explicitly installed in requirements.txt,
# so I'm relying on the dictionary form of `filterset_fields`.
# I should add `django-filter` to dependencies for robust filtering.
#
# Let me add django-filter to dependencies now as it's good practice for DRF.
# (This thought process would lead to an action to install it).
# For now, the content of `orders/views.py` is complete.The `OrderViewSet` is defined. Before creating URLs and running migrations for the `orders` app, I need to ensure `django-filter` is installed, as `DjangoFilterBackend` is used in the ViewSet.

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Payments related to an Order.
    Accessed via nested URL: /api/v1/orders/{order_pk}/payments/
    """
    queryset = Payment.objects.all() # Base queryset, will be filtered
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should only return payments for the order
        specified in the URL.
        """
        order_pk = self.kwargs.get('order_pk')
        if not order_pk:
            return Payment.objects.none() # Should not happen with nested routing

        # Ensure the order exists
        get_object_or_404(Order, pk=order_pk)
        return Payment.objects.filter(order_id=order_pk).order_by('-payment_date', '-created_at')

    @transaction.atomic # Ensure atomicity for payment creation and order update
    def perform_create(self, serializer):
        """
        Link the payment to the order from the URL.
        Update the order's advance_payment field.
        """
        order_pk = self.kwargs.get('order_pk')
        order = get_object_or_404(Order, pk=order_pk)

        # Validate that total payments (including this one) do not exceed order total.
        # It's generally better to handle advance_payment specifically on the Order model,
        # and other payments as separate transactions.
        # This logic assumes we are adding to a list of payments, and Order.advance_payment
        # might be the initial downpayment.
        # For simplicity, let's assume any payment made via this endpoint is an addition to previous payments.
        # A more robust system might differentiate between 'advance' and 'installment'.

        # For now, let's make a simple check against order.total_amount
        # Consider that order.advance_payment is ALREADY part of total paid.
        # The sum of all Payment records + order.advance_payment should not exceed order.total_amount.
        # OR, if Order.advance_payment is just the *first* payment, then sum of all Payment records should not exceed.

        # Let's adopt a simpler model: Order.advance_payment is the initial deposit.
        # Subsequent payments are recorded in the Payment model.
        # The Order.due_amount property already reflects total - advance.
        # So, new payments reduce this due amount.

        # A payment should not make the order overpaid.
        amount_being_paid = serializer.validated_data.get('amount_paid', 0)

        # Calculate current total paid through Payment records for this order
        current_payments_sum = sum(p.amount_paid for p in order.payments.all())

        # The advance_payment on the Order model is considered the first payment.
        # So, total paid so far = order.advance_payment + current_payments_sum
        # If a new payment makes (order.advance_payment + current_payments_sum + amount_being_paid) > order.total_amount, it's an overpayment.

        if (order.advance_payment + current_payments_sum + amount_being_paid) > order.total_amount:
            # Allow for a small tolerance for rounding if necessary, or exact match.
            # For now, strict check.
            max_payable_further = order.total_amount - (order.advance_payment + current_payments_sum)
            if max_payable_further < 0: max_payable_further = 0 # Already overpaid or fully paid

            raise serializers.ValidationError(
                f"This payment would make the order overpaid. Maximum further payment accepted is {max_payable_further:.2f}."
            )

        serializer.save(order=order)
        # Note: We are NOT automatically updating order.advance_payment here.
        # order.advance_payment is considered the initial deposit.
        # The `payments` related manager on the Order model will list all individual payments.
        # The `due_amount` property on the Order model will need to be updated to reflect all payments.
        # This implies the Order model's due_amount or a new property `total_paid` needs to consider these Payment records.

        # Let's refine Order model's due_amount calculation or add total_paid property in the model/serializer.
        # For now, this PaymentViewSet just records the payment.
        # Recalculating order's `due_amount` or `paid_status` would typically happen via a signal or by updating the OrderSerializer.

    # perform_update and perform_destroy for payments might also need to trigger recalculation
    # of the order's payment status or due amount if we maintain such aggregated fields on the Order model.
    # For now, they just modify the Payment record.
    @transaction.atomic
    def perform_update(self, serializer):
        # Similar validation as perform_create might be needed if amount_paid changes.
        payment = self.get_object() # Get existing payment
        original_amount = payment.amount_paid
        new_amount = serializer.validated_data.get('amount_paid', original_amount)

        order = payment.order
        current_payments_sum_excluding_this = sum(p.amount_paid for p in order.payments.exclude(pk=payment.pk))

        if (order.advance_payment + current_payments_sum_excluding_this + new_amount) > order.total_amount:
            max_payable_further = order.total_amount - (order.advance_payment + current_payments_sum_excluding_this)
            if max_payable_further < 0: max_payable_further = 0
            raise serializers.ValidationError(
                 f"Updating this payment would make the order overpaid. Maximum this payment can be is {max_payable_further:.2f} (or less if other payments exist)."
            )
        serializer.save()

    @transaction.atomic
    def perform_destroy(self, instance):
        # If a payment is deleted, the order's payment status might change.
        # No direct update to Order model here, but data becomes consistent.
        instance.delete()
