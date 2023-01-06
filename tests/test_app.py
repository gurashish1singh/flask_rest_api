from __future__ import annotations

import os
from copy import deepcopy
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
        os.environ["ENV"] = "testing"
        app = create_app()
        return app

    def setUp(self):
        for video_id, data in enumerate(DUMMY_DATA):
            self.client.post(
                f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=data
            )

    def tearDown(self):
        db_path = self.app.config["DB_PATH"]
        os.remove(db_path)

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
    def test_app_post_success(self, video_id, input_dict):
        resp = self.client.post(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertDictEqual(resp.json, {"id": video_id, **input_dict})
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

    def test_app_post_item_already_exists(self):
        video_id = 1
        data = {"likes": 10, "name": "Bob", "views": 1_000}

        resp = self.client.post(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=data
        )
        self.assertEqual(resp.status_code, HTTPStatus.CONFLICT)
        self.assertEqual(resp.json, {"message": f"Item with {video_id = } is taken."})

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
    def test_app_post_field_error(self, video_id, input_dict, missing_fields):
        resp = self.client.post(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertListEqual([*resp.json["message"].keys()], missing_fields)

    @parameterized.expand(
        [
            (
                1,
                {"likes": 13},
            ),
            (
                2,
                {"name": "Yob", "views": 389},
            ),
            (
                0,
                {"likes": 34, "name": "Rob", "views": 345},
            ),
        ]
    )
    def test_app_put_success(self, video_id, input_dict):
        resp = self.client.put(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        expected_resp = deepcopy(resp.json)
        expected_resp.update(input_dict)
        self.assertDictEqual(resp.json, expected_resp)
        self.assertEqual(resp.status_code, HTTPStatus.OK)

    @parameterized.expand(
        [
            (
                5,
                {"likes": 10, "name": "Bob", "views": 1_000},
                HTTPStatus.NOT_FOUND,
                "Item with video_id = 5 does not exist.",
            ),
            (
                1,
                {},
                HTTPStatus.NOT_ACCEPTABLE,
                "Item with video_id = 1 has not been modified.",
            ),
        ]
    )
    def test_app_put_failure(self, video_id, input_dict, error_code, error_msg):
        resp = self.client.put(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertEqual(resp.status_code, error_code)
        self.assertEqual(resp.json, {"message": error_msg})

    @parameterized.expand([(2,), (1,), (0,)])
    def test_app_get_success(self, video_id):
        resp = self.client.get(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}",
        )
        self.assertEqual(resp.status_code, HTTPStatus.OK)
        self.assertDictEqual(resp.json, {"id": video_id, **DUMMY_DATA[video_id]})

    def test_app_get_failure(self):
        resp = self.client.get(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/99",
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)

    @parameterized.expand(
        [
            (
                6,
                {"likes": 11, "name": "Rob", "views": 345},
            ),
            (
                7,
                {"likes": 12, "name": "Bob", "views": 389},
            ),
        ]
    )
    def test_app_delete_sucess(self, video_id, input_dict):
        resp = self.client.post(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}", data=input_dict
        )
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        # Delete and assert
        delete_resp = self.client.delete(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}"
        )
        self.assertEqual(delete_resp.status_code, HTTPStatus.NO_CONTENT)
        get_resp = self.client.get(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/{video_id}"
        )
        self.assertEqual(get_resp.json, {"message": f"Item with {video_id = } does not exist."})

    def test_app_delete_failure(self):
        resp = self.client.delete(
            f"{BASE_URL}{self.app.config['FLASK_RUN_PORT']}/video/99",
        )
        self.assertEqual(resp.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(resp.json, {"message": "Item with video_id = 99 does not exist."})
