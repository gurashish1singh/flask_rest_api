from __future__ import annotations

from http import HTTPStatus

from flask import Flask
from flask_testing import TestCase
from parameterized import parameterized

from flask_rest_api import create_app

BASE_URL = "https://127.0.0.1:"
DUMMY_DATA = (
    {"likes": 10, "name": "Bob", "views": 1_000},
    {"likes": 25, "name": "Bob", "views": 1_234},
    {"likes": 43, "name": "Bob", "views": 876},
)


class TestApp(TestCase):
    def create_app(self) -> Flask:
        app = create_app()
        return app

    def setUp(self):
        for video_id, data in enumerate(DUMMY_DATA):
            self.client.put(
                f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=data
            )

    @parameterized.expand(
        [
            (
                4,
                {"likes": 13, "name": "Bob", "views": 345},
            ),
            (
                5,
                {"likes": 12, "name": "Bob", "views": 389},
            ),
        ]
    )
    def test_app_put_success(self, video_id, input_dict):
        resp = self.client.put(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertDictEqual(resp.json, input_dict)
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

    def test_app_put_item_already_exists(self):
        video_id = 1
        data = {"likes": 10, "name": "Bob", "views": 1_000}

        resp = self.client.put(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=data
        )
        self.assertEqual(resp.status_code, HTTPStatus.CONFLICT)
        self.assertEqual(resp.json, {"message": f"Video with {video_id = } already exists."})

    @parameterized.expand(
        [
            (
                1,
                {"name": "Bob", "views": 345},
                ["likes"],
            ),
            (
                2,
                {"likes": 12, "views": 389},
                ["name"],
            ),
            (
                3,
                {"name": "Bob"},
                ["likes", "views"],
            ),
            (
                4,
                {"name": "Bob", "view": 234, "like": 10},
                ["likes", "views"],
            ),
            # type conversion takes place when the reqparse.RequestParser.add_argument is called
            (
                5,
                {"likes": "12a", "name": "Bob", "views": 389},
                ["likes"],
            ),
        ]
    )
    def test_app_put_field_error(self, video_id, input_dict, missing_fields):
        resp = self.client.put(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertListEqual([*resp.json["message"].keys()], missing_fields)

    @parameterized.expand(
        [
            (2,),
            (1,),
            (0,),
        ]
    )
    def test_app_get_success(self, video_id):
        resp = self.client.get(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}",
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertDictEqual(resp.json, DUMMY_DATA[video_id])

    def test_app_get_failure(self):
        resp = self.client.get(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/99",
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    @parameterized.expand(
        [
            (
                6,
                {"likes": 13, "name": "Bob", "views": 345},
            ),
            (
                7,
                {"likes": 12, "name": "Bob", "views": 389},
            ),
        ]
    )
    def test_app_delete_sucess(self, video_id, input_dict):
        resp = self.client.put(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        # Delete and assert
        delete_resp = self.client.delete(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}"
        )
        self.assertEqual(delete_resp.status_code, HTTPStatus.NO_CONTENT)

    def test_app_delete_failure(self):
        resp = self.client.delete(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/99",
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(resp.json, {"message": "Video with video_id = 99 does not exist."})
