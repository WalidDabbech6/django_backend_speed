# Generated by Django 4.2.11 on 2024-04-12 15:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0018_booking_paymentref'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='paymentRef',
        ),
    ]
