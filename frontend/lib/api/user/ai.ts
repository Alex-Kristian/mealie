import { BaseAPI } from "../base/base-clients";
import type { Recipe } from "~/lib/api/types/recipe";

const prefix = "/api/recipes/ai";

const routes = {
    generateNutrition: (recipeId: string) =>
        `${prefix}/generate-nutrition/${recipeId}`,
    generateRecipe: () =>
        `${prefix}/generate-recipe`,
};

export class AiApi extends BaseAPI {
    async generateNutrition(recipeId: string) {
        return await this.requests.post(routes.generateNutrition(recipeId), {});
    }

    async generateRecipe(userPrompt: string) {
        return await this.requests.post<Recipe>(routes.generateRecipe(), { userPrompt: userPrompt });
    }
}
