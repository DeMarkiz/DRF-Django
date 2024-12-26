from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["title"]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True)

    def get_lessons_count(self, course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = (
            "name",
            "description",
            "preview",
            "count_of_lessons",
            "info_lessons",
        )
