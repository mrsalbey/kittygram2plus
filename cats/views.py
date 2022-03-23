from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle

from .models import Achievement, Cat, User
from .pagination import CatsPagination
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .throttling import WorkingHoursRateThrottle


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = (OwnerOrReadOnly,)
    #throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    ##throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)
    # А далее применится лимит low_request
    ##throttle_scope = 'low_request'
    # Даже если на уровне проекта установлен PageNumberPagination
    # Для котиков будет работать LimitOffsetPagination
    ##pagination_class = LimitOffsetPagination
    # Вот он наш собственный класс пагинации с page_size=20
    #pagination_class = CatsPagination
    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # Временно отключим пагинацию на уровне вьюсета, 
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    search_fields = ('name',)
    ordering_fields = ('name', 'birth_year')
    ordering = ('birth_year',)  
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернем обновленный перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
