from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from recipes.models import (Favorites, Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import Subscriptions


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    is_subscribed = serializers.SerializerMethodField(default=False)
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request and (
            request.user.is_authenticated and Subscriptions.objects.filter(
                user=request.user.id,
                author=obj
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return request and (
            request.user.is_authenticated and obj.favorites.filter(
                user=request.user.id, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return request and (
            request.user.is_authenticated and obj.shopping_cart.filter(
                user=request.user.id, recipe=obj
            ).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Нужен хотя бы один ингредиент.'
            )
        unique_ing = {ing['id'] for ing in ingredients}
        if len(ingredients) != len(unique_ing):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться'
            )
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        unique_tags = set(tags)
        if len(tags) != len(unique_tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        serializer = RecipeReadSerializer(instance, context=context)
        return serializer.data

    def create_ingredient(self, recipe, ingredients):
        return RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ing['id'],
                amount=ing['amount']
            )
            for ing in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.create_ingredient(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.create_ingredient(instance, ingredients)
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class ShortRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов краткий."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для подписки."""
    class Meta:
        model = Subscriptions
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=fields,
                message='Вы уже подписаны на этого автора.'
            )
        ]

    def validate(self, data):
        user = data.get('user').id
        author = data.get('author').id
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        return data


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = obj.recipes.all()[:recipes_limit]
            except ValueError:
                pass
        else:
            recipes = obj.recipes.all()
        return ShortRecipesSerializer(
            recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в избранном."""

    class Meta:
        model = Favorites
        fields = ('recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=fields,
                message='Вы уже добавили этот рецепт.'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в корзине."""

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=fields,
                message='Вы уже добавили этот рецепт.'
            )
        ]
