from __future__ import annotations

from http import HTTPStatus

from flask import abort
from flask_restful import (
    Resource,
    reqparse,
)

VIDEOS = {}

video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video", required=True)
video_put_args.add_argument("likes", type=int, help="Likes on the video", required=True)
video_put_args.add_argument("views", type=int, help="Views of the video", required=True)


class Video(Resource):
    def get(self, video_id: int) -> str:
        try:
            return VIDEOS[video_id]
        except KeyError:
            return abort(HTTPStatus.NOT_FOUND, f"{video_id = } is not valid")

    def put(self, video_id: int) -> None:
        args = video_put_args.parse_args()
        VIDEOS[video_id] = args
        return VIDEOS[video_id], HTTPStatus.CREATED
