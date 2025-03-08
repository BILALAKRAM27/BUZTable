from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from user.forms import PaymentForm
from restaurants.models import Order
from .models import Payment

class PaymentModelTest(TestCase):
    
    def setUp(self):
        # Set up a user and order for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.order = Order.objects.create(
            user=self.user,
            total_amount=100.00,
            status='pending'
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            user=self.user,
            order=self.order,
            payment_method='credit_card',
            transaction_id='123abc',
            amount=100.00
        )
        
        # Test if the payment is created
        self.assertEqual(payment.user.username, 'testuser')
        self.assertEqual(payment.order.total_amount, 100.00)
        self.assertEqual(payment.status, 'pending')
        
    def test_payment_mark_completed(self):
        payment = Payment.objects.create(
            user=self.user,
            order=self.order,
            payment_method='paypal',
            transaction_id='456def',
            amount=50.00
        )
        
        # Mark the payment as completed
        payment.mark_as_completed()
        
        # Test if the status is updated to completed
        self.assertEqual(payment.status, 'completed')
        
    def test_payment_mark_failed(self):
        payment = Payment.objects.create(
            user=self.user,
            order=self.order,
            payment_method='bank_transfer',
            transaction_id='789ghi',
            amount=100.00
        )
        
        # Mark the payment as failed
        payment.mark_as_failed()
        
        # Test if the status is updated to failed
        self.assertEqual(payment.status, 'failed')

class PaymentFormTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.order = Order.objects.create(
            user=self.user,
            total_amount=100.00,
            status='pending'
        )

    def test_form_valid(self):
        form_data = {
            'payment_method': 'credit_card',
            'transaction_id': '123abc',
            'amount': 100.00
        }
        form = PaymentForm(data=form_data, order=self.order)
        
        # Test if the form is valid
        self.assertTrue(form.is_valid())
    
    def test_form_invalid(self):
        form_data = {
            'payment_method': 'credit_card',
            'transaction_id': '',  # Missing transaction_id
            'amount': 100.00
        }
        form = PaymentForm(data=form_data, order=self.order)
        
        # Test if the form is invalid
        self.assertFalse(form.is_valid())
        
        
        
class PaymentViewTest(TestCase):

    def setUp(self):
        # Create a user and order for testing
        self.user = User.objects.create_user(username='testuser', password='password')
        self.order = Order.objects.create(
            user=self.user,
            total_amount=100.00,
            status='pending'
        )

    def test_payment_page_access(self):
        self.client.login(username='testuser', password='password')
        url = reverse('make_payment', kwargs={'order_id': self.order.id})
        response = self.client.get(url)
        
        # Test if the payment page is accessible
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment for Order')

    def test_payment_submission(self):
        self.client.login(username='testuser', password='password')
        url = reverse('make_payment', kwargs={'order_id': self.order.id})
        
        # Simulate payment submission
        form_data = {
            'payment_method': 'credit_card',
            'transaction_id': 'testtx123',
            'amount': 100.00
        }
        response = self.client.post(url, data=form_data)
        
        # Test if payment was created and order status updated
        payment = Payment.objects.first()
        self.assertEqual(payment.transaction_id, 'testtx123')
        self.assertEqual(payment.status, 'completed')
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
        
        # Check that the user is redirected to the order details page
        self.assertRedirects(response, reverse('view_order', kwargs={'order_id': self.order.id}))



def test_payment_template_content(self):
    self.client.login(username='testuser', password='password')
    url = reverse('make_payment', kwargs={'order_id': self.order.id})
    response = self.client.get(url)
    
    # Ensure the form is rendered in the template
    self.assertContains(response, 'payment_method')
    self.assertContains(response, 'transaction_id')
    self.assertContains(response, 'amount')


