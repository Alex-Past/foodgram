import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from recipes.models import (Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import MAX_LEN_NAME, Subscriptions
from users.validators import username_validator


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Класс поля для изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    username = serializers.CharField(required=True,
                                     validators=[username_validator],
                                     max_length=MAX_LEN_NAME)
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
        return Subscriptions.objects.filter(
            user=self.context['request'].user.id, author=obj
        ).exists()


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара."""
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


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
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

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
        return obj.favorites.filter(
            user=self.context['request'].user.id, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return obj.shopping_cart.filter(
            user=self.context['request'].user.id, recipe=obj
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Минимальное время 1 мин.')
        return cooking_time

    def validate(self, data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError('Отсутствуют игредиенты!')
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        unique_ing = set()
        for ing in ingredients:
            if not Ingredient.objects.filter(id=ing['id']).exists():
                raise serializers.ValidationError(
                    'Указан несуществующий ингредиент.')
            if ing['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.')
            unique_ing.add(ing['id'])
        if len(ingredients) != len(unique_ing):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться')
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError('Отсутствуют теги!')
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        unique_tags = set()
        for tag in tags:
            unique_tags.add(tag)
        if len(tags) != len(unique_tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться.')
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        serializer = RecipeReadSerializer(instance, context=context)
        return serializer.data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ing in ingredients:
            ingredient = get_object_or_404(Ingredient, id=ing['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ing['amount']
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            for ing in ingredients:
                ingredient = get_object_or_404(Ingredient, id=ing['id'])
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ing['amount']
                )
        if 'tags' in validated_data:
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

    def validate(self, data):
        user = data.get('user').id
        author = data.get('author').id
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        if Subscriptions.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого автора.'
            )
        return data

    def create(self, validated_data):
        user = validated_data.get('user')
        author = validated_data.get('author')
        return Subscriptions.objects.create(user=user, author=author)


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


class ShoppingCartRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов в корзине."""
    recipe = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Recipe.objects.all()
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        serializer = ShortRecipesSerializer(instance, context=context)
        return serializer.data
