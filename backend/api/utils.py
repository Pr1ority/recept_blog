from datetime import datetime


def render_shopping_list(ingredients, recipes):
    report_date = datetime.now().strftime('%d-%m-%Y')
    report_header = f"Список покупок составлен: {report_date}"

    product_header = "Список продуктов:"
    product_list = [
        f'{index}.'
        f' {ingredient["ingredient__name"].capitalize()}'
        f'— {ingredient["total_amount"]}'
        f' {ingredient["ingredient__measurement_unit"]}'
        for index, ingredient in enumerate(ingredients, 1)
    ]

    recipe_header = 'Рецепты, для которых составлен список покупок:'
    recipe_list = [f'{idx + 1}. {recipe.name}' for idx, recipe in enumerate(
        recipes)]

    return '\n'.join(
        [report_header,
         product_header] + product_list + [recipe_header] + recipe_list
    )
