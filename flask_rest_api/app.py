from __future__ import annotations

from http import HTTPStatus

from flask import (
    abort,
    current_app,
)
from flask_restful import (
    Resource,
    fields,
    marshal_with,
    reqparse,
)
from sqlalchemy import delete

from flask_rest_api.models import VideoModel

video_post_args = reqparse.RequestParser(bundle_errors=True)
video_post_args.add_argument("name", type=str, help="Name of the video", required=True)
video_post_args.add_argument("likes", type=int, help="Likes on the video", required=True)
video_post_args.add_argument("views", type=int, help="Views of the video", required=True)

video_put_args = reqparse.RequestParser(bundle_errors=True)
# store_missing removes the null key: value pair from the video_put_args object
video_put_args.add_argument("name", type=str, help="Name of the video", store_missing=False)
video_put_args.add_argument("likes", type=int, help="Likes on the video", store_missing=False)
video_put_args.add_argument("views", type=int, help="Views of the video", store_missing=False)

resource_field = {
    "id": fields.Integer,
    "name": fields.String,
    "likes": fields.Integer,
    "views": fields.Integer,
}


class Video(Resource):
    @marshal_with(resource_field)
    def get(self, video_id: int) -> tuple[VideoModel, int]:
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(HTTPStatus.NOT_FOUND, f"Item with {video_id = } does not exist.")
        return result, HTTPStatus.OK

    @marshal_with(resource_field)
    def post(self, video_id: int) -> tuple[VideoModel, int]:
        args = video_post_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(HTTPStatus.CONFLICT, f"Item with {video_id = } is taken.")

        video = VideoModel(id=video_id, **args)
        with current_app.app_context():
            current_app.db.session.add(video)
            current_app.db.session.commit()
        return video, HTTPStatus.CREATED

    @marshal_with(resource_field)
    def put(self, video_id: int) -> tuple[VideoModel, int]:
        args = video_put_args.parse_args()
        if not args:
            abort(HTTPStatus.NOT_ACCEPTABLE, f"Item with {video_id = } has not been modified.")
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(HTTPStatus.NOT_FOUND, f"Item with {video_id = } does not exist.")

        for arg, value in args.items():
            setattr(result, arg, value)
        with current_app.app_context():
            current_app.db.session.add(result)
            current_app.db.session.commit()
        return result, HTTPStatus.OK

    def delete(self, video_id: int) -> tuple[VideoModel, int]:
        result = VideoModel.query.filter_by(id=video_id)
        if not result.first():
            abort(HTTPStatus.NOT_FOUND, f"Item with {video_id = } does not exist.")

        with current_app.app_context():
            d = delete(VideoModel).where(VideoModel.id == video_id)
            current_app.db.session.execute(d)
            current_app.db.session.commit()
        return "", HTTPStatus.NO_CONTENT
