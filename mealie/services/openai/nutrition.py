import json

from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.services.openai import OpenAIDataInjection, OpenAIService
from mealie.services.recipe.recipe_service import RecipeService

from .._base_service import BaseService


class NutritionAIService(BaseService):
    async def generate_and_update(self, recipe_id: str, recipe_service: RecipeService):
        """
        Main entrypoint — only requires recipe_id.
        Loads ingredients, calls OpenAI, writes nutrition back to DB.
        """
        recipe = recipe_service.get_one(recipe_id)
        if not recipe:
            raise Exception("Recipe not found")

        ingredients = self._extract_ingredients(recipe)

        nutrition_json = await self._generate_nutrition_json(ingredients)

        return await self._apply_nutrition_update(
            recipe_service=recipe_service,
            recipe=recipe,
            nutrition_json=nutrition_json,
        )

    def _extract_ingredients(self, recipe):
        """Extract recipe ingredients from Recipe object for AI prompting."""
        result = []
        for ing in recipe.recipe_ingredient or []:
            text = ing.note or ing.food or ""
            if text:
                result.append(text)
        return result

    async def _generate_nutrition_json(self, ingredients: list[str]):
        """Handles prompt and OpenAI call."""

        openai_service = OpenAIService()

        ingredient_text = "\n".join(ingredients)

        prompt = self._get_prompt(
            service=openai_service,
            ingredients=ingredients,
        )

        try:
            response = await openai_service.get_response(
                prompt=prompt,
                message=ingredient_text,
                force_json_response=True,
            )
            return response
        except Exception as e:
            raise Exception("Failed to call OpenAI services") from e

    def _get_prompt(self, service: OpenAIService, ingredients: list[str]):
        """Constructs the nutrition prompt."""

        data_injections = [
            OpenAIDataInjection(
                description=(
                    "This is the JSON response schema. You must respond in valid JSON that follows this schema. "
                    "Your payload should be as compact as possible, eliminating unncessesary whitespace. Any fields "
                    "with default values which you do not populate should not be in the payload."
                ),
                value=ingredients,
            ),
        ]

        return service.get_prompt(
            "recipes.generate-nutrition",
            data_injections=data_injections,
        )

    async def _apply_nutrition_update(self, recipe_service, recipe, nutrition_json):
        """Write Nutrition model to recipe and save to DB."""
        if isinstance(nutrition_json, str):
            nutrition_json = json.loads(nutrition_json)

        nutrition_model = Nutrition(**nutrition_json)

        recipe.nutrition = nutrition_model

        updated_recipe = recipe_service.update_one(recipe.id, recipe)
        return updated_recipe
