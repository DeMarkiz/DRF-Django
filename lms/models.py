from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название курса', help_text='Укажите название курса')
    preview = models.ImageField(upload_to='lms/img', blank=True, null=True, verbose_name='Превью', help_text='Загрузите изображение')
    description = models.TextField(max_length=250, blank=True, null=True, verbose_name='Описание курса', help_text='Укажите описание курса')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title



class Lesson(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name="название урока",
        help_text="укажите название урока",
    )
    description = models.TextField(
        max_length=250,
        verbose_name="описание урока",
        help_text="опишите урок",
        blank=True,
        null=True,
    )
    picture = models.ImageField(
        upload_to="lms/pictures",
        verbose_name="картинка",
        blank=True,
        null=True,
        help_text="Загрузите картинку",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="курс",
        help_text="выберите курс",
        related_name="lesson_set",
    )
    video_url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="ссылка на видео",
        help_text="загрузите видео",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.title