from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile, Team, Player


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'city', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'city', 'players_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'country']
    search_fields = ['name', 'city', 'state', 'manager__username', 'manager__first_name', 'manager__last_name']
    readonly_fields = ['created_at', 'updated_at', 'players_count']
    
    def players_count(self, obj):
        return obj.players.filter(is_active=True).count()
    players_count.short_description = 'Jugadores'


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'team', 'position', 'jersey_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'position', 'team', 'created_at']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name', 
        'user__email', 'team__name', 'jersey_number'
    ]
    readonly_fields = ['created_at', 'updated_at']
