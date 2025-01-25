from .models import Course, Lesson, CourseSubscription
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework import serializers
from lms.validators import validate_url


class LessonSerializer(ModelSerializer):
    url = serializers.URLField(validators=[validate_url])

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True)
    is_subscribed = SerializerMethodField()

    def get_lessons_count(self, course):
        return course.lessons.count()

    def get_is_subscribed(self, instance):
        return instance.subscriptions.filter(user=self.context['request'].user).exists()

    class Meta:
        model = Course
        fields = "__all__"


class CourseSubscriptionSerializer(ModelSerializer):

    class Meta:
        model = CourseSubscription
        fields = ["course"]
        read_only_fields = ('user',)
        read_only_fields = ('user',)
