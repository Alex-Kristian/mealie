<template>
  <div>
    <v-form ref="domForm" @submit.prevent="generateRecipe(prompt)">
      <div>
        <v-card-title class="headline">
          {{ $t("recipe.generate-recipe") }}
        </v-card-title>

        <v-card-text>
          <p>{{ $t("recipe.generate-recipe-description") }}</p>

          <v-textarea
            v-model="prompt"
            :label="$t('recipe.ai-recipe-prompt')"
            :prepend-inner-icon="$globals.icons.robot"
            validate-on="blur"
            autofocus
            variant="solo-filled"
            auto-grow
            clearable
            class="rounded-lg mt-2"
            rounded
            :rules="[validators.required]"
            persistent-hint
          />
        </v-card-text>

        <v-card-actions class="justify-center">
          <div style="width: 250px">
            <BaseButton
              rounded
              block
              type="submit"
              :loading="loading"
              :disabled="!prompt"
            >
              {{ $t("recipe.generate-recipe-button") }}
            </BaseButton>
          </div>
        </v-card-actions>
      </div>
    </v-form>

    <!-- Error box -->
    <v-expand-transition>
      <v-alert v-if="error" color="error" class="mt-6 white--text">
        <v-card-title class="ma-0 pa-0">
          <v-icon start color="white" size="x-large">
            {{ $globals.icons.robot }}
          </v-icon>
          {{ $t("recipe.generate-recipe-error-title") }}
        </v-card-title>

        <v-divider class="my-3 mx-2" />

        <p>{{ $t("recipe.generate-recipe-error-details") }}</p>
      </v-alert>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import { validators } from "~/composables/use-validators";
import { useNewRecipeOptions } from "~/composables/use-new-recipe-options";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      key: route => route.path,
    });

    const state = reactive({
      error: false,
      loading: false,
    });

    interface FormValidation {
      validate: () => boolean | Promise<boolean>;
    }

    const api = useUserApi();
    const route = useRoute();
    const $auth = useMealieAuth();

    const groupSlug = computed(
      () => route.params.groupSlug || $auth.user.value?.groupSlug || "",
    );

    const { stayInEditMode, navigateToRecipe } = useNewRecipeOptions();

    const prompt = ref("");
    const domForm = ref<FormValidation | null>(null);

    async function generateRecipe(promptText: string) {
      if (!promptText) {
        return;
      }

      if (!domForm.value?.validate()) {
        return;
      }

      state.loading = true;
      state.error = false;

      const { data, error } = await api.ai.generateRecipe(promptText);

      if (error || !data) {
        state.error = true;
        state.loading = false;
        return;
      }

      const recipe = data;

      const slug = recipe.slug ?? "";
      const group = typeof groupSlug.value === "string" ? groupSlug.value : "";
      if (!slug) {
        console.error("AI recipe generated without slug", recipe);
        state.error = true;
        return;
      }
      navigateToRecipe(
        slug,
        group,
        `/g/${groupSlug.value}/r/create/generate`,
      );
    }

    return {
      prompt,
      domForm,
      groupSlug,
      ...toRefs(state),
      stayInEditMode,
      generateRecipe,
      validators,
    };
  },
});
</script>
