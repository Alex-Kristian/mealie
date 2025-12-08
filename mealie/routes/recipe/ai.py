from pydantic import BaseModel

from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.services.openai.nutrition import NutritionAIService
from mealie.services.recipe.recipe_service import RecipeService

router = UserAPIRouter(prefix="/ai")


class GenerateRecipeRequest(BaseModel):
    userPrompt: str


@controller(router)
class RecipeAiController(BaseUserController):
    @router.post("/generate-nutrition/{recipe_id}", response_model=Nutrition)
    async def generate_and_update_nutrition(self, recipe_id: str) -> Nutrition:
        recipe_service = RecipeService(
            repos=self.repos, user=self.user, household=self.household, translator=self.translator
        )
        nutrition_service = NutritionAIService()

        updated_recipe = await nutrition_service.generate_and_update(
            recipe_id=recipe_id,
            recipe_service=recipe_service,
        )

        return updated_recipe.nutrition

    @router.post("/generate-recipe", response_model=Recipe)
    async def generate_recipe_from_text(self, request: GenerateRecipeRequest) -> Recipe:
        recipe_service = RecipeService(
            repos=self.repos, user=self.user, household=self.household, translator=self.translator
        )
        return await recipe_service.create_from_text(user_prompt=request.userPrompt)
