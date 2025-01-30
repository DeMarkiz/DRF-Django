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

    def get_lessons_count(self, course):
        return course.lessons.count()

    class Meta:
        model = Course
        fields = "__all__"


class CourseSubscriptionSerializer(ModelSerializer):

    class Meta:
        model = CourseSubscription
        fields = '__all__'
        validators = [
            serializers.UniqueTogetherValidator(
                fields=['user', 'course'], queryset=CourseSubscription.objects.all()
            )
        ]
        read_only_fields = ('user',)
