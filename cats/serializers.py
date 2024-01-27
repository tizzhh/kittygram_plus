import datetime as dt

import webcolors
from rest_framework import serializers

from .models import CHOICES, Achievement, AchievementCat, Cat, Owner


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')

        return data


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatListSerializer(serializers.ModelSerializer):
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
    # color = Hex2NameColor()
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = (
            'id',
            'name',
            'color',
            'birth_year',
            'owner',
            'achievements',
            'age',
        )

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat

        achievements = validated_data.pop('achievements')
        cat = Cat.objects.create(**validated_data)

        for ach in achievements:
            cur_ach, status = Achievement.objects.get_or_create(**ach)
            AchievementCat.objects.create(achievement=cur_ach, cat=cat)
        return cat


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')
