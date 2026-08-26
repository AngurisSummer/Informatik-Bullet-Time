from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask("VideoAPI")
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("title", required=True, location="form")

videos = {
     #dictionary of videos
    "video1": {"title": "Hello World in Python"},
    "video2": {"title": "Hello World in Python"}
}

#creating class for individual video
class Video(Resource): #class video will extend from a resource (part of flask-restful already)
    #we define the methods for get, post, put and delete in this class
    def get(self, video_id): #parameter video_id
        if video_id == "all":
            return videos
        return videos[video_id], 201

    def post(self, video_id):
        args = parser.parse_args()
        new_video = {"title": args["title"]}
        videos[video_id] = new_video
        return {video_id: videos[video_id]}, 201

    def put(self, video_id):
        args = parser.parse_args()
        new_video = {"title": args["title"]}
        videos[video_id] = new_video
        return {video_id: videos[video_id]}, 201

#to make the resource accessible, we have to add this resource to the application we are making
api.add_resource(Video, "/videos/<video_id>") #adding the video as a resource, "/" is the default path of localhost

if __name__ == "__main__":
    app.run()