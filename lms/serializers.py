from .models import Course, Lesson
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers


class LessonSerializer(ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True)

    def get_lessons_count(self, course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = '__all__'
