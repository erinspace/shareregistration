import copy
import json
import mock

import vcr
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser, User
from shareregistration.views import index as main_index
from push_endpoint.views import DataList, EstablishedDataList, render_api_help, render_settings, provider_information

from push_endpoint.models import Provider, PushedData

VALID_POST = {
    "jsonData": {
        "creationDate": "2014-09-12",
        "contributors": [
            {
                "name": "Roger Danger Ebert",
                "sameAs": [
                    "https://osf.io/thing"
                ],
                "familyName": "Ebert",
                "givenName": "Roger",
                "additionalName": "Danger",
                "email": "rogerebert@example.com"
            },
            {
                "name": "Roger Madness Ebert"
            }
        ],
        "language": "eng",
        "description": "This is a thing",
        "directLink": "https://www.example.com/stuff",
        "providerUpdatedDateTime": "2014-12-12T00:00:00Z",
        "freeToRead": {
            "startDate": "2014-09-12",
            "endDate": "2014-10-12"
        },
        "licenseRef": [
            {
                "uri": "http://www.mitlicense.com",
                "startDate": "2014-10-12",
                "endDate": "2014-11-12"
            }
        ],
        "notificationLink": "http://myresearch.com/",
        "publisher": {
            "name": "Roger Ebert Inc",
            "email": "roger@example.com"
        },
        "raw": "http://osf.io/raw/thisdocument/",
        "relation": [
            "http://otherresearch.com/this"
        ],
        "resourceIdentifier": "http://landingpage.com/this",
        "revisionTime": "2014-02-12T15:25:02Z",
        "sponsorship": [{
            "award": {
                "awardName": "Participation",
                "awardIdentifier": "http://example.com"
            },
            "sponsor": {
                "sponsorName": "Orange",
                "sponsorIdentifier": "http://example.com/orange"
            }
        }],
        "title": "Interesting research",
        "journalArticleVersion": "AO",
        "versionOfRecord": "http://example.com/this/now/",
        "uris": {
            "canonicalUri": "http://example.com",
            "providerUris": [
                'http://provideruri1.source.com/doc1',
                'http://provideruri2.source.com/doc1'
            ]
        }
    }

}


class APIPostTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create(username='bubbaray', password='dudley')

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi1.yaml')
    def test_valid_submission(self):
        Provider.objects.create(user=self.user, shortname='devooonnnn')
        view = DataList.as_view()
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(VALID_POST),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, 201)
        Provider.objects.all().delete()

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi1.yaml')
    def test_valid_with_deleted_status(self):
        Provider.objects.create(user=self.user, shortname='devooonnnn')
        view = DataList.as_view()
        deleted_status_post = copy.deepcopy(VALID_POST)
        deleted_status_post['jsonData']['uris']['providerUris'][0] = 'http://thisshouldbedeleted.now'
        deleted_status_post['jsonData']['otherProperties'] = [
            {
                "name": "status",
                "properties": {
                    "status": ["deleted"]
                }
            }
        ]

        request = self.factory.post(
            '/pushed_data/',
            json.dumps(deleted_status_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        self.assertEqual(response.status_code, 201)

        new_data = view(self.factory.get('/pushed_data/'))
        self.assertEqual(len(new_data.data['results']), 1)
        self.assertEqual(new_data.data['results'][0]['status'], 'deleted')

        Provider.objects.all().delete()

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi4.yaml')
    def test_established_view(self):
        view = EstablishedDataList.as_view()
        request = self.factory.get(
            '/pushed_data/established',)
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_established_view(self):
        view = EstablishedDataList.as_view()
        request = self.factory.get(
            '/pushed_data/established'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_get_api_docs(self):
        view = render_api_help
        request = self.factory.get(
            '/help'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi.yaml')
    def test_missing_providerUpdateDateTime(self):
        view = DataList.as_view()
        invalid_post = copy.deepcopy(VALID_POST)
        invalid_post['jsonData'].pop('providerUpdatedDateTime')
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(invalid_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        data = response.data

        self.assertEqual(data['detail'], "'providerUpdatedDateTime' is a required property")
        self.assertEqual(response.status_code, 400)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi.yaml')
    def test_missing_title_fails(self):
        view = DataList.as_view()
        invalid_post = copy.deepcopy(VALID_POST)
        invalid_post['jsonData'].pop('title')
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(invalid_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        data = response.data

        self.assertEqual(data['detail'], "'title' is a required property")
        self.assertEqual(response.status_code, 400)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi.yaml')
    def test_missing_contributors_fails(self):
        view = DataList.as_view()
        invalid_post = copy.deepcopy(VALID_POST)
        invalid_post['jsonData'].pop('contributors')
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(invalid_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        data = response.data

        self.assertEqual(data['detail'], "'contributors' is a required property")
        self.assertEqual(response.status_code, 400)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi.yaml')
    def test_missing_providerUri_fails(self):
        view = DataList.as_view()
        invalid_post = copy.deepcopy(VALID_POST)
        invalid_post['jsonData']['uris'].pop('providerUris')
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(invalid_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        data = response.data

        self.assertEqual(data['detail'], "'providerUris' is a required property")
        self.assertEqual(response.status_code, 400)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi3.yaml')
    def test_missing_uris(self):
        view = DataList.as_view()
        invalid_post = copy.deepcopy(VALID_POST)
        invalid_post['jsonData'].pop('uris')
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(invalid_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        data = response.data
        self.assertEqual(data['detail'], "'uris' is a required property")
        self.assertEqual(response.status_code, 400)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi4.yaml')
    def test_missing_description_is_ok(self):
        Provider.objects.create(user=self.user, shortname='devooonnnn')
        view = DataList.as_view()
        invalid_post = copy.deepcopy(VALID_POST)
        invalid_post['jsonData'].pop('description')
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(invalid_post),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, 201)
        Provider.objects.all().delete()

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi.yaml')
    def test_anonomous_user_can_view(self):
        view = DataList.as_view()
        request = self.factory.get('/pushed_data/')
        request.user = AnonymousUser()
        response = view(request)

        self.assertEqual(response.status_code, 200)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi.yaml')
    def test_anonomous_user_can_not_post(self):
        view = DataList.as_view()
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(VALID_POST),
            content_type='application/json'
        )
        request.user = AnonymousUser()
        response = view(request)
        data = response.data

        self.assertEqual(data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(response.status_code, 401)

    @vcr.use_cassette('provider_registration/test_utils/vcr_cassettes/doi2.yaml')
    def test_source_is_same_as_shortname(self):
        Provider.objects.create(user=self.user, shortname='devooonnnn')
        view = DataList.as_view()
        request = self.factory.post(
            '/pushed_data/',
            json.dumps(VALID_POST),
            content_type='application/json'
        )
        request.user = self.user
        response = view(request)
        data = response.data

        self.assertEqual(data['source'], 'devooonnnn')

        Provider.objects.all().delete()

    def test_render_index(self):
        view = main_index
        request = self.factory.get(
            '/index'
        )
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_render_provider_form_gather(self):
        view = provider_information
        request = self.factory.get(
            '/information/'
        )
        request.user = self.user

        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_does_not_render_information(self):
        view = render_settings
        request = self.factory.get(
            '/information/'
        )
        request.user = self.user
        self.assertRaises(Provider.DoesNotExist, view, request)

    def test_render_information(self):
        view = render_settings
        request = self.factory.get(
            '/information/'
        )
        request.user = self.user
        Provider.objects.create(user=self.user)

        response = view(request)
        self.assertEqual(response.status_code, 200)

    def test_render_provider_form(self):
        view = provider_information
        favicon_image = open('shareregistration/static/img/share.png')
        request = self.factory.post(
            '/provider_information/', {
                'longname': 'Dudley Boyz Strike Back',
                'shortname': 'dbsb',
                'url': 'http://url.com',
                'favicon_image': favicon_image
            }
        )
        mock.MagicMock(spec=request.FILES)
        request.user = self.user
        response = view(request)
        self.assertEqual(response.status_code, 302)
