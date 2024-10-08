from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views as djoser_views
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.converters_shopping_cart import pdf_shopping_cart
from api.paginations import RecipePagination
from api.permissions import AuthorPermission
from api.serializers import (
    AvatarSerializer,
    FavoritesSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShortRecipesSerializer,
    SubscribeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserSerializer
)
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from users.models import Subscriptions


User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    """Представления для пользователей."""
    serializer_class = UserSerializer
    pagination_class = RecipePagination

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(
        methods=['put'],
        url_path='me/avatar',
        serializer_class=AvatarSerializer,
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def avatar(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        url_path=r'(?P<pk>\d+)/subscribe',
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)
        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'author': author.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = SubscriptionsSerializer(
            author,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)
        subscription = Subscriptions.objects.filter(
            user=request.user,
            author=author
        )
        if not subscription.delete()[0]:
            return Response(
                {'detail': 'Вы не были подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'detail': 'Подписка отменена.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscriptionsSerializer
    )
    def subscriptions(self, request):
        queryset = self.paginate_queryset(
            User.objects.filter(subscriptions__user=self.request.user)
        )
        serializer = SubscriptionsSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представления для рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorPermission,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = RecipePagination

    def create_obj(self, create_serializer, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = create_serializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = ShortRecipesSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if not obj.delete()[0]:
            return Response(
                {'detail': 'Вы не добавляли этот рецепт!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'detail': 'Рецепт удален.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        url_path=r'(?P<pk>\d+)/favorite',
        serializer_class=FavoritesSerializer,
        detail=False,
    )
    def favorite(self, request, pk=None):
        return self.create_obj(self.serializer_class, request, pk)

    @favorite.mapping.delete
    def del_favorite(self, request, pk=None):
        return self.delete_obj(Favorites, request, pk)

    @action(
        methods=['post'],
        url_path=r'(?P<pk>\d+)/shopping_cart',
        serializer_class=ShoppingCartSerializer,
        detail=False,
    )
    def shopping_cart(self, request, pk=None):
        return self.create_obj(self.serializer_class, request, pk)

    @shopping_cart.mapping.delete
    def del_shopping_cart(self, request, pk=None):
        return self.delete_obj(ShoppingCart, request, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shopping_cart = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return pdf_shopping_cart(shopping_cart)

    @action(
        detail=True,
        url_path='get-link',
        permission_classes=(AllowAny,)
    )
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        short_link = request.build_absolute_uri(
            reverse('recipes:short_link', args=[recipe.pk])
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """Представления для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представления для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
