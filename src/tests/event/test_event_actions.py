import datetime

import pytest

from pretalx.event.actions import build_initial_data, copy_data_from
from pretalx.event.models import Event


@pytest.fixture
def event():
    return Event.objects.create(
        name='Event', slug='event', is_public=True,
        email='orga@orga.org', locale_array='en,de', locale='en',
        date_from=datetime.date.today(), date_to=datetime.date.today()
    )


@pytest.mark.django_db
def test_initial_data(event):
    assert not hasattr(event, 'cfp')

    build_initial_data(event)

    assert event.cfp.default_type
    assert event.accept_template
    assert event.ack_template
    assert event.reject_template
    assert event.schedules.count()
    assert event.wip_schedule
    template_count = event.mail_templates.all().count()

    event.cfp.delete()
    build_initial_data(event)

    assert event.cfp
    assert event.cfp.default_type
    assert event.accept_template
    assert event.ack_template
    assert event.reject_template
    assert event.schedules.count()
    assert event.wip_schedule
    assert event.mail_templates.all().count() == template_count


@pytest.mark.django_db
@pytest.mark.parametrize('with_url', (True, False))
def test_event_copy_settings(event, submission_type, with_url):
    if with_url:
        event.settings.custom_domain = 'https://testeventcopysettings.example.org'
    build_initial_data(event)
    event.settings.random_value = 'testcopysettings'
    event.accept_template.text = 'testtemplate'
    event.accept_template.save()
    new_event = Event.objects.create(
        organiser=event.organiser, locale_array='de,en',
        name='Teh Name', slug='tn', timezone='Europe/Berlin',
        email='tehname@example.org', locale='de',
        date_from=datetime.date.today(), date_to=datetime.date.today()
    )
    copy_data_from(event, new_event)
    assert new_event.submission_types.count() == event.submission_types.count()
    assert new_event.accept_template
    assert new_event.accept_template.text == 'testtemplate'
    assert new_event.settings.random_value == 'testcopysettings'
    assert not new_event.settings.custom_domain
