from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class UserRecipeBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               verbose_name='Рецепт')

    class Meta:
        abstract = True 
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe')
        ]

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name}'
