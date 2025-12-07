import { BaseAPI } from "../base/base-clients";

const prefix = "/api/recipes/ai";

const routes = {
    generateNutrition: (recipeId: string) =>
        `${prefix}/generate-nutrition/${recipeId}`,
};

export class AiApi extends BaseAPI {
    async generateNutrition(recipeId: string) {
        return await this.requests.post(routes.generateNutrition(recipeId), {});
    }
}
