from django.core.mail import send_mail


def send_registration_email(user):
    subject = "Registration Complete"
    message = "Welcome to our site, {}. Your registration is complete.".format(user.username)
    from_email = 'nivdoron1234@gmail.com'
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
